from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import *

urlpatterns = [
    path("auth/register/", RegisterView.as_view()),
    path("auth/login/", TokenObtainPairView.as_view()),
    path("auth/refresh/", TokenRefreshView.as_view()),
    path("auth/logout/", LogoutView.as_view()),

    path("courses/", CourseListCreateView.as_view()),
    path("my-created-courses/", MyCreatedCoursesView.as_view()),
    path("courses/<int:pk>/", CourseDetailView.as_view()),
    path("courses/<int:course_id>/enroll/", EnrollCourseView.as_view()),
    path("courses/<int:course_id>/modules/", ModuleListCreateView.as_view()),
    path("courses/<int:course_id>/progress/", CourseProgressView.as_view()),
    path("courses/<int:course_id>/stats/", CourseStatsView.as_view()),
    path("courses/<int:course_id>/students/", CourseStudentsView.as_view()),

    path("enrollments/", EnrollmentListView.as_view()),

    path("modules/<int:pk>/", ModuleDetailView.as_view()),
    path("modules/<int:module_id>/tasks/", TaskListCreateView.as_view()),

    path("tasks/<int:pk>/", TaskDetailView.as_view()),
    path("tasks/<int:task_id>/test-cases/", TestCaseListCreateView.as_view()),
    path("tasks/<int:task_id>/submit/", SubmitCodeView.as_view()),

    path("submissions/", SubmissionListView.as_view()),

    path("test-cases/<int:pk>/", TestCaseDetailView.as_view()),
    
    path("leaderboard/", LeaderboardView.as_view()),
]
