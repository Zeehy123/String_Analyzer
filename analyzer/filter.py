from django_filters import rest_framework as filters
from .models import StringAnalysisResult

class StringAnalysisResultFilter(filters.FilterSet):
    is_palindrome = filters.BooleanFilter(method='filter_is_palindrome')
    min_length = filters.NumberFilter(method='filter_min_length')
    max_length = filters.NumberFilter(method='filter_max_length')
    word_count = filters.NumberFilter(method='filter_word_count')
    contains_character = filters.CharFilter(method='filter_contains_character')

    class Meta:
        model = StringAnalysisResult
        fields = ['is_palindrome', 'min_length', 'max_length', 'word_count', 'contains_character']

    def filter_is_palindrome(self, queryset, name, value):
        if isinstance(value, str):
            value = value.lower() == 'true'
        return queryset.filter(components__is_palindrome=value)

    def filter_min_length(self, queryset, name, value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            return queryset
        return queryset.filter(components__length__gte=value)

    def filter_max_length(self, queryset, name, value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            return queryset
        return queryset.filter(components__length__lte=value)

    def filter_word_count(self, queryset, name, value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            return queryset
        return queryset.filter(components__word_count=value)

    def filter_contains_character(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(components__character_frequency__has_key=value)
