from rest_framework import serializers
from .models import StringAnalysisResult
from .utils import compute_component
from .utils import make_json_safe

class CreateStringAnalysisSerializer(serializers.Serializer):
    value = serializers.CharField()

    def validate_value(self, v):
        if not isinstance(v, str):
            raise serializers.ValidationError("Value must be a string.")
        return v
    def create(self, validated_data):
        v = validated_data['value']
        components = make_json_safe(compute_component(v))

        sha256_hash = components['sha256_hash']

        #if exists return 409
        if StringAnalysisResult.objects.filter(id=sha256_hash).exists():
            raise serializers.ValidationError("String analysis already exists.", code=409)
        
        string_analysis = StringAnalysisResult.objects.create(
            id=sha256_hash,
            value=v,
            components=components
        )
        return string_analysis
     
class StringAnalysisResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = StringAnalysisResult
        fields = ['id', 'value', 'components', 'created_at']




        