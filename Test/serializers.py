from rest_framework import serializers
from .models import Test, Question, Answer, TestResult
from Course.models import Course
from CustomerUser.models import CustomerUser

class AnswerSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    text = serializers.CharField(max_length=200)
    is_correct = serializers.BooleanField()

    def create(self, validated_data):
        return Answer.objects.create(**validated_data)

class QuestionSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    test = serializers.PrimaryKeyRelatedField(queryset=Test.objects.all())
    text = serializers.CharField()
    points = serializers.IntegerField(default=1)
    order = serializers.IntegerField()
    answers = AnswerSerializer(many=True, read_only=True)

    def create(self, validated_data):
        return Question.objects.create(**validated_data)

class QuestionCreateSerializer(serializers.Serializer):
    test = serializers.PrimaryKeyRelatedField(queryset=Test.objects.all())
    text = serializers.CharField()
    points = serializers.IntegerField(default=1)
    order = serializers.IntegerField()

    def create(self, validated_data):
        return Question.objects.create(**validated_data)

class TestSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    title = serializers.CharField(max_length=200)
    description = serializers.CharField()
    duration_minutes = serializers.IntegerField()
    passing_score = serializers.IntegerField()
    is_active = serializers.BooleanField(default=True)
    created_by = serializers.PrimaryKeyRelatedField(queryset=CustomerUser.objects.all(), required=False)
    questions = QuestionSerializer(many=True, read_only=True)

    def create(self, validated_data):
        return Test.objects.create(**validated_data)

class TestResultSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=CustomerUser.objects.all())
    test = serializers.PrimaryKeyRelatedField(queryset=Test.objects.all())
    score = serializers.IntegerField()  # Integer sifatida aniqlandi
    completed_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        return TestResult.objects.create(**validated_data)