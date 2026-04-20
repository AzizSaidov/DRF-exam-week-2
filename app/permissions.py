from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsCourseOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsModuleCourseOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.course.owner == request.user


class IsTaskCourseOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.module.course.owner == request.user


class IsTestCaseCourseOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.task.module.course.owner == request.user
