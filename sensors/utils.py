import hmac
import hashlib
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from .models import Alert, ActivityLog


def sign_data(value, timestamp):
    """Podpisuje dane HMAC"""
    message = f"{value}-{timestamp}".encode('utf-8')
    secret = settings.SENSOR_DATA_SECRET.encode('utf-8')
    signature = hmac.new(secret, message, digestmod=hashlib.sha256).hexdigest()
    return signature


def verify_signature(value, timestamp, signature):
    """Weryfikuje podpis HMAC"""
    expected = sign_data(value, timestamp)
    return hmac.compare_digest(expected, signature)


def calculate_reactive_power(power, pf):
    """
    Oblicza moc bierną Q [VAR] na podstawie mocy czynnej P i współczynnika mocy PF

    Q = sqrt(S² - P²)
    gdzie S = P / PF (moc pozorna)
    """
    if pf == 0 or power == 0:
        return 0
    try:
        S = power / pf  # Moc pozorna [VA]
        Q = (S ** 2 - power ** 2) ** 0.5  # Moc bierna [VAR]
        return round(Q, 2)
    except:
        return 0


def check_alerts(sensor, sensor_data):
    """
    Sprawdza czy należy utworzyć alert dla danego pomiaru
    """
    from datetime import timedelta

    alerts_created = []

    # 1. Alert przekroczenia mocy
    if sensor.power_threshold and sensor_data.power:
        if sensor_data.power > sensor.power_threshold:
            # Sprawdź czy nie było już alertu w ostatnich 10 minutach
            recent_alert = Alert.objects.filter(
                sensor=sensor,
                alert_type='power_high',
                created_at__gte=timezone.now() - timedelta(minutes=10)
            ).exists()

            if not recent_alert:
                alert = Alert.objects.create(
                    house=sensor.house,
                    sensor=sensor,
                    alert_type='power_high',
                    severity='warning',
                    message=f"Czujnik '{sensor.name}' przekroczył próg mocy!",
                    value=sensor_data.power,
                    threshold=sensor.power_threshold
                )
                alerts_created.append(alert)

    # 2. Alert limitu miesięcznego
    if sensor.house.monthly_limit_kwh:
        from django.db.models import Sum
        start_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Oblicz zużycie w miesiącu
        monthly_energy = 0
        for s in sensor.house.sensors.all():
            data_list = list(s.data.filter(timestamp__gte=start_of_month).order_by('timestamp'))
            if len(data_list) > 1:
                for i in range(1, len(data_list)):
                    dt = (data_list[i].timestamp - data_list[i - 1].timestamp).total_seconds()
                    power = float(data_list[i].power) if data_list[i].power else 0
                    monthly_energy += power * dt / 3600000.0  # kWh

        if monthly_energy > sensor.house.monthly_limit_kwh:
            # Sprawdź czy nie było już alertu dziś
            recent_alert = Alert.objects.filter(
                house=sensor.house,
                alert_type='monthly_limit',
                created_at__gte=timezone.now().replace(hour=0, minute=0, second=0)
            ).exists()

            if not recent_alert:
                alert = Alert.objects.create(
                    house=sensor.house,
                    sensor=None,
                    alert_type='monthly_limit',
                    severity='critical',
                    message=f"Dom '{sensor.house.name}' przekroczył miesięczny limit zużycia!",
                    value=monthly_energy,
                    threshold=sensor.house.monthly_limit_kwh
                )
                alerts_created.append(alert)

    # Wyślij email jeśli są nowe alerty
    if alerts_created:
        send_alert_email(alerts_created)

    return alerts_created


