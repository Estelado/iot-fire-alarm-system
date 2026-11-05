from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import SensorData
import json

def index(request):
    """Главная страница."""
    return render(request, 'data/index.html')

def alerts(request):
    """Страница истории тревог."""
    alerts_list = SensorData.objects.filter(fire_alert=True).order_by('-timestamp')
    # Добавляем максимальный сигнал для отображения на странице
    for alert in alerts_list:
        max_signal = alert.channel_a1 or 0
        if alert.channel_a3 and alert.channel_a3 > max_signal:
            max_signal = alert.channel_a3
        if alert.channel_a5 and alert.channel_a5 > max_signal:
            max_signal = alert.channel_a5
        alert.max_signal = max_signal
    return render(request, 'data/alerts.html', {'alerts': alerts_list})

@csrf_exempt
def api_data(request):
    """Приём телеметрии от датчика (POST)."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            SensorData.objects.create(
                device_id=data.get('device_id', 1),
                temperature=data.get('temperature', 22.5),
                battery_voltage=data.get('battery_voltage', 3.85),
                fire_alert=data.get('fire_alert', False),
                channel_a1=data.get('channel_a1', 0),
                channel_a3=data.get('channel_a3', 0),
                channel_a5=data.get('channel_a5', 0),
                direction=data.get('direction', 'none'),
            )
            return JsonResponse({'status': 'ok'}, status=201)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Only POST method allowed'}, status=405)

def api_latest(request):
    """Возвращает последнюю запись для динамического обновления главной."""
    last = SensorData.objects.filter(device_id=1).first()
    result = []
    if last:
        delta = timezone.now() - last.timestamp
        is_online = delta.total_seconds() < 60 # Считаем онлайн, если данные пришли менее минуты назад
        
        max_signal = last.channel_a1 or 0
        if last.channel_a3 and last.channel_a3 > max_signal:
            max_signal = last.channel_a3
        if last.channel_a5 and last.channel_a5 > max_signal:
            max_signal = last.channel_a5
            
        result.append({
            'device_id': last.device_id,
            'fire_alert': last.fire_alert,
            'channel_a1': last.channel_a1,
            'channel_a3': last.channel_a3,
            'channel_a5': last.channel_a5,
            'max_signal': max_signal,
            'is_online': is_online,
            'timestamp': timezone.localtime(last.timestamp).strftime('%d.%m.%Y %H:%M:%S'),
        })
    return JsonResponse(result, safe=False)
