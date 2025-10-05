from .models import Drone, Medication
from .serializers import DroneSerializer, MedicationSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

class DroneRegisterView(APIView):
    """
    Register a new drone
    """

    def post(self, request):
        serializer = DroneSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DroneBatteryView(APIView):
    """
    Get the battery level of a drone by its ID
    """
    def get(self, request, pk):
        drone = get_object_or_404(Drone, pk=pk)
        return Response({
            "serial_number": drone.serial_number,
            "battery_level": str(drone.battery_capacity) + "%"
            }, status=status.HTTP_200_OK)
    
class DroneMedicationView(APIView):
    """
    Get the list of medications loaded on a drone by its ID
    """
    def get(self, request, pk):
        drone = get_object_or_404(Drone, pk=pk)
        medications = drone.medications.all()
        serializer = MedicationSerializer(medications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class AvailableDronesView(APIView):
    """
    Get the list of available drones for loading
    """
    def get(self, request):
        drones = Drone.objects.filter(state__in=['IDLE', 'LOADING'], battery_capacity__gte=25)
        serializer = DroneSerializer(drones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class DroneLoadView(APIView):
    """
    Load medications onto a drone
    """
    
    def post(self, request, drone_id):
        drone = get_object_or_404(Drone, id=drone_id)
        
        # Check state
        if drone.state != 'LOADING':
            return Response(
                {"error": "Drone must be in LOADING state to load medications"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check battery
        if drone.battery_capacity < 25:
            return Response(
                {"error": f"Battery level {drone.battery_capacity}% is too low. Minimum 25% required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate current weight
        existing_medications = drone.medications.all()
        current_weight = sum(med.weight for med in existing_medications)
        
        # Handle both single medication and list of medications
        medications_data = request.data
        if isinstance(medications_data, dict):
            medications_data = [medications_data]
        elif not isinstance(medications_data, list):
            return Response(
                {"error": "Expected a medication object or list of medications"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate new weight and validate medications
        new_medications_weight = 0
        for med_data in medications_data:
            weight_str = med_data.get('weight', 0)
            try:
                weight_int = int(weight_str)
                new_medications_weight += weight_int
            except (ValueError, TypeError):
                return Response(
                    {"error": f"Invalid weight value: {weight_str}. Weight must be a number."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        total_weight = current_weight + new_medications_weight
        
        # Check weight limit
        if total_weight > drone.weight_limit:
            return Response(
                {"error": f"Total weight {total_weight}g exceeds drone limit of {drone.weight_limit}g"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create medications
        created_medications = []
        for med_data in medications_data:
            med_data['weight'] = int(med_data.get('weight', 0))
            
            serializer = MedicationSerializer(data=med_data)
            if serializer.is_valid():
                medication = serializer.save(drone=drone)
                created_medications.append(medication)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Update drone state
        drone.state = 'LOADED'
        drone.save()

        # Return success response
        output_serializer = MedicationSerializer(created_medications, many=True)
        return Response({
            "message": f"Successfully loaded {len(created_medications)} medications",
            "total_weight": total_weight,
            "medications": output_serializer.data
        }, status=status.HTTP_201_CREATED)