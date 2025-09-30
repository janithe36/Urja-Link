# backend/urls.py
from django.contrib import admin
from django.urls import path
from core.views import AnalyzeAITCampusView # Our API view

urlpatterns = [
    path('admin/', admin.site.urls),
    # This defines the URL for our API
    path('api/analyze-ait-campus/', AnalyzeAITCampusView.as_view()),
]