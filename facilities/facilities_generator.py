import random
import base64
import uuid
import os
import requests


locker_folder = "/home/luluma/AWS/capstone/jhb_2_cloud_capstone_project/facilities/images/lockers"
garage_forlder = "/home/luluma/AWS/capstone/jhb_2_cloud_capstone_project/facilities/images/garages"
storage_unit_folder = "/home/luluma/AWS/capstone/jhb_2_cloud_capstone_project/facilities/images/storage_units"
warehouse_folder = "/home/luluma/AWS/capstone/jhb_2_cloud_capstone_project/facilities/images/warehouses"

api_url = "https://b9mdnewkzk.execute-api.eu-west-1.amazonaws.com/prod/facilities"

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        return base64.b64encode(image_data).decode('utf-8')

""" Functions to generate random facilities with base64 image"""
def generate_facility_locker():
    locker_facility_name = random.choice([
    "SecureVault", "EasyStore Locker", "SafeKeep Locker", "QuickLock", 
    "The Locker Zone", "Locker Haven", "SwiftVault", "LockBox Express", 
    "SecureStash", "FlexiLock"
    ])
    location = random.choice([
    "Johannesburg", "Cape Town", "Durban", "Pretoria", "Port Elizabeth", 
    "Bloemfontein", "East London", "Polokwane", "Nelspruit", "Kimberley", 
    "Pietermaritzburg", "George", "Rustenburg", "Upington", "Vanderbijlpark",
    "Welkom", "Mthatha", "Kimberley", "Kuruman", "Ladysmith"
    ])
    facility_type = "Locker"
    capacity = random.randint(1, 100)  # Random capacity
    description = random.choice([
    "A secure and compact storage solution for small items.",
    "Perfect for storing personal belongings in a safe environment.",
    "Convenient, easy-access storage for your valuables.",
    "Durable and safe, ideal for keeping your items protected.",
    "The ultimate space-saving solution for busy lifestyles.",
    "A reliable option for storing your items with peace of mind.",
    "Weather-resistant and secure, ideal for sensitive items.",
    "Convenient and accessible storage for all your needs.",
    "Keep your valuables safe with top-notch security features."
    ])
    price = random.choice([50, 70, 90, 110, 130, 150, 170, 190, 210, 230] )

    # Get a random image from the folder
    random_image_filename = random.choice(os.listdir(locker_folder))
    random_image_path = os.path.join(locker_folder, random_image_filename)
    image_data = image_to_base64(random_image_path)

    facility = {
        'facility_name': locker_facility_name,
        'location': location,
        'type': facility_type,
        'capacity': capacity,
        'price': price,
        'description': description,
        'image': image_data  # base64 encoded image data
    }
    return facility


    
def generate_facility_garage():
    garage_facility_name = random.choice([
    "GarageXpress", "ParkEase Garage", "SecurePark", "CityGarage Hub", 
    "AutoSecure Garage", "ParkGuard Garage", "DriveSafe Garage", "UrbanPark Garage", 
    "SafePark Storage", "The Garage Spot"
    ])
    location = random.choice([
    "Johannesburg", "Cape Town", "Durban", "Pretoria", "Port Elizabeth", 
    "Bloemfontein", "East London", "Polokwane", "Nelspruit", "Kimberley", 
    "Pietermaritzburg", "George", "Rustenburg", "Upington", "Vanderbijlpark",
    "Welkom", "Mthatha", "Kimberley", "Kuruman", "Ladysmith"
    ])
    facility_type = "Garage"
    capacity = random.randint(1, 100)  # Random capacity
    description = random.choice([
    "Perfect for storing heavy machinery or industrial equipment.",
    "Convenient and secure parking for vehicles and equipment.",
    "Weather-proof and protected space for your vehicles.",
    "A spacious and safe garage for cars, bikes, and other vehicles.",
    "Ideal for DIY projects or workshop space with secure storage.",
    "A reliable, accessible space to keep your vehicles safe.",
    "Designed to accommodate vehicles and large equipment with ease.",
    "A multi-purpose garage for both storage and vehicle parking.",
    "Keep your vehicles and tools safe with 24/7 security features."
    ])
    price = random.choice([800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200, 1250] )

    # Get a random image from the folder
    random_image_filename = random.choice(os.listdir(garage_forlder))
    random_image_path = os.path.join(garage_forlder, random_image_filename)
    image_data = image_to_base64(random_image_path)

    facility = {
        'facility_name': garage_facility_name,
        'location': location,
        'type': facility_type,
        'capacity': capacity,
        'price': price,
        'description': description,
        'image': image_data  # base64 encoded image data
    }
    return facility



