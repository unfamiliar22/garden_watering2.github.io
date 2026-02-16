from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, GardenZone, WateringSchedule


class UserRegistrationForm(UserCreationForm):
    """Форма регистрации пользователя"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите email'
    }))
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите имя'
    }))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите фамилию'
    }))
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Придумайте логин'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Придумайте пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Повторите пароль'
        })


class UserProfileForm(forms.ModelForm):
    """Форма профиля пользователя"""
    class Meta:
        model = UserProfile
        fields = ['phone', 'address']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 999-99-99'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Адрес вашего участка'
            }),
        }


class GardenZoneForm(forms.ModelForm):
    """Форма создания/редактирования зоны сада"""
    class Meta:
        model = GardenZone
        fields = ['name', 'description', 'plant_type', 'area_size', 'watering_duration', 'watering_frequency']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Огуречная грядка'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Описание зоны'
            }),
            'plant_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Огурцы, помидоры'
            }),
            'area_size': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Площадь в м²',
                'step': '0.01'
            }),
            'watering_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Минут',
                'min': '1',
                'max': '120'
            }),
            'watering_frequency': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Раз в день',
                'min': '1',
                'max': '5'
            }),
        }


class WateringScheduleForm(forms.ModelForm):
    """Форма расписания полива"""
    days_choices = [
        (1, 'Пн'),
        (2, 'Вт'),
        (3, 'Ср'),
        (4, 'Чт'),
        (5, 'Пт'),
        (6, 'Сб'),
        (7, 'Вс'),
    ]
    
    days = forms.MultipleChoiceField(
        choices=days_choices,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='Дни недели'
    )
    
    class Meta:
        model = WateringSchedule
        fields = ['time', 'is_active']
        widgets = {
            'time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['days'].initial = self.instance.get_days_list()
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.set_days_list(self.cleaned_data['days'])
        if commit:
            instance.save()
        return instance


class ManualWateringForm(forms.Form):
    """Форма ручного запуска полива"""
    duration = forms.IntegerField(
        min_value=1,
        max_value=60,
        initial=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Минут'
        }),
        label='Длительность полива (минут)'
    )
