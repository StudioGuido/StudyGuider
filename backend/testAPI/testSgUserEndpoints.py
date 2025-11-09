import requests
import asyncio
import time


def testUserCreation():
    url = "http://0.0.0.0:8000/api/createUser"

    headers = {"Content-Type": "application/json"}

    json = {
        "username": "pierce",
        "email": "pwex@gmail.com",
    }
    response = requests.post(url=url, json=json, headers=headers)
    chunk_data = response.json()
    print("CREATED USER")
    print(response.json())


def testUserDeletion():
    username = "pierce"
    url = f"http://0.0.0.0:8000/api/deleteUser/{username}"

    response = requests.delete(url)
    print("DELETED USER")
    print(response.json())


# createFlashCardSet


def testFlashCardSetCreation():
    url = "http://0.0.0.0:8000/api/createFlashCardSet"

    headers = {"Content-Type": "application/json"}

    json = {
        "user_email": "pwex@gmail.com",
        "title": "Basic Math FlashCards",
    }
    response = requests.post(url=url, json=json, headers=headers)
    print(f"CREATED FLASH CARD SET")
    print(response.json())


def testFlashCardsCreation():
    url = "http://0.0.0.0:8000/api/addToFlashCardSet"

    headers = {"Content-Type": "application/json"}

    json = [
        {
            "flashcardset": {
                "user_email": "pwex@gmail.com",
                "title": "Basic Math FlashCards",
            },
            "question": "1 + 1",
            "answer": "2",
        },
        {
            "flashcardset": {
                "user_email": "pwex@gmail.com",
                "title": "Basic Math FlashCards",
            },
            "question": "1 - 1",
            "answer": "0",
        },
        {
            "flashcardset": {
                "user_email": "pwex@gmail.com",
                "title": "Basic Math FlashCards",
            },
            "question": "1 * 1",
            "answer": "1",
        },
        {
            "flashcardset": {
                "user_email": "pwex@gmail.com",
                "title": "Basic Math FlashCards",
            },
            "question": "1 / 1",
            "answer": "1",
        },
        {
            "flashcardset": {
                "user_email": "pwex@gmail.com",
                "title": "Basic Math FlashCards",
            },
            "question": "1 ^ 1",
            "answer": "1",
        },
    ]
    response = requests.post(url=url, json=json, headers=headers)
    print(f"CREATED FLASH CARDS")
    print(response.json())


def testSummarySaving():
    url = "http://0.0.0.0:8000/api/saveSummary"

    headers = {"Content-Type": "application/json"}

    json = {
        "user_email": "pwex@gmail.com",
        "title": "Important Generated Summary",
        "content": "Chatgpt says that ......",
    }
    response = requests.post(url=url, json=json, headers=headers)
    print(f"SAVED SUMMARY")
    print(response.json())


# time.sleep(10)
testUserCreation()
# time.sleep(10)
testFlashCardSetCreation()
# time.sleep(10)
testFlashCardsCreation()
# time.sleep(10)
testSummarySaving()
# time.sleep(10)
# testUserDeletion()
