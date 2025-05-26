from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from .models import Payment, Course
from .serializers import PaymentSerializer, PaymentRefundSerializer
from .permissions import IsOwnerOrAdmin, IsCourseInstructorOrAdmin, IsPaymentProvider
from .providers import get_provider
from django.utils import timezone
import logging
from rest_framework.throttling import UserRateThrottle
from django.core.cache import cache
from django.core.exceptions import ValidationError
import requests
import json
from datetime import timedelta
from rest_framework import serializers

logger = logging.getLogger(__name__)

class PaymentRateThrottle(UserRateThrottle):
    rate = '10/minute'

class PaymentListView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [PaymentRateThrottle]

    def get(self, request):
        payments = Payment.objects.filter(user=request.user)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

    def post(self, request):
        try:
            serializer = PaymentSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            
            # Check if user has active payment for this course
            cache_key = f"payment_course_{serializer.validated_data['course'].id}_user_{request.user.id}"
            if cache.get(cache_key):
                return Response(
                    {"detail": "Sizda bu kurs uchun faol to'lov mavjud"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get payment provider
            provider = get_provider(serializer.validated_data['method'])
            if not provider:
                return Response(
                    {"detail": "Noto'g'ri to'lov usuli"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create payment in provider
            provider_data = provider.create_payment(
                amount=serializer.validated_data['amount'],
                currency='UZS',
                description=f"Course payment: {serializer.validated_data['course'].title}"
            )
            
            # Create payment in our system
            payment = serializer.save(
                user=request.user,
                payment_provider_id=provider_data['provider_id'],
                payment_provider_data=provider_data['provider_data']
            )
            
            # Set cache to prevent multiple payments
            cache.set(cache_key, True, timeout=3600)  # 1 hour
            
            return Response({
                **serializer.data,
                'checkout_url': provider_data['checkout_url']
            }, status=status.HTTP_201_CREATED)
            
        except serializers.ValidationError as e:
            logger.error(f"Payment validation error: {str(e)}")
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Payment creation failed: {str(e)}")
            return Response(
                {"detail": "To'lov yaratishda xatolik yuz berdi"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PaymentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Payment, pk=pk)

    def get(self, request, pk):
        payment = self.get_object(pk)
        if payment.user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "Bu to'lov ma'lumotlariga kirish huquqingiz yo'q"},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)

    def put(self, request, pk):
        payment = self.get_object(pk)
        if payment.user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "Bu to'lovni o'zgartirish huquqingiz yo'q"},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = PaymentSerializer(payment, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

class PaymentRefundView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Payment, pk=pk)

    def post(self, request, pk):
        payment = self.get_object(pk)
        if payment.user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "Bu to'lovni qaytarish huquqingiz yo'q"},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = PaymentRefundSerializer(data=request.data, context={'payment': payment})
        try:
            serializer.is_valid(raise_exception=True)
            provider = get_provider(payment.method)
            if not provider:
                return Response(
                    {'error': 'Payment provider not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            refund_success = provider.process_refund(
                payment.payment_provider_id,
                serializer.validated_data['amount'],
                serializer.validated_data['reason']
            )
            if refund_success:
                payment.status = 'refunded'
                payment.refund_date = timezone.now()
                payment.refund_amount = serializer.validated_data['amount']
                payment.refund_reason = serializer.validated_data['reason']
                payment.save()
                # Remove course enrollment
                if payment.course:
                    payment.course.enrolled_students.remove(payment.user)
                return Response(PaymentSerializer(payment).data)
            else:
                return Response(
                    {'error': 'Refund failed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except serializers.ValidationError as e:
            logger.error(f"Refund validation error: {str(e)}")
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Payment refund failed: {str(e)}")
            return Response(
                {'error': 'Payment refund failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PaymentCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Payment, pk=pk)

    def post(self, request, pk):
        payment = self.get_object(pk)
        if payment.user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "Bu to'lovni bekor qilish huquqingiz yo'q"},
                status=status.HTTP_403_FORBIDDEN
            )

        if payment.status != 'pending':
            return Response(
                {"detail": "Faqat kutilayotgan to'lovlarni bekor qilish mumkin"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            payment.status = 'cancelled'
            payment.save()
            
            # Clear cache
            cache_key = f"payment_course_{payment.course.id}_user_{payment.user.id}"
            cache.delete(cache_key)
            
            return Response(
                PaymentSerializer(payment).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error cancelling payment: {str(e)}")
            return Response(
                {"detail": "To'lovni bekor qilishda xatolik yuz berdi"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PaymentWebhookView(APIView):
    permission_classes = [IsPaymentProvider]

    def post(self, request, provider):
        try:
            provider_instance = get_provider(provider)
            if not provider_instance:
                return Response(
                    {"detail": "Noto'g'ri to'lov provayderi"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            signature = request.headers.get('X-Signature')
            if not provider_instance.verify_webhook(request.data, signature):
                return Response(
                    {"detail": "Noto'g'ri webhook imzosi"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            payment_id = request.data.get('payment_id')
            payment = get_object_or_404(Payment, payment_provider_id=payment_id)
            
            status_result = provider_instance.check_payment_status(payment_id)
            if status_result == 'completed':
                payment.status = 'completed'
                payment.payment_date = timezone.now()
                payment.save()
                
                # Add user to course enrolled students
                if payment.course:
                    payment.course.enrolled_students.add(payment.user)
                
                return Response({"status": "success"})
            
            return Response({"status": "pending"})
            
        except Exception as e:
            logger.error(f"Webhook processing failed: {str(e)}")
            return Response(
                {"detail": "Webhook qayta ishlashda xatolik yuz berdi"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )