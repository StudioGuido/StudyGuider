import requests

def testUserCreation():
    url = 'http://0.0.0.0:8000/api/createUser'

    headers = {
        "Content-Type": "application/json"
    }

    json = {
        "username": "firerazor420Blazer",
        "email": "minecrafter8@icloud.com",
        "password": "alibutt",
        "first_name": "Niv",
        "last_name": "Butt",
        "provider": None,
        "provider_id": None
    }
    response = requests.post(url=url, json=json, headers=headers)
    chunk_data = response.json()

    print(chunk_data['response'])


def testgetCreation():
    url = 'http://0.0.0.0:8000/api/getUser'

    headers = {
        "Content-Type": "application/json"
    }
    json = {
        "username": "firerazor420Blazer",
        "password": "alibutt"
    }
    response = requests.post(url=url, json=json, headers=headers)
    chunk_data = response.json()

    print(response.status_code)
    print(chunk_data['response'])


def testDeleteUser():
    url = 'http://0.0.0.0:8000/api/deleteUser'

    headers = {
        "Content-Type": "application/json"
    }
    json = {
        "username": "firerazor420Blazer",
        "password": "alibutt"
    }
    response = requests.post(url=url, json=json, headers=headers)
    chunk_data = response.json()

    print(response.status_code)
    print(chunk_data['response'])

testUserCreation()