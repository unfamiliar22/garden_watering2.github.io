from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum
from .models import UserProfile, GardenZone, WateringSchedule, WateringLog, SensorReading, SystemStatus
from .forms import UserRegistrationForm, UserProfileForm, GardenZoneForm, WateringScheduleForm, ManualWateringForm


def home(request):
    """Главная страница"""
    context = {
        'user': request.user,
        'is_authenticated': request.user.is_authenticated,
    }
    
    # Если пользователь авторизован, показываем статус системы
    if request.user.is_authenticated:
        try:
            system_status = SystemStatus.objects.get(user=request.user)
            context['system_status'] = system_status
        except SystemStatus.DoesNotExist:
            # Создаем статус системы при первом входе
            system_status = SystemStatus.objects.create(user=request.user)
            context['system_status'] = system_status
        
        # Статистика для дашборда
        context['zones_count'] = GardenZone.objects.filter(user=request.user).count()
        context['active_schedules'] = WateringSchedule.objects.filter(
            zone__user=request.user, 
            is_active=True
        ).count()
        
        # Общее количество поливов
        total_waterings = WateringLog.objects.filter(zone__user=request.user).count()
        context['total_waterings'] = total_waterings
        
        # Общий расход воды
        total_water = WateringLog.objects.filter(zone__user=request.user).aggregate(
            total=Sum('water_used')
        )['total'] or 0
        context['total_water'] = round(total_water, 2)
    
    return render(request, 'main/home.html', context)


def register(request):
    """Регистрация нового пользователя"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Создаем профиль пользователя
            UserProfile.objects.create(user=user)
            # Создаем статус системы
            SystemStatus.objects.create(user=user)
            # Авторизуем пользователя
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно! Добро пожаловать!')
            return redirect('home')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'main/register.html', {'form': form})


def user_login(request):
    """Вход пользователя"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    
    return render(request, 'main/login.html')


def user_logout(request):
    """Выход пользователя"""
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы.')
    return redirect('home')


@login_required
def profile(request):
    """Профиль пользователя"""
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)
    
    return render(request, 'main/profile.html', {
        'form': form,
        'profile': user_profile
    })


@login_required
def dashboard(request):
    """Панель управления поливом"""
    zones = GardenZone.objects.filter(user=request.user).prefetch_related('schedules')
    
    # Статистика
    today = timezone.now().date()
    today_waterings = WateringLog.objects.filter(
        zone__user=request.user,
        started_at__date=today
    ).count()
    
    recent_logs = WateringLog.objects.filter(
        zone__user=request.user
    ).select_related('zone').order_by('-started_at')[:10]
    
    # Последние показания датчиков
    sensor_data = {}
    for zone in zones:
        latest_reading = SensorReading.objects.filter(zone=zone).order_by('-timestamp').first()
        if latest_reading:
            sensor_data[zone.id] = latest_reading
    
    context = {
        'zones': zones,
        'zones_count': zones.count(),
        'today_waterings': today_waterings,
        'recent_logs': recent_logs,
        'sensor_data': sensor_data,
    }
    
    return render(request, 'main/dashboard.html', context)


@login_required
def zone_create(request):
    """Создание новой зоны полива"""
    if request.method == 'POST':
        form = GardenZoneForm(request.POST)
        if form.is_valid():
            zone = form.save(commit=False)
            zone.user = request.user
            zone.save()
            messages.success(request, f'Зона "{zone.name}" успешно создана!')
            return redirect('dashboard')
    else:
        form = GardenZoneForm()
    
    return render(request, 'main/zone_form.html', {
        'form': form,
        'title': 'Создание новой зоны',
        'button_text': 'Создать'
    })


@login_required
def zone_edit(request, zone_id):
    """Редактирование зоны полива"""
    zone = get_object_or_404(GardenZone, id=zone_id, user=request.user)
    
    if request.method == 'POST':
        form = GardenZoneForm(request.POST, instance=zone)
        if form.is_valid():
            form.save()
            messages.success(request, f'Зона "{zone.name}" обновлена!')
            return redirect('dashboard')
    else:
        form = GardenZoneForm(instance=zone)
    
    return render(request, 'main/zone_form.html', {
        'form': form,
        'zone': zone,
        'title': 'Редактирование зоны',
        'button_text': 'Сохранить'
    })


