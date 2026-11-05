from django.db import models

class SensorData(models.Model):
    device_id = models.IntegerField(verbose_name="ID датчика")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Время получения")
    temperature = models.FloatField(null=True, blank=True, verbose_name="Температура, °С")
    battery_voltage = models.FloatField(verbose_name="Напряжение аккумулятора, В")
    fire_alert = models.BooleanField(default=False, verbose_name="Тревога (пожар)")
    low_battery = models.BooleanField(default=False, verbose_name="Низкий заряд батареи")
    alert_counter = models.IntegerField(default=0, verbose_name="Счётчик тревог")
    
    channel_a1 = models.IntegerField(default=0, verbose_name="Левый датчик (АЦП)")
    channel_a3 = models.IntegerField(default=0, verbose_name="Центральный датчик (АЦП)")
    channel_a5 = models.IntegerField(default=0, verbose_name="Правый датчик (АЦП)")
    direction = models.CharField(max_length=100, default='none', verbose_name="Направление")

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Показание датчика"
        verbose_name_plural = "Показания датчиков"

    def __str__(self):
        return f"Датчик #{self.device_id} | {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
