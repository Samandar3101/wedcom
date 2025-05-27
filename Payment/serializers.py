from rest_framework import serializers
from .models import Payment
from CustomerUser.models import CustomerUser
from Course.models import Course
from django.utils import timezone
from decimal import Decimal

class PaymentSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=CustomerUser.objects.all(), required=False)
    user_email = serializers.CharField(source='user.email', read_only=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    course_title = serializers.CharField(source='course.title', read_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.ChoiceField(choices=Payment.PAYMENT_STATUS, read_only=True)
    method = serializers.ChoiceField(choices=Payment.PAYMENT_METHODS)
    transaction_id = serializers.CharField(max_length=100, read_only=True)
    payment_date = serializers.DateTimeField(read_only=True)
    payment_provider_id = serializers.CharField(max_length=100, required=False, allow_null=True)
    payment_provider_data = serializers.JSONField(required=False, default=dict)
    refund_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    refund_date = serializers.DateTimeField(required=False, allow_null=True)
    refund_reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        # On update, skip required field checks
        if self.instance:
            return data

        # Validate course exists and has a price
        course = data.get('course')
        if not course:
            raise serializers.ValidationError({"course": "Kurs tanlanishi shart"})
        
        if not hasattr(course, 'price') or not course.price:
            raise serializers.ValidationError({"course": "Kurs narxi to'g'ri ko'rsatilmagan"})

        # Validate payment method
        method = data.get('method')
        if not method:
            raise serializers.ValidationError({"method": "To'lov usuli kiritilishi shart"})
        
        if method not in dict(Payment.PAYMENT_METHODS):
            raise serializers.ValidationError({"method": f"'{method}' to'g'ri to'lov usuli emas"})

        # Validate amount
        amount = data.get('amount')
        if not amount:
            raise serializers.ValidationError({"amount": "To'lov summasi kiritilishi shart"})
        
        if amount <= Decimal('0'):
            raise serializers.ValidationError({"amount": "To'lov summasi 0 dan katta bo'lishi kerak"})
        
        if amount != course.price:
            raise serializers.ValidationError({"amount": "To'lov summasi kurs narxiga teng bo'lishi kerak"})

        # Validate cash payment limit
        if method == 'cash' and amount > Decimal('1000000'):
            raise serializers.ValidationError(
                {"method": "Naqd pul orqali to'lov 1 million so'mdan oshmasligi kerak"}
            )

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        course = validated_data['course']
        amount = validated_data['amount']
        method = validated_data['method']
        
        payment = Payment(
            user=user,
            course=course,
            amount=amount,
            status='pending',
            method=method,
            payment_provider_id=validated_data.get('payment_provider_id'),
            payment_provider_data=validated_data.get('payment_provider_data', {})
        )
        payment.save()
        return payment

    def update(self, instance, validated_data):
        # Only allow updating payment provider fields
        if 'payment_provider_id' in validated_data:
            instance.payment_provider_id = validated_data['payment_provider_id']
        if 'payment_provider_data' in validated_data:
            instance.payment_provider_data = validated_data['payment_provider_data']
        instance.save()
        return instance

class PaymentRefundSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    reason = serializers.CharField(required=True, allow_blank=True)

    def validate(self, data):
        payment = self.context['payment']

        # Avval allaqachon refund qilinganini tekshirish
        if payment.refund_amount:
            raise serializers.ValidationError(
                {"status": "Bu to'lov allaqachon qaytarilgan"}
            )

        # Faqat yakunlangan to'lovlarni refund qilish mumkin
        if payment.status != 'completed':
            raise serializers.ValidationError(
                {"status": "Faqat yakunlangan to'lovlarni qaytarish mumkin"}
            )

        # Validate refund time limit
        if payment.payment_date:
            days_since_payment = (timezone.now() - payment.payment_date).days
            if days_since_payment > 30:
                raise serializers.ValidationError(
                    {"time": "To'lovdan keyin 30 kundan o'tgan bo'lsa, qaytarish mumkin emas"}
                )

        # Validate amount
        amount = data.get('amount')
        if amount is None:
            amount = payment.amount
        if amount <= Decimal('0'):
            raise serializers.ValidationError(
                {"amount": "Qaytariladigan summa 0 dan katta bo'lishi kerak"}
            )
        if amount > payment.amount:
            raise serializers.ValidationError(
                {"amount": "Qaytariladigan summa to'lov summasidan ko'p bo'lishi mumkin emas"}
            )

        # Validate reason
        reason = data.get('reason', '').strip()
        if not reason:
            raise serializers.ValidationError(
                {"reason": "Qaytarish sababi kiritilishi shart"}
            )
        if len(reason) < 10:
            raise serializers.ValidationError(
                {"reason": "Qaytarish sababi kamida 10 ta belgidan iborat bo'lishi kerak"}
            )

        data['amount'] = amount
        return data