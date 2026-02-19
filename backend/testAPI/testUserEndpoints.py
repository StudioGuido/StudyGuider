import requests
import asyncio
import time

# Updates for Username/email + Set Titles
# Logging and monitoring?


def testUserCreation():
    url = "http://0.0.0.0:8000/api/createUser"

    headers = {"Content-Type": "application/json"}

    json = {
        "username": "pierce",
        "email": "pwex@gmail.com",
    }
    response = requests.post(url=url, json=json, headers=headers)
    print("CREATED USER")
    print(response.json())


def testUserDeletion():
    email = "pwex@gmail.com"
    url = f"http://0.0.0.0:8000/api/deleteUser/{email}"

    response = requests.delete(url)
    print("DELETED USER")
    print(response.json())


def testUserUpdates():
    url = "http://0.0.0.0:8000/api/updateUser"

    headers = {"Content-Type": "application/json"}

    json = {
        "username": "pierce's cooler username",
        "email": "pwex@gmail.com",
    }
    response = requests.put(url=url, json=json, headers=headers)
    print("Updated USER")
    print(response.json())


def testUserGet():
    email = "pwex@gmail.com"
    url = f"http://0.0.0.0:8000/api/getUsername/{email}"

    response = requests.get(url)
    print("ASSOCIATED USERNAME:")
    print(response.json())


test_no = 1
match test_no:
    case 0:
        print("No tests ran")
    case 1:
        """
        Test 1: Basic User creation and viewing of username:
        """
        testUserCreation()
        testUserGet()
    case 2:
        """
        Test 2: Update username and view result:
        """
        testUserUpdates()
        testUserGet()
    case 3:
        """
        Test 3: Delete user:
        """
        testUserDeletion()
    case 4:
        """
        Test 4: All tests combined:
        """
        testUserCreation()
        testUserGet()
        testUserUpdates()
        testUserGet()
        testUserDeletion()
