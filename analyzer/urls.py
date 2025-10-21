from django.urls import path
from .views import StringListCreateView ,GetStringAnalysisResultView,nl_query_view

urlpatterns=[
  path('strings',StringListCreateView.as_view(),name='list_create_string'),

  path("strings/<str:string_value>",GetStringAnalysisResultView.as_view(),name="get_string"),
  path("strings/filter-by-natural-language",nl_query_view,name="nl_query"),


]