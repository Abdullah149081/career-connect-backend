from django_filters import rest_framework as filters
from .models import JobListing


class JobListingFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr="icontains")
    location = filters.CharFilter(lookup_expr="icontains")
    category = filters.NumberFilter(field_name="category__id")
    employment_type = filters.ChoiceFilter(choices=JobListing.EMPLOYMENT_TYPE_CHOICES)
    salary_min = filters.NumberFilter(field_name="salary_min", lookup_expr="gte")
    salary_max = filters.NumberFilter(field_name="salary_max", lookup_expr="lte")

    class Meta:
        model = JobListing
        fields = [
            "title",
            "location",
            "category",
            "employment_type",
            "salary_min",
            "salary_max",
        ]
