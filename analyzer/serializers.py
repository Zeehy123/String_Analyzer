from rest_framework import serializers
from .models import StringAnalysisResult
from .utils import compute_component
from .utils import make_json_safe

class DuplicateStringError(Exception):
    pass

class CreateStringAnalysisSerializer(serializers.Serializer):
    value = serializers.CharField()

    class Meta:
        model = StringAnalysisResult
        fields = ["value"]

    def validate_value(self, v):
        # Check the raw input type to reject numbers
        request_data = self.context.get('request').data if self.context.get('request') else {}
        raw_value = request_data.get('value')
        if not isinstance(raw_value, str):
            raise serializers.ValidationError("Value must be a string.")
        return v
    
    def create(self, validated_data):
        v = validated_data['value']
        components = make_json_safe(compute_component(v))
        sha256_hash = components['sha256_hash']

        # Check for duplicates
        if StringAnalysisResult.objects.filter(id=sha256_hash).exists():
            # Do NOT raise ValidationError here; we'll handle 409 in the view
            raise DuplicateStringError("String analysis already exists.")

        return StringAnalysisResult.objects.create(
            id=sha256_hash,
            value=v,
            components=components
        )

     
class StringAnalysisResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = StringAnalysisResult
        fields = ['id', 'value', 'components', 'created_at']




        