@login_required
def zone_delete(request, zone_id):
    """Удаление зоны полива"""
    zone = get_object_or_404(GardenZone, id=zone_id, user=request.user)
    
    if request.method == 'POST':
        zone_name = zone.name
        zone.delete()
        messages.success(request, f'Зона "{zone_name}" удалена!')
        return redirect('dashboard')
    
    return render(request, 'main/zone_confirm_delete.html', {'zone': zone})


@login_required
def schedule_create(request, zone_id):
    """Создание расписания полива"""
    zone = get_object_or_404(GardenZone, id=zone_id, user=request.user)
    
    if request.method == 'POST':
        form = WateringScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.zone = zone
            schedule.save()
            messages.success(request, 'Расписание добавлено!')
            return redirect('dashboard')
    else:
        form = WateringScheduleForm()
    
    return render(request, 'main/schedule_form.html', {
        'form': form,
        'zone': zone,
        'title': 'Добавление расписания'
    })


@login_required
def schedule_delete(request, schedule_id):
    """Удаление расписания"""
    schedule = get_object_or_404(WateringSchedule, id=schedule_id, zone__user=request.user)
    
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, 'Расписание удалено!')
        return redirect('dashboard')
    
    return render(request, 'main/schedule_confirm_delete.html', {'schedule': schedule})


@login_required
def start_watering(request, zone_id):
    """Ручной запуск полива"""
    zone = get_object_or_404(GardenZone, id=zone_id, user=request.user)
    
    if request.method == 'POST':
        form = ManualWateringForm(request.POST)
        if form.is_valid():
            duration = form.cleaned_data['duration']
            # Создаем запись о поливе
            log = WateringLog.objects.create(
                zone=zone,
                duration=duration,
                is_manual=True,
                water_used=duration * 5  # Примерно 5 литров в минуту
            )
            
            # Обновляем общий расход воды
            system_status, _ = SystemStatus.objects.get_or_create(user=request.user)
            system_status.total_water_used += log.water_used
            system_status.save()
            
            messages.success(request, f'Полив зоны "{zone.name}" запущен на {duration} минут!')
            return redirect('dashboard')
    else:
        form = ManualWateringForm(initial={'duration': zone.watering_duration})
    
    return render(request, 'main/start_watering.html', {
        'form': form,
        'zone': zone
    })


@login_required
def watering_history(request):
    """История полива"""
    logs = WateringLog.objects.filter(
        zone__user=request.user
    ).select_related('zone').order_by('-started_at')
    
    # Фильтрация по зоне
    zone_filter = request.GET.get('zone')
    if zone_filter:
        logs = logs.filter(zone_id=zone_filter)
    
    zones = GardenZone.objects.filter(user=request.user)
    
    return render(request, 'main/watering_history.html', {
        'logs': logs,
        'zones': zones,
        'selected_zone': zone_filter
    })


@login_required
def api_zone_status(request, zone_id):
    """API для получения статуса зоны"""
    zone = get_object_or_404(GardenZone, id=zone_id, user=request.user)
    
    # Последнее показание датчика
    latest_reading = SensorReading.objects.filter(zone=zone).order_by('-timestamp').first()
    
    # Последний полив
    last_watering = WateringLog.objects.filter(zone=zone).order_by('-started_at').first()
    
    data = {
        'zone_id': zone.id,
        'zone_name': zone.name,
        'soil_moisture': latest_reading.soil_moisture if latest_reading else None,
        'temperature': float(latest_reading.temperature) if latest_reading and latest_reading.temperature else None,
        'humidity': latest_reading.humidity if latest_reading else None,
        'last_watering': last_watering.started_at.isoformat() if last_watering else None,
        'schedules_count': zone.schedules.filter(is_active=True).count(),
    }
    
    return JsonResponse(data)


@login_required
def api_toggle_schedule(request, schedule_id):
    """API для включения/выключения расписания"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    schedule = get_object_or_404(WateringSchedule, id=schedule_id, zone__user=request.user)
    schedule.is_active = not schedule.is_active
    schedule.save()
    
    return JsonResponse({
        'schedule_id': schedule.id,
        'is_active': schedule.is_active,
        'message': 'Расписание ' + ('включено' if schedule.is_active else 'выключено')
    })
