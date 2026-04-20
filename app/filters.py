from django_filters import rest_framework as filters

from .models import Course


class CourseFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='icontains')
    owner = filters.NumberFilter(field_name='owner__id')

    class Meta:
        model = Course
        fields = ['title', 'owner']
