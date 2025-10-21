from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
import hashlib
from decimal import Decimal

from .models import StringAnalysisResult
from .serializers import CreateStringAnalysisSerializer, StringAnalysisResultSerializer
from .filter import StringAnalysisResultFilter
from .utils import parse_nl_query, make_json_safe

# -------------------------
# Home view
# -------------------------
from django.http import JsonResponse

def home_view(request):
    return JsonResponse({"message": "Welcome to String Analyzer API"})


# -------------------------
# Combined GET / POST
# -------------------------
class StringListCreateView(generics.ListCreateAPIView):
    queryset = StringAnalysisResult.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend]
    filterset_class = StringAnalysisResultFilter

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateStringAnalysisSerializer
        return StringAnalysisResultSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = make_json_safe(serializer.data)

        filters_applied = {
            k: v[0] if isinstance(v, list) else v
            for k, v in dict(request.query_params).items()
            if v and v != ['']
        }

        return Response({
            "data": data,
            "count": queryset.count(),
            "filters_applied": filters_applied
        })


# -------------------------
# GET /strings/{string_value} and DELETE /strings/{string_value}
# -------------------------
class GetStringAnalysisResultView(APIView):
    def get(self, request, string_value):
        sha256_hash = hashlib.sha256(string_value.encode('utf-8')).hexdigest()
        try:
            result = StringAnalysisResult.objects.get(id=sha256_hash)
        except StringAnalysisResult.DoesNotExist:
            return Response({"details": "String does not exist in the system"}, status=404)
        return Response({"data": StringAnalysisResultSerializer(result).data}, status=200)

    def delete(self, request, string_value):
        sha256_hash = hashlib.sha256(string_value.encode('utf-8')).hexdigest()
        try:
            result = StringAnalysisResult.objects.get(id=sha256_hash)
        except StringAnalysisResult.DoesNotExist:
            return Response({"details": "String does not exist in the system"}, status=404)
        result.delete()
        return Response(status=204)




# -------------------------
# GET /strings/filter-by-natural-language
# -------------------------
from rest_framework.decorators import api_view

@api_view(['GET'])
def nl_query_view(request):
    query = request.query_params.get("query", "")
    if not query:
        return Response({"details": "query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        filters = parse_nl_query(query)
    except ValueError:
        return Response({"details": "Unable to parse Natural language query"}, status=status.HTTP_400_BAD_REQUEST)

    queryset = StringAnalysisResult.objects.all()
    if filters.get("is_palindrome"):
        queryset = queryset.filter(components__is_palindrome=True)
    if "min_length" in filters:
        queryset = queryset.filter(components__length__gte=filters["min_length"])
    if "max_length" in filters:
        queryset = queryset.filter(components__length__lte=filters["max_length"])
    if "word_count" in filters:
        queryset = queryset.filter(components__word_count=filters["word_count"])
    if "contains_letter" in filters:
        key = filters["contains_letter"]
        queryset = queryset.filter(components__character_frequency__has_key=key)

    serializer = StringAnalysisResultSerializer(queryset, many=True)

    return Response({
        "data": make_json_safe(serializer.data),
        "count": queryset.count(),
        "interpreted_query": {"original_query": query, "applied_filters": filters}
    })
