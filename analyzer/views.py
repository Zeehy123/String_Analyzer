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
            if "details" in serializer.errors and serializer.errors["details"] == "string already exists":
                return Response({"details": "strings already exists"}, status=status.HTTP_409_CONFLICT)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            result = serializer.save()
        except ValidationError:
            return Response({"details": "string analysis already exists"}, status=status.HTTP_409_CONFLICT)
          

        output=StringAnalysisResultSerializer(result).data
        return Response(output, status=status.HTTP_201_CREATED)
    
  
class GetStringAnalysisResultView(APIView):
    #GET /string/{string_id}

    def get(self, request, string_value):
        
      sha256_hash=hashlib.sha256(string_value.encode("utf-8")).hexdigest()
      result=get_object_or_404(StringAnalysisResult, id=sha256_hash)
      return Response(StringAnalysisResultSerializer(result).data, status=status.HTTP_200_OK)
    
    def delete(self,request,string_value):
        sha256_hash=hashlib.sha256(string_value.encode("utf-8")).hexdigest()
        result=StringAnalysisResult.objects.filter(id=sha256_hash)
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
        data = make_json_safe(data)

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

        # ✅ Debug: find any Decimal value before sending to Response
        def find_decimal(obj, path="root"):
            if isinstance(obj, Decimal):
                print(f"⚠️ Decimal found at {path}: {obj}")
            elif isinstance(obj, dict):
                for k, v in obj.items():
                    find_decimal(v, f"{path}.{k}")
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    find_decimal(v, f"{path}[{i}]")

        find_decimal(response_data)

        # ✅ Now wrap response in try-except
        try:
            return Response(response_data)
        except TypeError as e:
            print("💥 TypeError during JSON serialization:", e)
            import pprint
            pprint.pprint(response_data)
            raise e



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
