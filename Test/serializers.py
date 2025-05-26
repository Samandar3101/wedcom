from rest_framework import serializers
from Course.models import Course
from CustomerUser.models import CustomerUser
from .models import Test, Question, Answer, TestResult
from Course.serializers import CourseSerializer
from CustomerUser.serializers import CustomerUserSerializer
import uuid

class TestSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    course = CourseSerializer(read_only=True)
    course_id = serializers.UUIDField(write_only=True)
    created_by = CustomerUserSerializer(read_only=True)
    
    class Meta:
        model = Test
        fields = ['id', 'course', 'course_id', 'title', 'description', 'duration_minutes', 
                 'passing_score', 'is_active', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def validate_duration_minutes(self, value):
        if value < 1:
            raise serializers.ValidationError("Test davomiyligi kamida 1 daqiqa bo'lishi kerak")
        return value

    def validate_passing_score(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("O'tish balli 0 dan 100 gacha bo'lishi kerak")
        return value

    def create(self, validated_data):
        course_id = validated_data.pop('course_id')
        course = Course.objects.get(id=course_id)
        test = Test.objects.create(course=course, **validated_data)
        return test

    def update(self, instance, validated_data):
        course_id = validated_data.pop('course_id', None)
        if course_id:
            instance.course = Course.objects.get(id=course_id)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class QuestionSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    test = TestSerializer(read_only=True)
    test_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'test', 'test_id', 'text', 'order', 'points', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_points(self, value):
        if value < 0:
            raise serializers.ValidationError("Ball manfiy bo'lishi mumkin emas")
        return value

class QuestionCreateSerializer(QuestionSerializer):
    answers = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=True
    )

    class Meta(QuestionSerializer.Meta):
        fields = QuestionSerializer.Meta.fields + ['answers']

    def validate_answers(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Kamida 2 ta javob bo'lishi kerak")
        
        correct_answers = [ans for ans in value if ans.get('is_correct')]
        if not correct_answers:
            raise serializers.ValidationError("Kamida 1 ta to'g'ri javob bo'lishi kerak")
        
        return value

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        test_id = validated_data.pop('test_id')
        test = Test.objects.get(id=test_id)
        question = Question.objects.create(test=test, **validated_data)
        for answer_data in answers_data:
            Answer.objects.create(question=question, **answer_data)
        return question

    def update(self, instance, validated_data):
        test_id = validated_data.pop('test_id', None)
        if test_id:
            instance.test = Test.objects.get(id=test_id)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class AnswerSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    question = QuestionSerializer(read_only=True)
    question_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Answer
        fields = ['id', 'question', 'question_id', 'text', 'is_correct', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class TestResultSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    test = TestSerializer(read_only=True)
    test_id = serializers.UUIDField(write_only=True)
    user = CustomerUserSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = TestResult
        fields = ['id', 'test', 'test_id', 'user', 'user_id', 'score', 'passed', 
                 'started_at', 'completed_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'score', 'passed', 'created_at', 'updated_at']

    def validate(self, data):
        if data.get('completed_at') and data.get('started_at'):
            if data['completed_at'] < data['started_at']:
                raise serializers.ValidationError("Tugash vaqti boshlash vaqtidan oldin bo'lishi mumkin emas")
        return data

    def create(self, validated_data):
        test_id = validated_data.pop('test_id')
        user_id = validated_data.pop('user_id')
        test = Test.objects.get(id=test_id)
        user = CustomerUser.objects.get(id=user_id)
        result = TestResult.objects.create(test=test, user=user, **validated_data)
        return result

    def update(self, instance, validated_data):
        test_id = validated_data.pop('test_id', None)
        user_id = validated_data.pop('user_id', None)
        if test_id:
            instance.test = Test.objects.get(id=test_id)
        if user_id:
            instance.user = CustomerUser.objects.get(id=user_id)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance