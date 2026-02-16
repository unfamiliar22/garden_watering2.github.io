from django.urls import path
from . import views

urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),
    
    # Аутентификация
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Профиль
    path('profile/', views.profile, name='profile'),
    
    # Панель управления
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Управление зонами
    path('zone/create/', views.zone_create, name='zone_create'),
    path('zone/<int:zone_id>/edit/', views.zone_edit, name='zone_edit'),
    path('zone/<int:zone_id>/delete/', views.zone_delete, name='zone_delete'),
    
    # Управление расписанием
    path('zone/<int:zone_id>/schedule/create/', views.schedule_create, name='schedule_create'),
    path('schedule/<int:schedule_id>/delete/', views.schedule_delete, name='schedule_delete'),
    
    # Управление поливом
    path('zone/<int:zone_id>/water/', views.start_watering, name='start_watering'),
    path('history/', views.watering_history, name='watering_history'),
    
    # API
    path('api/zone/<int:zone_id>/status/', views.api_zone_status, name='api_zone_status'),
    path('api/schedule/<int:schedule_id>/toggle/', views.api_toggle_schedule, name='api_toggle_schedule'),
]
