// Основной JavaScript для сайта умного полива

document.addEventListener('DOMContentLoaded', function() {
    // Автоматическое скрытие алертов через 5 секунд
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });

    // Подтверждение удаления
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Вы уверены?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Анимация карточек при скролле
    const cards = document.querySelectorAll('.card');
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const cardObserver = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    cards.forEach(function(card) {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        cardObserver.observe(card);
    });

    // Тултипы для кнопок
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Поповеры
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Функция для переключения расписания через API
function toggleSchedule(scheduleId) {
    fetch(`/api/schedule/${scheduleId}/toggle/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            showNotification(data.message, 'success');
            // Обновляем внешний вид кнопки
            const badge = document.querySelector(`#schedule-badge-${scheduleId}`);
            if (badge) {
                badge.className = `badge ${data.is_active ? 'bg-success' : 'bg-secondary'}`;
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Ошибка при переключении расписания', 'error');
    });
}

// Функция для получения CSRF токена
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Функция для показа уведомлений
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(notification);

    setTimeout(() => {
        const closeButton = notification.querySelector('.btn-close');
        if (closeButton) {
            closeButton.click();
        }
    }, 5000);
}

// Функция для обновления статуса зоны
function updateZoneStatus(zoneId) {
    fetch(`/api/zone/${zoneId}/status/`)
        .then(response => response.json())
        .then(data => {
            // Обновляем показания датчиков на странице
            const moistureElement = document.querySelector(`#moisture-${zoneId}`);
            const tempElement = document.querySelector(`#temp-${zoneId}`);
            const humidityElement = document.querySelector(`#humidity-${zoneId}`);

            if (moistureElement && data.soil_moisture !== null) {
                moistureElement.textContent = `${data.soil_moisture}%`;
            }
            if (tempElement && data.temperature !== null) {
                tempElement.textContent = `${data.temperature}°C`;
            }
            if (humidityElement && data.humidity !== null) {
                humidityElement.textContent = `${data.humidity}%`;
            }
        })
        .catch(error => console.error('Error updating zone status:', error));
}

// Функция для запуска полива
function startWatering(zoneId, duration) {
    fetch(`/zone/${zoneId}/water/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `duration=${duration}`
    })
    .then(response => {
        if (response.ok) {
            showNotification('Полив успешно запущен!', 'success');
            // Перезагружаем страницу через 2 секунды
            setTimeout(() => location.reload(), 2000);
        } else {
            showNotification('Ошибка при запуске полива', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Ошибка при запуске полива', 'danger');
    });
}

// Валидация форм
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('is-invalid');
        } else {
            field.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Добавляем валидацию ко всем формам
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
        if (!validateForm(this)) {
            e.preventDefault();
            showNotification('Пожалуйста, заполните все обязательные поля', 'warning');
        }
    });
});
