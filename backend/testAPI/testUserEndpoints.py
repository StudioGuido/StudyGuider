import os
import requests
import asyncio
import time
from pathlib import Path

# from dotenv import load_dotenv

# # Load .env from backend dir and project root so test uses same config as backend
# _backend_dir = Path(__file__).resolve().parent.parent
# _project_root = _backend_dir.parent
# load_dotenv(_backend_dir / ".env")
# load_dotenv(_project_root / ".env")

SUPABASE_URL = "https://bafblcxwhdvikgcpcnds.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_EHbCfU3Xd5oku8EZZTLD7g_1bxWBYnC"

EMAIL = "test@gmail.com"
PASSWORD = "testpass123"


def get_jwt():
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"

    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
    }

    json = {
        "email": EMAIL,
        "password": PASSWORD,
    }

    response = requests.post(url, headers=headers, json=json)

    if response.status_code != 200:
        print("Login failed:", response.text)
        exit()

    return response.json()["access_token"]


TOKEN = get_jwt()

AUTH_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}",
}


def testUserCreation():
    url = "http://0.0.0.0:8000/api/createUser"

    response = requests.post(
        url=url,
        headers={"Content-Type": "application/json", **AUTH_HEADERS},
    )

    print("CREATED USER")
    print(response.json())


def testUserDeletion():
    url = "http://0.0.0.0:8000/api/users/me"

    response = requests.delete(url, headers=AUTH_HEADERS)

    print("DELETED USER")
    print(response.json())


test_no = 0
match test_no:
    case 0:
        """
        Test 1: Basic User creation:
        """
        testUserCreation()
    case 1:
        """
        Test 2: Basic User deletion:
        """
        testUserDeletion()
    case 2:
        """
        Test 3: Creation+Deletion combined:
        """
        testUserCreation()
        time.sleep(10)  
        testUserDeletion()
