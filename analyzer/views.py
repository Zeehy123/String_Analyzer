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
from rest_framework import generics, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import StringAnalysisResult
from .serializers import CreateStringAnalysisSerializer, StringAnalysisResultSerializer
from .filter import StringAnalysisResultFilter
from .utils import make_json_safe

class StringListCreateView(generics.ListCreateAPIView):
    queryset = StringAnalysisResult.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend]
    filterset_class = StringAnalysisResultFilter

    # -------------------------
    # POST /strings
    # -------------------------
    def post(self, request, *args, **kwargs):
        serializer = CreateStringAnalysisSerializer(data=request.data, context={'request': request})
        
        # Validation error: missing or invalid 'value'
        if not serializer.is_valid():
            error_message = serializer.errors.get('value', ["This field is required."])[0]
            return Response({"details": error_message}, status=status.HTTP_400_BAD_REQUEST)
        
        value = serializer.validated_data.get('value')
        if not isinstance(value, str):
            return Response({"details": "Invalid input"}, status=status.HTTP_400_BAD_REQUEST)

        # Save and handle duplicates
        try:
            result = serializer.save()
        except Exception:
            return Response({"details": "String already exists"}, status=status.HTTP_409_CONFLICT)
        
        # Success response
        return Response(StringAnalysisResultSerializer(result).data, status=status.HTTP_201_CREATED)

    # -------------------------
    # GET /strings with filters
    # -------------------------
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = StringAnalysisResultSerializer(queryset, many=True)
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
            if not isinstance(string_value, str) or string_value.strip() == "":
                return Response({"details": "Invalid string value provided"}, status=status.HTTP_400_BAD_REQUEST)

            sha256_hash = hashlib.sha256(string_value.encode('utf-8')).hexdigest()
            try:
                result = StringAnalysisResult.objects.get(id=sha256_hash)
            except StringAnalysisResult.DoesNotExist:
                return Response({"details": "String does not exist in the system"}, status=status.HTTP_404_NOT_FOUND)
            
            # Success: return all required fields
            return Response(StringAnalysisResultSerializer(result).data, status=status.HTTP_200_OK)


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
        return Response(
            {"details": "query parameter is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Parse the natural language query
    try:
        filters = parse_nl_query(query)
    except ValueError:
        return Response(
            {"details": "Unable to parse Natural language query"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Start with all objects
    queryset = StringAnalysisResult.objects.all()

    # Apply filters using exact keys
    if filters.get("is_palindrome") is True:
        queryset = queryset.filter(components__is_palindrome=True)
    if filters.get("min_length") is not None:
        queryset = queryset.filter(components__length__gte=filters["min_length"])
    if filters.get("max_length") is not None:
        queryset = queryset.filter(components__length__lte=filters["max_length"])
    if filters.get("word_count") is not None:
        queryset = queryset.filter(components__word_count=filters["word_count"])
    if filters.get("contains_character"):
        queryset = queryset.filter(
            components__character_frequency__has_key=filters["contains_character"]
        )

    serializer = StringAnalysisResultSerializer(queryset, many=True)

    return Response({
        "data": make_json_safe(serializer.data),
        "count": queryset.count(),
        "interpreted_query": {
            "original_query": query,
            "applied_filters": filters
        }
    }, status=status.HTTP_200_OK)
