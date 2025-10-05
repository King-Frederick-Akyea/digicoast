# Drone Fleet Management API

A Django REST Framework API for managing drone deliveries of medications to remote areas. This system handles drone fleet management, medication tracking, and enforces business rules for safe operations.

## Features

- Drone registration and management
- Medication loading and tracking
- Battery level monitoring
- Available drones listing
- Business rule enforcement
- Weight limit validation
- Battery level checks

## Technologies

- Django 
- Django REST Framework
- postgresql database
- Pillow for image handling

## Installation

1. Create virtual environment. Use:
pipenv shell

2. Install dependencies:
pip install -r requirements.txt

3. Create .env file and use the format in the example.env file 

3. Setup database:
python manage.py makemigrations
python manage.py migrate

4. Create admin user (optional): 
python manage.py createsuperuser

5. Run server:
python manage.py runserver

API available at: http://127.0.0.1:8000/

## API Endpoints

Register Drone
POST /api/drones/

{
    "serial_number": "DRONE_001",
    "model": "LIGHT",
    "weight_limit": 300,
    "battery_capacity": 100,
    "state": "IDLE"
}

Load Medications
POST /api/drones/{id}/load/

{
    "name": "Aspirin",
    "weight": 50,
    "code": "ASP_001",
    "image": "aspirin.jpg"
}

Check Medications
GET /api/drones/{id}/medications/

Available Drones
GET /api/drones/available/

Check Battery
GET /api/drones/{id}/battery/

## Business Rules

* Drones can only be loaded in LOADING state
* Battery level must be 25% or higher for loading
* Total medication weight cannot exceed drone weight limit (500g max)
* Medication names: letters, numbers, hyphens, underscores only
* Medication codes: uppercase letters, numbers, underscores only

## Models

### Drone
serial_number (unique, max 100 chars)
model: Lightweight, Middleweight, Cruiserweight, Heavyweight
weight_limit (max 500g)
battery_capacity (0-100%)
state: IDLE, LOADING, LOADED, DELIVERING, DELIVERED, RETURNING

### Medication
name (validated format)
weight (in grams)
code (validated format, unique)
image
drone (foreign key)

## Testing
Run the test suite:

python manage.py test

Test with Postman or Thunder Client by hitting the endpoints with sample data.

## Project Structure
digicoast/
├── digicoast/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── drone/ (main app)
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
└── media
└── example.env
└── manage.py
└── Pipfile
└── Pipfile.lock
└── README.md
└── requirements.txt

## Error Handling
The API returns descriptive error messages for:

* Validation errors (400)
* Object not found (404)
* Business rule violations (400)
* Server errors (500)



This documentation covers all the essential information needed to understand, install, and use the Drone Fleet Management API while maintaining a professional and clean appearance.