def send_alert_email(alerts):
    """
    Wysyła email z alertami
    """
    if not alerts:
        return

    house = alerts[0].house
    email = house.alert_email or house.user.email

    if not email:
        return

    subject = f"⚠️ Alerty - {house.name}"

    message_lines = [
        f"Witaj {house.user.username},",
        "",
        f"Mamy nowe alerty dla domu '{house.name}':",
        ""
    ]

    for alert in alerts:
        message_lines.append(f"• {alert.get_severity_display()}: {alert.message}")
        if alert.value and alert.threshold:
            message_lines.append(f"  Wartość: {alert.value:.1f}, Próg: {alert.threshold:.1f}")
        message_lines.append("")

    message_lines.extend([
        "Zaloguj się do systemu aby zobaczyć szczegóły.",
        "",
        "---",
        "Energy Monitor System"
    ])

    message = "\n".join(message_lines)

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=True,
        )
        # Oznacz alerty jako wysłane
        for alert in alerts:
            alert.email_sent = True
            alert.save(update_fields=['email_sent'])
    except Exception as e:
        print(f"Błąd wysyłania emaila: {e}")


def log_activity(user, action, model_name, object_id, description, request=None):
    """
    Loguje aktywność użytkownika
    """
    ip_address = None
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')

    ActivityLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=object_id,
        description=description,
        ip_address=ip_address
    )


def get_comparison_data(house, period='month'):
    """
    Porównuje zużycie energii między okresami

    period: 'day', 'week', 'month'
    """
    from datetime import timedelta
    from django.db.models import Avg, Sum

    now = timezone.now()

    if period == 'day':
        current_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        previous_start = current_start - timedelta(days=1)
        previous_end = current_start
    elif period == 'week':
        current_start = now - timedelta(days=now.weekday())
        current_start = current_start.replace(hour=0, minute=0, second=0, microsecond=0)
        previous_start = current_start - timedelta(weeks=1)
        previous_end = current_start
    else:  # month
        current_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 1:
            previous_start = now.replace(year=now.year - 1, month=12, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            previous_start = now.replace(month=now.month - 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        previous_end = current_start

    # Oblicz zużycie dla bieżącego okresu
    current_kwh = calculate_energy_for_period(house, current_start, now)

    # Oblicz zużycie dla poprzedniego okresu
    previous_kwh = calculate_energy_for_period(house, previous_start, previous_end)

    # Oblicz różnicę
    if previous_kwh > 0:
        change_percent = ((current_kwh - previous_kwh) / previous_kwh) * 100
    else:
        change_percent = 0

    return {
        'current': current_kwh,
        'previous': previous_kwh,
        'change_percent': change_percent,
        'change_absolute': current_kwh - previous_kwh
    }


def calculate_energy_for_period(house, start_time, end_time):
    """
    Oblicza całkowitą energię dla domu w danym okresie
    """
    from .models import SensorData

    total_kwh = 0

    for sensor in house.sensors.all():
        data_list = list(
            SensorData.objects.filter(
                sensor=sensor,
                timestamp__gte=start_time,
                timestamp__lte=end_time
            ).order_by('timestamp')
        )

        if len(data_list) > 1:
            for i in range(1, len(data_list)):
                dt = (data_list[i].timestamp - data_list[i - 1].timestamp).total_seconds()
                power = float(data_list[i].power) if data_list[i].power else 0
                total_kwh += power * dt / 3600000.0  # kWh

    return total_kwh


def predict_monthly_cost(house):
    """
    Przewiduje koszt na koniec miesiąca na podstawie dotychczasowego zużycia
    """
    from datetime import datetime

    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Ile dni minęło w miesiącu
    days_passed = (now - start_of_month).days + 1

    # Ile dni w miesiącu
    if now.month == 12:
        next_month = now.replace(year=now.year + 1, month=1, day=1)
    else:
        next_month = now.replace(month=now.month + 1, day=1)
    days_in_month = (next_month - start_of_month).days

    # Zużycie do tej pory
    current_kwh = calculate_energy_for_period(house, start_of_month, now)

    # Przewidywane zużycie na koniec miesiąca
    if days_passed > 0:
        daily_avg = current_kwh / days_passed
        predicted_kwh = daily_avg * days_in_month
        predicted_cost = predicted_kwh * house.price_per_kwh
    else:
        predicted_kwh = 0
        predicted_cost = 0

    return {
        'current_kwh': current_kwh,
        'predicted_kwh': predicted_kwh,
        'predicted_cost': predicted_cost,
        'days_passed': days_passed,
        'days_remaining': days_in_month - days_passed,
        'daily_average': current_kwh / days_passed if days_passed > 0 else 0
    }
