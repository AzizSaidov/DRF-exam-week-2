from django.contrib import admin

from .models import Course, Enrollment, Module, Submission, Task, TestCase, User

admin.site.register(User)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Module)
admin.site.register(Task)
admin.site.register(TestCase)
admin.site.register(Submission)
