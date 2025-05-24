from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from decimal import Decimal
from django.conf import settings
import requests
import json
import hmac
import hashlib
from datetime import datetime

class PaymentProvider(ABC):
    @abstractmethod
    def create_payment(self, amount: Decimal, currency: str, description: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def check_payment_status(self, payment_id: str) -> str:
        pass

    @abstractmethod
    def process_refund(self, payment_id: str, amount: Decimal, reason: str) -> bool:
        pass

    @abstractmethod
    def verify_webhook(self, payload: Dict[str, Any], signature: str) -> bool:
        pass

class PaymeProvider(PaymentProvider):
    def __init__(self):
        self.merchant_id = settings.PAYME_MERCHANT_ID
        self.secret_key = settings.PAYME_SECRET_KEY
        self.api_url = settings.PAYME_API_URL

    def create_payment(self, amount: Decimal, currency: str, description: str) -> Dict[str, Any]:
        payload = {
            "method": "receipts.create",
            "params": {
                "amount": int(amount * 100),  # Convert to tiyin
                "currency": currency,
                "description": description,
                "merchant_id": self.merchant_id
            }
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()  # HTTP xatolarini ushlaydi
            data = response.json()
            if data.get('result', {}).get('receipt', {}).get('_id'):
                return {
                    'provider_id': data['result']['receipt']['_id'],
                    'checkout_url': data['result']['receipt']['url'],
                    'provider_data': data
                }
            raise Exception("Payme payment creation failed: Invalid response structure")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Payme API request failed: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("Payme API returned invalid JSON")

    def check_payment_status(self, payment_id: str) -> str:
        payload = {
            "method": "receipts.get",
            "params": {
                "id": payment_id,
                "merchant_id": self.merchant_id
            }
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            data = response.json()
            status = data.get('result', {}).get('receipt', {}).get('status')
            if status:
                return self._map_status(status)
            return 'failed'
        except requests.exceptions.RequestException as e:
            raise Exception(f"Payme status check failed: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("Payme API returned invalid JSON")

    def process_refund(self, payment_id: str, amount: Decimal, reason: str) -> bool:
        payload = {
            "method": "receipts.cancel",
            "params": {
                "id": payment_id,
                "merchant_id": self.merchant_id,
                "amount": int(amount * 100),  # Convert to tiyin
                "reason": reason
            }
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            raise Exception(f"Payme refund failed: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("Payme API returned invalid JSON")

    def verify_webhook(self, payload: Dict[str, Any], signature: str) -> bool:
        if not signature:
            return False
        
        # Verify signature
        data = json.dumps(payload, separators=(',', ':'))
        expected_signature = hmac.new(
            self.secret_key.encode(),
            data.encode(),
            hashlib.sha1
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)

    def _get_headers(self) -> Dict[str, str]:
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {self.secret_key}'
        }

    def _map_status(self, payme_status: str) -> str:
        status_map = {
            'waiting': 'pending',
            'paid': 'completed',
            'cancelled': 'cancelled',
            'failed': 'failed'
        }
        return status_map.get(payme_status, 'failed')

class ClickProvider(PaymentProvider):
    def __init__(self):
        self.merchant_id = settings.CLICK_MERCHANT_ID
        self.service_id = settings.CLICK_SERVICE_ID
        self.secret_key = settings.CLICK_SECRET_KEY
        self.api_url = settings.CLICK_API_URL

    def create_payment(self, amount: Decimal, currency: str, description: str) -> Dict[str, Any]:
        payload = {
            "service_id": self.service_id,
            "amount": str(amount),
            "currency": currency,
            "description": description,
            "merchant_id": self.merchant_id,
            "timestamp": int(datetime.now().timestamp())
        }
        
        # Add signature
        payload['sign_string'] = self._generate_signature(payload)
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            data = response.json()
            if data.get('result', {}).get('invoice_id'):
                return {
                    'provider_id': data['result']['invoice_id'],
                    'checkout_url': data['result']['url'],
                    'provider_data': data
                }
            raise Exception("Click payment creation failed: Invalid response structure")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Click API request failed: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("Click API returned invalid JSON")

    def check_payment_status(self, payment_id: str) -> str:
        payload = {
            "service_id": self.service_id,
            "invoice_id": payment_id,
            "merchant_id": self.merchant_id,
            "timestamp": int(datetime.now().timestamp())
        }
        
        # Add signature
        payload['sign_string'] = self._generate_signature(payload)
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            data = response.json()
            status = data.get('result', {}).get('status')
            if status:
                return self._map_status(status)
            return 'failed'
        except requests.exceptions.RequestException as e:
            raise Exception(f"Click status check failed: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("Click API returned invalid JSON")

    def process_refund(self, payment_id: str, amount: Decimal, reason: str) -> bool:
        payload = {
            "service_id": self.service_id,
            "invoice_id": payment_id,
            "amount": str(amount),
            "reason": reason,
            "merchant_id": self.merchant_id,
            "timestamp": int(datetime.now().timestamp())
        }
        
        # Add signature
        payload['sign_string'] = self._generate_signature(payload)
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            raise Exception(f"Click refund failed: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("Click API returned invalid JSON")

    def verify_webhook(self, payload: Dict[str, Any], signature: str) -> bool:
        if not signature:
            return False
        
        # Verify signature
        expected_signature = self._generate_signature(payload)
        return hmac.compare_digest(signature, expected_signature)

    def _get_headers(self) -> Dict[str, str]:
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {self.secret_key}'
        }

    def _generate_signature(self, payload: Dict[str, Any]) -> str:
        # Remove sign_string if exists
        if 'sign_string' in payload:
            del payload['sign_string']
        
        # Sort keys
        sorted_payload = dict(sorted(payload.items()))
        
        # Create sign string
        sign_string = '&'.join(f"{k}={v}" for k, v in sorted_payload.items())
        
        # Add secret key
        sign_string += f"&{self.secret_key}"
        
        # Generate hash
        return hashlib.md5(sign_string.encode()).hexdigest()

    def _map_status(self, click_status: str) -> str:
        status_map = {
            'waiting': 'pending',
            'paid': 'completed',
            'cancelled': 'cancelled',
            'failed': 'failed'
        }
        return status_map.get(click_status, 'failed')

def get_provider(provider_name: str) -> Optional[PaymentProvider]:
    providers = {
        'payme': PaymeProvider,
        'click': ClickProvider
    }
    
    provider_class = providers.get(provider_name.lower())
    if provider_class:
        return provider_class()
    
    return None 