from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from io import BytesIO
from .models import Drone, Medication

class DroneLoadingTests(APITestCase):
    def setUp(self):
        """
        Create test drones with different states and battery levels
        """
        
        # A drone that should work for loading
        self.valid_drone = Drone.objects.create(
            serial_number="w23j5JK23",
            model="LIGHT",
            weight_limit=300,
            battery_capacity=80,
            state="LOADING"
        )
        
        # Drone with low battery - should fail loading
        self.low_battery_drone = Drone.objects.create(
            serial_number="jr8NkL925",
            model="LIGHT", 
            weight_limit=300,
            battery_capacity=20,
            state="LOADING"
        )
        
        # Drone in wrong state - should fail loading
        self.wrong_state_drone = Drone.objects.create(
            serial_number="KJ23j5w23",
            model="LIGHT",
            weight_limit=300,
            battery_capacity=80,
            state="DELIVERING"
        )
        
        # Small drone with low weight limit
        self.small_drone = Drone.objects.create(
            serial_number="s23j5JK24",
            model="LIGHT",
            weight_limit=100,
            battery_capacity=80,
            state="LOADING"
        )
        
        # Available drone for loading
        self.available_drone = Drone.objects.create(
            serial_number="a23j5JK25",
            model="HEAVY",
            weight_limit=500,
            battery_capacity=90,
            state="IDLE"
        )

    def create_test_image(self, filename="test.jpg"):
        """
        Create a simple test image for medication testing
        """

        image = Image.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        image.save(buffer, format='JPEG')
        buffer.seek(0)
        
        return SimpleUploadedFile(
            filename,
            buffer.getvalue(),
            content_type="image/jpeg"
        )

    def test_low_battery_drone_cannot_be_loaded(self):
        """
        Drones with less than 25% battery should be blocked from loading
        """
        url = reverse('load-drone', kwargs={'drone_id': self.low_battery_drone.id})
        
        medication_data = {
            "name": "Aspirin",
            "weight": 50,
            "code": "ASP_001",
            "image": self.create_test_image("aspirin.jpg")
        }
        
        response = self.client.post(url, medication_data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('battery', response.data['error'].lower())
        self.assertIn('25', response.data['error'])

    def test_wrong_state_drone_cannot_be_loaded(self):
        """
        Only drones in LOADING state can accept medications
        """
        url = reverse('load-drone', kwargs={'drone_id': self.wrong_state_drone.id})
        
        medication_data = {
            "name": "Aspirin",
            "weight": 50,
            "code": "ASP_001",
            "image": self.create_test_image("aspirin.jpg")
        }
        
        response = self.client.post(url, medication_data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('loading', response.data['error'].lower())
        self.assertIn('state', response.data['error'].lower())

    def test_drone_cannot_exceed_weight_limit(self):
        """
        Drones should reject medications that exceed their weight capacity
        """
        url = reverse('load-drone', kwargs={'drone_id': self.small_drone.id})
        
        medication_data = {
            "name": "Bandage",
            "weight": 150, 
            "code": "BAND_001", 
            "image": self.create_test_image("bandage.jpg")
        }
        
        response = self.client.post(url, medication_data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('weight', response.data['error'].lower())
        self.assertIn('exceed', response.data['error'].lower())

    def test_valid_loading_operation(self):
        """
        Successful medication loading should create medications and update drone state
        """
        url = reverse('load-drone', kwargs={'drone_id': self.valid_drone.id})
        
        medication_data = {
            "name": "Aspirin",
            "weight": 50,
            "code": "ASP_001",
            "image": self.create_test_image("aspirin.jpg")
        }
        
        response = self.client.post(url, medication_data, format='multipart')
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('successfully', response.data['message'].lower())
        self.assertEqual(response.data['total_weight'], 50)
        
        # Verify medication was created in database
        self.assertEqual(Medication.objects.count(), 1)
        self.assertEqual(Medication.objects.first().name, 'Aspirin')
        
        # Verify drone state changed to LOADED
        self.valid_drone.refresh_from_db()
        self.assertEqual(self.valid_drone.state, 'LOADED')

    def test_available_drones_filter_correctly(self):
        """
        Available drones endpoint should only show IDLE/LOADING drones with sufficient battery
        """
        url = reverse('available-drones')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Get serial numbers of returned drones
        available_serials = [drone['serial_number'] for drone in response.data]
        
        # Should include drones with good battery and correct state
        self.assertIn(self.valid_drone.serial_number, available_serials)
        self.assertIn(self.available_drone.serial_number, available_serials)
        
        # Should exclude drones with low battery or wrong state
        self.assertNotIn(self.low_battery_drone.serial_number, available_serials)
        self.assertNotIn(self.wrong_state_drone.serial_number, available_serials)

    def test_medication_validation(self):
        """
        Medication names and codes should follow specific format rules
        """
        url = reverse('load-drone', kwargs={'drone_id': self.valid_drone.id})
        
        invalid_medication = {
            "name": "Invalid@Med",  # Contains invalid character @
            "weight": 50,
            "code": "invalid-code",  # Lowercase instead of uppercase
            "image": self.create_test_image("test.jpg")
        }
        
        response = self.client.post(url, invalid_medication, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Should return validation errors for both name and code
        self.assertIn('name', response.data)
        self.assertIn('code', response.data)