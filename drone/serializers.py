from .models import Drone, Medication
from rest_framework import serializers

class DroneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drone
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'drone')


    def validate_name(self, value):
        if not all(char.isalnum() or char in ('-', '_') for char in value):
            raise serializers.ValidationError("Name can only contain letters, numbers, '-', and '_'")
        return value
        
    def validate_code(self, value):
        if not all(char.isupper() or char.isdigit() or char == '_' for char in value):
            raise serializers.ValidationError("Code can only contain uppercase letters, numbers, and '_'")
        return value