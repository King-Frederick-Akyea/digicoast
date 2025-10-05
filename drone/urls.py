from django.urls import path
from .views import AvailableDronesView, DroneRegisterView, DroneBatteryView, DroneMedicationView, DroneLoadView

urlpatterns = [
    path('drones/register/', DroneRegisterView.as_view(), name='register-drone'),
    path('drones/<int:pk>/battery/', DroneBatteryView.as_view(), name='drone-battery'),
    path('drones/<int:pk>/medications/', DroneMedicationView.as_view(), name='drone-medications'),
    path('drones/available/', AvailableDronesView.as_view(), name='available-drones'),
    path('drones/<int:drone_id>/load/', DroneLoadView.as_view(), name='load-drone'),
]