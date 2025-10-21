from django.urls import path
from .views import CreateStringAnalysisResultView, ListStringView, GetStringAnalysisResultView,nl_query_view

urlpatterns=[
  path('strings',CreateStringAnalysisResultView.as_view(),name='create_string'),
  path("strings/",ListStringView.as_view(),name="list_strings"),
  path("strings/<str:string_value>/",GetStringAnalysisResultView.as_view(),name="get_string"),
  path("strings/filter-by-natural-language",nl_query_view,name="nl_query"),


]