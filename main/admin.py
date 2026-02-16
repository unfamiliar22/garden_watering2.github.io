from django.contrib import admin
from .models import UserProfile, GardenZone, WateringSchedule, WateringLog, SensorReading, SystemStatus


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'address', 'created_at']
    search_fields = ['user__username', 'phone', 'address']
    list_filter = ['created_at']


@admin.register(GardenZone)
class GardenZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'plant_type', 'area_size', 'watering_duration', 'created_at']
    search_fields = ['name', 'user__username', 'plant_type']
    list_filter = ['created_at', 'plant_type']


@admin.register(WateringSchedule)
class WateringScheduleAdmin(admin.ModelAdmin):
    list_display = ['zone', 'time', 'days_of_week', 'is_active']
    list_filter = ['is_active', 'days_of_week']
    search_fields = ['zone__name']


@admin.register(WateringLog)
class WateringLogAdmin(admin.ModelAdmin):
    list_display = ['zone', 'started_at', 'duration', 'water_used', 'is_manual']
    list_filter = ['is_manual', 'started_at']
    search_fields = ['zone__name']
    date_hierarchy = 'started_at'


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ['zone', 'timestamp', 'soil_moisture', 'temperature', 'humidity']
    list_filter = ['timestamp']
    search_fields = ['zone__name']
    date_hierarchy = 'timestamp'


@admin.register(SystemStatus)
class SystemStatusAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_online', 'last_connection', 'water_pressure', 'total_water_used']
    list_filter = ['is_online']
    search_fields = ['user__username']
