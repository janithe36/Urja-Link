# core/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from .analysis import analyze_ait_campus # Our AI logic

class AnalyzeAITCampusView(APIView):
    def get(self, request, format=None):
        """
        This endpoint triggers the analysis for the AIT Pune campus
        and returns the rooftop data.
        """
        rooftop_data = analyze_ait_campus()
        return Response(rooftop_data)