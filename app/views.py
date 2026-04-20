import subprocess
import sys

from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .filters import CourseFilter
from .models import Course, Enrollment, Module, Submission, Task, TestCase
from .pagination import StandardPagination
from .permissions import IsCourseOwner, IsModuleCourseOwner, IsTaskCourseOwner, IsTestCaseCourseOwner
from .serializers import *


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=LogoutSerializer, responses={205: "Logout successful", 400: "Invalid token"})
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)










#courses

class CourseListCreateView(ListCreateAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = CourseFilter
    search_fields = ["title", "description"]

    def get_queryset(self):
        return Course.objects.all().order_by("-created_at")

    def perform_create(self, serializer):
        course = serializer.save(owner=self.request.user)
        Enrollment.objects.get_or_create(user=self.request.user, course=course)



class CourseDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsCourseOwner]
    queryset = Course.objects.all()




class MyCreatedCoursesView(ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        return Course.objects.filter(owner=self.request.user).order_by("-created_at")







#enrollments
class EnrollCourseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)

        enrollment = Enrollment.objects.filter(user=request.user, course=course).first()

        if enrollment:
            return Response(EnrollmentSerializer(enrollment).data,status=status.HTTP_200_OK)

        enrollment = Enrollment.objects.create(user=request.user,course=course)
        return Response(EnrollmentSerializer(enrollment).data,status=status.HTTP_201_CREATED)








class EnrollmentListView(ListAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user).select_related("course", "course__owner").order_by("-enrolled_at")







#coures owner info

class CourseStudentsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)

        if course.owner != request.user:
            raise PermissionDenied("Only the course owner can view students")

        total_tasks = Task.objects.filter(module__course=course).count()
        enrollments = Enrollment.objects.filter(course=course).exclude(user=course.owner).select_related("user")

        data = []

        for enroll in enrollments:
            solved_tasks = Submission.objects.filter(user=enroll.user,task__module__course=course,status="pass").values("task").distinct().count()

            percent = 0
            if total_tasks:
                percent = round((solved_tasks / total_tasks) * 100)

            data.append({
                "user": enroll.user.id,
                "username": enroll.user.username,
                "total_tasks": total_tasks,
                "solved_tasks": solved_tasks,
                "percent": percent,
                "is_completed": total_tasks > 0 and solved_tasks >= total_tasks
            })

        return Response(data)





class CourseStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)

        if course.owner != request.user:
            raise PermissionDenied("Only the course owner can view course stats")

        tasks_count = Task.objects.filter(module__course=course).count()
        modules_count = Module.objects.filter(course=course).count()
        submissions_count = Submission.objects.filter(task__module__course=course).count()

        students = Enrollment.objects.filter(course=course).exclude(user=course.owner)

        completed_count = 0

        for enroll in students:
            solved_tasks = Submission.objects.filter(user=enroll.user,task__module__course=course,status="pass").values("task").distinct().count()

            if tasks_count > 0 and solved_tasks >= tasks_count:
                completed_count += 1

        return Response({
            "course": course.id,
            "students_count": students.count(),
            "modules_count": modules_count,
            "tasks_count": tasks_count,
            "submissions_count": submissions_count,
            "completed_count": completed_count
        })



#modules

class ModuleListCreateView(ListCreateAPIView):
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Module.objects.filter(course_id=self.kwargs["course_id"])

    def perform_create(self, serializer):
        course = get_object_or_404(Course, pk=self.kwargs["course_id"])
        if course.owner != self.request.user:
            raise PermissionDenied("Only the course owner can add modules.")
        serializer.save(course=course)




class ModuleDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsModuleCourseOwner]
    queryset = Module.objects.all()







#tasks
class TaskListCreateView(ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(module_id=self.kwargs["module_id"])

    def perform_create(self, serializer):
        module = get_object_or_404(Module, pk=self.kwargs["module_id"])
        if module.course.owner != self.request.user:
            raise PermissionDenied("Only the course owner can add tasks.")
        serializer.save(module=module)




class TaskDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsTaskCourseOwner]
    queryset = Task.objects.all()







#test cases

class TestCaseListCreateView(ListCreateAPIView):
    serializer_class = TestCaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        task = get_object_or_404(Task, pk=self.kwargs["task_id"])
        if task.module.course.owner != self.request.user:
            raise PermissionDenied("Only the course owner can view test cases.")
        return TestCase.objects.filter(task=task)

    def perform_create(self, serializer):
        task = get_object_or_404(Task, pk=self.kwargs["task_id"])
        if task.module.course.owner != self.request.user:
            raise PermissionDenied("Only the course owner can add test cases.")
        serializer.save(task=task)




class TestCaseDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = TestCaseSerializer
    permission_classes = [permissions.IsAuthenticated, IsTestCaseCourseOwner]
    queryset = TestCase.objects.all()




#submit code

class SubmitCodeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Submit code for the task from task_id in the URL.",
        manual_parameters=[openapi.Parameter("task_id", openapi.IN_PATH, description="Task ID.", type=openapi.TYPE_INTEGER, required=True)],
        request_body=SubmitCodeSerializer,
        responses={200: SubmitCodeResponseSerializer, 400: "Validation error"}
    )




    def post(self, request, task_id):
        task = get_object_or_404(Task, pk=task_id)
        course = task.module.course

        if course.owner != request.user and not Enrollment.objects.filter(user=request.user, course=course).exists():
            raise PermissionDenied("Enroll in this course before submitting solutions.")

        serializer = SubmitCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        submission = Submission.objects.create(user=request.user, task=task, code=serializer.validated_data["code"], status="pending")
        test_cases = TestCase.objects.filter(task=task)

        if not test_cases.exists():
            submission.status = "fail"
            submission.save()
            return Response({"message": "Task has no test cases.", "already_solved": False, "submission": SubmissionSerializer(submission).data}, status=status.HTTP_400_BAD_REQUEST)

        already_solved = Submission.objects.filter(user=request.user, task=task, status="pass").exclude(id=submission.id).exists()

        submission.status = "pass" if self.check_solution(submission.code, test_cases) else "fail"
        submission.save()

        message = "Correct answer." if submission.status == "pass" else "Wrong answer."
        return Response({"submission": SubmissionSerializer(submission).data, "message": message, "already_solved": already_solved})



    def check_solution(self, code, test_cases):
        for tc in test_cases:
            try:
                result = subprocess.run(
                    [sys.executable, "-c", code],
                    input=tc.input,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            except subprocess.TimeoutExpired:
                return False

            if result.stdout.strip() != tc.expected_output.strip():
                return False
            
        return True






#submissons hostory

class SubmissionListView(ListAPIView):
    serializer_class = SubmissionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = Submission.objects.filter(user=self.request.user).select_related("task").order_by("-submitted_at")
        task_id = self.request.query_params.get("task")
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        return queryset








#progres

class CourseProgressView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)

        total_tasks = Task.objects.filter(module__course=course).count()
        solved_tasks = Submission.objects.filter(user=request.user, task__module__course=course, status="pass").values("task").distinct().count()

        percent = 0
        if total_tasks:
            percent = round((solved_tasks / total_tasks) * 100)

        return Response({
            "course": course.id,
            "total_tasks": total_tasks,
            "solved_tasks": solved_tasks,
            "percent": percent,
            "is_completed": total_tasks > 0 and solved_tasks >= total_tasks
        })







#leaderboard

class LeaderboardView(ListAPIView):
    serializer_class = LeaderboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        return Submission.objects.filter(status="pass").values("user__id", "user__username").annotate(solved_count=Count("task", distinct=True)).order_by("-solved_count")
