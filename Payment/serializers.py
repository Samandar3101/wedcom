from rest_framework import serializers
from .models import Payment
from CustomerUser.models import CustomerUser
from Course.models import Course
from django.utils import timezone

class PaymentSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=CustomerUser.objects.all(), required=False)
    user_email = serializers.CharField(source='user.email', read_only=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    course_title = serializers.CharField(source='course.title', read_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
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
        # Ensure method is provided and valid
        method = data.get('method')
        if not method:
            raise serializers.ValidationError("To'lov usuli kiritilishi shart.")
        if method not in dict(Payment.PAYMENT_METHODS):
            raise serializers.ValidationError(f"'{method}' to'g'ri to'lov usuli emas.")
        
        # Validate course exists and has a price
        course = data.get('course')
        if not course:
            raise serializers.ValidationError("Kurs tanlanishi shart.")
        
        if not hasattr(course, 'price') or not course.price:
            raise serializers.ValidationError("Kurs narxi to'g'ri ko'rsatilmagan.")
        
        # Validate payment method based on amount
        amount = course.price
        if method == 'cash' and amount > 1000000:  # 1 million so'm
            raise serializers.ValidationError(
                "Naqd pul orqali to'lov 1 million so'mdan oshmasligi kerak"
            )
        
        # Set amount from course price
        data['amount'] = amount
        
        return data

    def create(self, validated_data):
        # Extract user from context (set by view)
        user = self.context['request'].user
        course = validated_data['course']
        
        payment = Payment(
            user=user,
            course=course,
            amount=course.price,
            status='pending',
            method=validated_data['method']
        )
        payment.save()
        return payment

    def update(self, instance, validated_data):
        # Only allow updating payment provider fields
        instance.payment_provider_id = validated_data.get('payment_provider_id', instance.payment_provider_id)
        instance.payment_provider_data = validated_data.get('payment_provider_data', instance.payment_provider_data)
        instance.save()
        return instance

class PaymentRefundSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    reason = serializers.CharField(required=True)

    def validate(self, data):
        payment = self.context['payment']
        amount = data.get('amount')
        
        if amount is None:
            amount = payment.amount
        
        if amount <= 0:
            raise serializers.ValidationError(
                "Qaytariladigan summa 0 dan katta bo'lishi kerak"
            )
        
        if amount > payment.amount:
            raise serializers.ValidationError(
                "Qaytariladigan summa to'lov summasidan ko'p bo'lishi mumkin emas"
            )
        
        if payment.status != 'completed':
            raise serializers.ValidationError(
                "Faqat yakunlangan to'lovlarni qaytarish mumkin"
            )
        
        if payment.refund_amount:
            raise serializers.ValidationError(
                "Bu to'lov allaqachon qaytarilgan"
            )
        
        # Check if refund is within allowed time period (e.g., 30 days)
        if payment.payment_date:
            days_since_payment = (timezone.now() - payment.payment_date).days
            if days_since_payment > 30:
                raise serializers.ValidationError(
                    "To'lovdan keyin 30 kundan o'tgan bo'lsa, qaytarish mumkin emas"
                )
        
        # Validate reason length
        reason = data.get('reason', '').strip()
        if len(reason) < 10:
            raise serializers.ValidationError(
                "Qaytarish sababi kamida 10 ta belgidan iborat bo'lishi kerak"
            )
        
        data['amount'] = amount
        return data