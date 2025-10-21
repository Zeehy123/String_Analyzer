from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import StringAnalysisResult
import hashlib
from .serializers import CreateStringAnalysisSerializer, StringAnalysisResultSerializer
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import generics
from .filter import StringAnalysisResultFilter
from rest_framework.decorators import api_view
from .utils import parse_nl_query
from django_filters.rest_framework import DjangoFilterBackend

# Create your views here.

from django.http import JsonResponse

def home_view(request):
    return JsonResponse({"message": "Welcome to String Analyzer API"})

class CreateStringAnalysisResultView(APIView):
    #Post /string

    def post(self, request):
        serializer = CreateStringAnalysisSerializer(data=request.data)
        if not serializer.is_valid():
            errors = serializer.errors
            if "value" in errors:
                return Response({"details": errors["value"][0]}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"details": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = serializer.save()
        except ValidationError:
            return Response({"details": "string analysis already exists"}, status=status.HTTP_409_CONFLICT)
          

        output=StringAnalysisResultSerializer(result).data
        return Response(output, status=status.HTTP_201_CREATED)
    
  
class GetStringAnalysisResultView(APIView):
    #GET /string/{string_id}

    def get(self, request, string_value):
        sha256_hash = hashlib.sha256(string_value.encode("utf-8")).hexdigest()
        try:
            result = StringAnalysisResult.objects.get(id=sha256_hash)
        except StringAnalysisResult.DoesNotExist:
            return Response({"details": "String not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(StringAnalysisResultSerializer(result).data, status=status.HTTP_200_OK)

    def delete(self,request,string_value):
        sha256_hash=hashlib.sha256(string_value.encode("utf-8")).hexdigest()
        result=StringAnalysisResult.objects.filter(value=string_value)
        if not result.exists():
            return Response({"details":"not found"},status=status.HTTP_404_NOT_FOUND)
        result.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

from decimal import Decimal

class ListStringView(generics.ListAPIView):
    serializer_class = StringAnalysisResultSerializer
    queryset = StringAnalysisResult.objects.all().order_by("-created_at")
    filter_backends = [DjangoFilterBackend]
    filterset_class = StringAnalysisResultFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

     
        from .utils import make_json_safe
        data = make_json_safe(serializer.data)

        filters_applied = {
            k: v[0] if isinstance(v, list) else v
            for k, v in dict(request.query_params).items()
            if v and v != ['']
        }

        response_data = {
            "data": data,
            "count": len(data),
            "filters_applied": filters_applied,
        }

        # # ✅ Debug: find any Decimal value before sending to Response
        # def find_decimal(obj, path="root"):
        #     if isinstance(obj, Decimal):
        #         print(f"⚠️ Decimal found at {path}: {obj}")
        #     elif isinstance(obj, dict):
        #         for k, v in obj.items():
        #             find_decimal(v, f"{path}.{k}")
        #     elif isinstance(obj, list):
        #         for i, v in enumerate(obj):
        #             find_decimal(v, f"{path}[{i}]")

        # find_decimal(response_data)

      
     
        return Response(response_data)
       
            



@api_view(['GET'])
def nl_query_view(request):
    query = request.query_params.get("query", "")
    if not query:
        return Response({"details": "query parameter is required."}, status=400)

    try:
        filters = parse_nl_query(query)
    except ValueError:
        return Response({"details": "Unable to parse Natural language query"}, status=400)

  
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
        "data": serializer.data,
        "count": queryset.count(),
        "interpreted_query": {"original_query": query, "applied_filters": filters}
    })