def generate_facility_storage_unit():
    storage_unit_facility_name = random.choice([
    "StorEase Unit", "The Storage Cube", "SpaceSaver Unit", "BoxedUp Storage", 
    "FlexiSpace Units", "StoreMore Unit", "VaultSafe Storage", "EasyStorage Unit", 
    "MaxSpace Unit", "StorPro Unit"
    ])
    location = random.choice([
    "Johannesburg", "Cape Town", "Durban", "Pretoria", "Port Elizabeth", 
    "Bloemfontein", "East London", "Polokwane", "Nelspruit", "Kimberley", 
    "Pietermaritzburg", "George", "Rustenburg", "Upington", "Vanderbijlpark",
    "Welkom", "Mthatha", "Kimberley", "Kuruman", "Ladysmith"
    ])
    facility_type = "Storage Unit"
    capacity = random.randint(1, 100)  # Random capacity
    description = random.choice([
    "Spacious, clean, and ideal for storing furniture or large items.",
    "Designed for maximum security and efficient use of space.",
    "A perfect place for your seasonal items or business equipment.",
    "Store your items safely with our flexible and customizable units.",
    "Protect your belongings with our state-of-the-art locking mechanisms.",
    "A space-efficient storage option that ensures protection.",
    "Store everything from household goods to large equipment with ease.",
    "Safe, clean, and spacious, designed to keep your items organized.",
    "A premium storage solution for both personal and business needs."
    ])
    price = random.choice([300, 350, 400, 450, 500, 550, 600, 650, 700, 750])

    # Get a random image from the folder
    random_image_filename = random.choice(os.listdir(storage_unit_folder))
    random_image_path = os.path.join(storage_unit_folder, random_image_filename)
    image_data = image_to_base64(random_image_path)

    facility = {
        'facility_name': storage_unit_facility_name,
        'location': location,
        'type': facility_type,
        'capacity': capacity,
        'price': price,
        'description': description,
        'image': image_data  # base64 encoded image data
    }
    return facility


def generate_facility_warehouse():
    warehouse_facility_name = random.choice([
    "MegaStorage Warehouse", "ProStore Warehouse", "SecureStock Warehouse", 
    "VaultSpace Warehouse", "RapidStore Warehouse", "The Warehouse Hub", 
    "FlexiStore Warehouse", "StockPoint Warehouse", "MaxiStor Warehouse", 
    "SupplyHub Warehouse"
    ])

    location = random.choice([
    "Johannesburg", "Cape Town", "Durban", "Pretoria", "Port Elizabeth", 
    "Bloemfontein", "East London", "Polokwane", "Nelspruit", "Kimberley", 
    "Pietermaritzburg", "George", "Rustenburg", "Upington", "Vanderbijlpark",
    "Welkom", "Mthatha", "Kimberley", "Kuruman", "Ladysmith"
    ])
    facility_type = "Warehouse"
    capacity = random.randint(1, 100)  # Random capacity
    description = random.choice([
    "A large-scale storage solution for business and industrial needs.",
    "Perfect for storing bulk inventory and large shipments.",
    "A high-security warehouse for storing sensitive goods.",
    "Designed for efficient organization and easy access to stock.",
    "Secure, weather-resistant, and perfect for long-term storage.",
    "A spacious warehouse equipped for large-scale logistics.",
    "Ideal for storing products, materials, or large machinery.",
    "Maximize your storage capacity with this flexible warehouse space.",
    "A robust warehouse with advanced security and monitoring systems.",
    "Efficient storage and distribution space for businesses of all sizes."
    ]) # Random description
    price = random.choice([1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400])

    # Get a random image from the folder
    random_image_filename = random.choice(os.listdir(warehouse_folder))
    random_image_path = os.path.join(warehouse_folder, random_image_filename)
    image_data = image_to_base64(random_image_path)

    facility = {
        'facility_name': warehouse_facility_name,
        'location': location,
        'type': facility_type,
        'capacity': capacity,
        'price': price,
        'description': description,
        'image': image_data  # base64 encoded image data
    }
    return facility

for _ in range(10):  # Create 5 random facilities
    locker_facility = generate_facility_locker()
    garage_facility = generate_facility_garage()
    storage_facility = generate_facility_storage_unit()
    warehouse_facility = generate_facility_warehouse()

    # Send each facility as a POST request
    for facility in [locker_facility, garage_facility, storage_facility, warehouse_facility]:
        response = requests.post(api_url, json=facility)
        if response.status_code == 201:  # Assuming 201 Created is the success code
            print(f"Successfully created facility: {facility['facility_name']}")
        else:
            print(f"Failed to create facility: {facility['facility_name']}, Error: {response.text}")



