from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Payment, Course
from .serializers import PaymentSerializer, PaymentRefundSerializer
from .permissions import IsOwnerOrAdmin, IsCourseInstructorOrAdmin, IsPaymentProvider
from .filters import PaymentFilter
from .providers import get_provider
from django.utils import timezone
import logging
from rest_framework.throttling import UserRateThrottle
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
import requests
import json
from datetime import timedelta

logger = logging.getLogger(__name__)

class PaymentRateThrottle(UserRateThrottle):
    rate = '10/minute'  # 10 requests per minute

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PaymentFilter
    search_fields = ['transaction_id', 'user__email', 'course__title']
    ordering_fields = ['payment_date', 'amount', 'status']
    ordering = ['-payment_date']
    throttle_classes = [PaymentRateThrottle]

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create', 'me']:
            return [IsAuthenticated()]
        elif self.action in ['refund', 'cancel', 'confirm']:
            return [IsOwnerOrAdmin()]
        elif self.action in ['course_payments']:
            return [IsCourseInstructorOrAdmin()]
        elif self.action in ['webhook']:
            return [IsPaymentProvider()]
        return [IsAdminUser()]

    def get_payment_provider(self, method):
        return get_provider(method)

    def create(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Check if user has active payment for this course
            cache_key = f"payment_course_{serializer.validated_data['course'].id}_user_{request.user.id}"
            if cache.get(cache_key):
                return Response(
                    {"detail": "Sizda bu kurs uchun faol to'lov mavjud"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get payment provider
            provider = self.get_payment_provider(serializer.validated_data['method'])
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
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Payment creation failed: {str(e)}")
            return Response(
                {"detail": "To'lov yaratishda xatolik yuz berdi"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def me(self, request):
        try:
            payments = Payment.objects.filter(user=request.user)
            serializer = self.get_serializer(payments, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error getting user payments: {str(e)}")
            return Response(
                {"detail": "To'lovlarni olishda xatolik yuz berdi"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path=r'course/(?P<course_id>[0-9a-f-]+)')
    def course_payments(self, _, course_id=None):
        try:
            course = get_object_or_404(Course, id=course_id)
            payments = Payment.objects.filter(course=course)
            serializer = self.get_serializer(payments, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error getting course payments: {str(e)}")
            return Response(
                {"detail": "Kurs to'lovlarini olishda xatolik yuz berdi"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        payment = self.get_object()
        
        # Check if payment is completed
        if payment.status != 'completed':
            return Response(
                {'error': 'Only completed payments can be refunded'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if payment is already refunded
        if payment.status == 'refunded':
            return Response(
                {'error': 'Payment is already refunded'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check refund time limit (30 days to match serializer)
        if payment.payment_date and (timezone.now() - payment.payment_date).days > 30:
            return Response(
                {'error': 'Refund is only possible within 30 days of payment'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate refund amount
        refund_amount = request.data.get('amount', payment.amount)
        if refund_amount > payment.amount:
            return Response(
                {'error': 'Refund amount cannot exceed payment amount'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            provider = self.get_payment_provider(payment.method)
            if not provider:
                return Response(
                    {'error': 'Payment provider not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            refund_success = provider.process_refund(
                payment.payment_provider_id,
                refund_amount,
                request.data.get('reason', '')
            )
            
            if refund_success:
                payment.status = 'refunded'
                payment.refund_date = timezone.now()
                payment.refund_amount = refund_amount
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
                
        except Exception as e:
            logger.error(f"Payment refund failed: {str(e)}")
            return Response(
                {'error': 'Payment refund failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        payment = self.get_object()
        
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

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        payment = self.get_object()
        if payment.status != 'pending':
            return Response(
                {'error': 'Payment is not in pending status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            provider = self.get_payment_provider(payment.method)
            if not provider:
                return Response(
                    {'error': 'Payment provider not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            payment_status = provider.check_payment_status(payment.payment_provider_id)
            if payment_status == 'completed':
                payment.status = 'completed'
                payment.completed_at = timezone.now()
                payment.save()
                
                # Update course enrollment
                if payment.course:
                    payment.course.enrolled_students.add(payment.user)
                
                return Response(PaymentSerializer(payment).data)
            else:
                return Response(
                    {'error': f'Payment not completed. Status: {payment_status}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            logger.error(f"Payment confirmation failed: {str(e)}")
            return Response(
                {'error': 'Payment confirmation failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='webhook/(?P<provider>[^/.]+)')
    def webhook(self, request, provider=None):
        try:
            # Get payment provider
            payment_provider = get_provider(provider)
            if not payment_provider:
                return Response(
                    {"detail": "Noto'g'ri to'lov provayderi"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get signature from headers
            signature = request.headers.get('X-Signature')
            if not signature:
                return Response(
                    {"detail": "Imzo topilmadi"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verify webhook signature
            if not payment_provider.verify_webhook(request.data, signature):
                return Response(
                    {"detail": "Noto'g'ri imzo"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get payment from provider data
            payment_id = request.data.get('payment_id')
            if not payment_id:
                return Response(
                    {"detail": "To'lov ID si topilmadi"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Find payment in our system
            try:
                payment = Payment.objects.get(payment_provider_id=payment_id)
            except Payment.DoesNotExist:
                return Response(
                    {"detail": "To'lov topilmadi"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Update payment status
            status = payment_provider.check_payment_status(payment_id)
            if status:
                payment.status = status
                if status == 'completed':
                    payment.completed_at = timezone.now()
                payment.save()
            
            return Response({"detail": "OK"})
            
        except Exception as e:
            logger.error(f"Webhook processing failed: {str(e)}")
            return Response(
                {"detail": "Webhook qayta ishlashda xatolik yuz berdi"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PaymentListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.is_staff:
            payments = Payment.objects.all()
        else:
            payments = Payment.objects.filter(user=request.user)
            
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                payment = serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Payment creation error: {str(e)}")
                return Response(
                    {"detail": "To'lov yaratishda xatolik yuz berdi"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PaymentDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        return get_object_or_404(Payment, pk=pk)
    
    def get(self, request, pk):
        payment = self.get_object(pk)
        if not (request.user.is_staff or payment.user == request.user):
            return Response(
                {"detail": "Ruxsat yo'q"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)
    
    def put(self, request, pk):
        payment = self.get_object(pk)
        if not request.user.is_staff:
            return Response(
                {"detail": "Ruxsat yo'q"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = PaymentSerializer(payment, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data)
            except Exception as e:
                logger.error(f"Payment update error: {str(e)}")
                return Response(
                    {"detail": "To'lov ma'lumotlarini yangilashda xatolik yuz berdi"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserPaymentsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        payments = Payment.objects.filter(user=request.user)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

class PaymentVerifyView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        payment = self.get_object(pk)
        if not request.user.is_staff:
            return Response(
                {"detail": "Ruxsat yo'q"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        try:
            payment.verify_payment()
            serializer = PaymentSerializer(payment)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Payment verification error: {str(e)}")
            return Response(
                {"detail": "To'lovni tasdiqlashda xatolik yuz berdi"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )