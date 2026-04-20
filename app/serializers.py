from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Course, Enrollment, Module, Submission, Task, TestCase


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data['username'], password=validated_data['password'])
        return user


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()












class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']





class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = ['id', 'input', 'expected_output']




class TaskSerializer(serializers.ModelSerializer):
    test_cases = serializers.SerializerMethodField()
    is_solved = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'order_index', 'is_solved', 'test_cases']

    def get_test_cases(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and obj.module.course.owner == request.user:
            return TestCaseSerializer(obj.test_cases.all(), many=True).data
        return []

    def get_is_solved(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Submission.objects.filter(user=request.user, task=obj, status='pass').exists()





class ModuleSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ['id', 'title', 'order_index', 'tasks']





class CourseSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'owner', 'modules', 'created_at']





class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'enrolled_at']





class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['id', 'task', 'code', 'status', 'submitted_at']
        read_only_fields = ['status', 'submitted_at']





class SubmissionHistorySerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source='task.title', read_only=True)

    class Meta:
        model = Submission
        fields = ['id', 'task', 'task_title', 'code', 'status', 'submitted_at']






class SubmitCodeSerializer(serializers.Serializer):
    code = serializers.CharField(help_text="Your Python code for this task.")








class SubmitCodeResponseSerializer(serializers.Serializer):
    submission = SubmissionSerializer()
    message = serializers.CharField()
    already_solved = serializers.BooleanField()



class LeaderboardSerializer(serializers.Serializer):
    user__id = serializers.IntegerField()
    user__username = serializers.CharField()
    solved_count = serializers.IntegerField()
