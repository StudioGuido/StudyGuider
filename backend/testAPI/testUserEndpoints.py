import requests
import time

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
    """POST /api/createUser — JWT only; persists supabase_uid (no username body)."""
    url = "http://0.0.0.0:8000/api/createUser"

    response = requests.post(
        url=url,
        json={},
        headers={"Content-Type": "application/json", **AUTH_HEADERS},
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body.get("response", {}).get("supabase_uid"), body

    print("CREATED USER")
    print(response.json())


def testUserDeletion():
    url = "http://0.0.0.0:8000/api/users/me"

    response = requests.delete(url, headers=AUTH_HEADERS)

    assert response.status_code in (200, 404), response.text

    print("DELETED USER")
    print(response.json())


test_no = 2

match test_no:

    case 0:
        print("No Tests Ran")

    case 1:
        """
        Test 1: Basic user creation (supabase_uid only):
        """
        testUserCreation()
        
    case 2:
        """
        Test 2: Delete user:
        """
        testUserDeletion()

    case 3:
        """
        Test 3: Create then delete:
        """
        testUserCreation()
        time.sleep(5)
        testUserDeletion()
