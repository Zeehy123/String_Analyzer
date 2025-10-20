from django.db import models
from django.utils import timezone

class StringAnalysisResult(models.Model):
  id=models.CharField(max_length=255, primary_key=True)
  value=models.TextField()
  components=models.JSONField() # Stores list of string componentslike length 
  created_at=models.DateTimeField(default=timezone.now)

  def __str__(self):
    return f"StringAnalysisResult(id={self.id}, value={self.value})"