from django.db import models
from django.contrib.auth.models import User
import json


class UserProfile(models.Model):
    """Расширенный профиль пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    address = models.CharField(max_length=255, blank=True, verbose_name='Адрес участка')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    
    def __str__(self):
        return f'Профиль {self.user.username}'
    
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'


class GardenZone(models.Model):
    """Зона полива на участке"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='garden_zones')
    name = models.CharField(max_length=100, verbose_name='Название зоны')
    description = models.TextField(blank=True, verbose_name='Описание')
    plant_type = models.CharField(max_length=100, blank=True, verbose_name='Тип растений')
    area_size = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Площадь (м²)')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Настройки полива
    watering_duration = models.IntegerField(default=10, verbose_name='Длительность полива (мин)')
    watering_frequency = models.IntegerField(default=1, verbose_name='Частота полива (раз в день)')
    
    def __str__(self):
        return f'{self.name} ({self.user.username})'
    
    class Meta:
        verbose_name = 'Зона сада'
        verbose_name_plural = 'Зоны сада'


class WateringSchedule(models.Model):
    """Расписание полива"""
    zone = models.ForeignKey(GardenZone, on_delete=models.CASCADE, related_name='schedules')
    time = models.TimeField(verbose_name='Время полива')
    days_of_week = models.CharField(max_length=50, default='1,2,3,4,5,6,7', verbose_name='Дни недели')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    
    def get_days_list(self):
        return [int(d) for d in self.days_of_week.split(',')]
    
    def set_days_list(self, days_list):
        self.days_of_week = ','.join(str(d) for d in days_list)
    
    def __str__(self):
        return f'{self.zone.name} - {self.time}'
    
    class Meta:
        verbose_name = 'Расписание полива'
        verbose_name_plural = 'Расписания полива'


class WateringLog(models.Model):
    """История полива"""
    zone = models.ForeignKey(GardenZone, on_delete=models.CASCADE, related_name='logs')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='Время начала')
    duration = models.IntegerField(verbose_name='Длительность (мин)')
    water_used = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name='Использовано воды (л)')
    is_manual = models.BooleanField(default=False, verbose_name='Ручной запуск')
    
    def __str__(self):
        return f'{self.zone.name} - {self.started_at}'
    
    class Meta:
        verbose_name = 'Запись полива'
        verbose_name_plural = 'История полива'


class SensorReading(models.Model):
    """Показания датчиков"""
    zone = models.ForeignKey(GardenZone, on_delete=models.CASCADE, related_name='sensor_readings')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Время измерения')
    soil_moisture = models.IntegerField(null=True, blank=True, verbose_name='Влажность почвы (%)')
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name='Температура (°C)')
    humidity = models.IntegerField(null=True, blank=True, verbose_name='Влажность воздуха (%)')
    
    def __str__(self):
        return f'{self.zone.name} - {self.timestamp}'
    
    class Meta:
        verbose_name = 'Показание датчика'
        verbose_name_plural = 'Показания датчиков'


class SystemStatus(models.Model):
    """Статус системы полива"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='system_status')
    is_online = models.BooleanField(default=False, verbose_name='Система онлайн')
    last_connection = models.DateTimeField(null=True, blank=True, verbose_name='Последнее подключение')
    water_pressure = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Давление воды')
    total_water_used = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Всего использовано воды (л)')
    
    def __str__(self):
        return f'Статус системы {self.user.username}'
    
    class Meta:
        verbose_name = 'Статус системы'
        verbose_name_plural = 'Статусы систем'
