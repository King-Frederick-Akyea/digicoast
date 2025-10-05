from django.db import models
from django.core.validators import MaxValueValidator


class Drone(models.Model):
    Model_choices = [
        ('LIGHT', 'Lightweight'),
        ('MIDDLE', 'Middleweight'),
        ('CRUISER', 'Cruiserweight'),
        ('HEAVY', 'Heavyweight'),
    ]

    Drone_states = [
        ('IDLE', 'Idle'),
        ('LOADING', 'Loading'),
        ('LOADED', 'Loaded'),
        ('DELIVERING', 'Delivering'),
        ('DELIVERED', 'Delivered'),
        ('RETURNING', 'Returning'),
    ]

    id = models.AutoField(primary_key=True)
    serial_number = models.CharField(max_length=100, unique=True)
    model = models.CharField(max_length=20, choices=Model_choices)
    weight_limit = models.IntegerField(validators=[MaxValueValidator(500)])
    battery_capacity = models.IntegerField(validators=[MaxValueValidator(100)])
    state = models.CharField(max_length=20, choices=Drone_states, default='IDLE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.serial_number
    
class Medication(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    weight = models.IntegerField()
    code = models.CharField(max_length=200, unique=True)
    image = models.ImageField(upload_to='medications/')
    drone = models.ForeignKey(Drone, related_name='medications', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
