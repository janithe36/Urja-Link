# core/models.py
from django.db import models

class RooftopAnalysis(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    total_potential_kwh_year = models.FloatField()

    def __str__(self):
        return f"Rooftop at ({self.latitude}, {self.longitude})"