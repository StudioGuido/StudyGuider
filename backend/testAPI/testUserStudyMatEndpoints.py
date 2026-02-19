import requests
import asyncio
import time


def testFlashCardSetCreation():
    url = "http://0.0.0.0:8000/api/createFlashCardSet"

    headers = {"Content-Type": "application/json"}

    json1 = {
        "user_email": "pwex@gmail.com",
        "title": "Basic Math FlashCards",
    }
    response1 = requests.post(url=url, json=json1, headers=headers)
    json2 = {
        "user_email": "pwex@gmail.com",
        "title": "Advanced Math FlashCards",
    }
    response2 = requests.post(url=url, json=json2, headers=headers)
    print(f"CREATED FLASH CARD SETS")
    print(response1.json())
    print(response2.json())

def testFlashcardSetUpdates():
    updated_title = "REALLY Advanced Math FlashCards"
    url = f"http://0.0.0.0:8000/api/updateFlashSet/{updated_title}"

    headers = {"Content-Type": "application/json"}

    json = {
        "user_email": "pwex@gmail.com",
        "title": "Advanced Math FlashCards",
    }
    response = requests.put(url=url, json=json, headers=headers)
    print("Updated USER")
    print(response.json())

def testFlashCardsCreation():
    url = "http://0.0.0.0:8000/api/addToFlashCardSet"
    headers = {"Content-Type": "application/json"}
    json1 = [
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
    response1 = requests.post(url=url, json=json1, headers=headers)

    json2 = [
        {
            "flashcardset": {
                "user_email": "pwex@gmail.com",
                "title": "Advanced Math FlashCards",
            },
            "question": "f(x) = 2x^2, What is f'(x)",
            "answer": "4x",
        },
        {
            "flashcardset": {
                "user_email": "pwex@gmail.com",
                "title": "Advanced Math FlashCards",
            },
            "question": "f(x) = 2x, What is f'(x)",
            "answer": "2",
        },
        {
            "flashcardset": {
                "user_email": "pwex@gmail.com",
                "title": "Advanced Math FlashCards",
            },
            "question": "f(x) = 2, What is f'(x)",
            "answer": "0",
        },
        {
            "flashcardset": {
                "user_email": "pwex@gmail.com",
                "title": "Advanced Math FlashCards",
            },
            "question": "417 % 10",
            "answer": "17",
        },
        {
            "flashcardset": {
                "user_email": "pwex@gmail.com",
                "title": "Advanced Math FlashCards",
            },
            "question": "5!",
            "answer": "120",
        },
    ]
    response2 = requests.post(url=url, json=json2, headers=headers)
    print(f"CREATED FLASH CARDS")
    print(response1.json())
    print(response2.json())


def testFlashCardSetDeletion1():
    url = f"http://0.0.0.0:8000/api/deleteFlashSet"
    headers = {"Content-Type": "application/json"}

    json = {
        "user_email": "pwex@gmail.com",
        "title": "Basic Math FlashCards",
    }

    response = requests.delete(url=url, json=json, headers=headers)
    print("DELETED FLASHSET")
    print(response.json())


def testFlashCardSetDeletion2():
    url = f"http://0.0.0.0:8000/api/deleteFlashSet"
    headers = {"Content-Type": "application/json"}

    json = {
        "user_email": "pwex@gmail.com",
        "title": "REALLY Advanced Math FlashCards",
    }

    response = requests.delete(url=url, json=json, headers=headers)
    print("DELETED FLASHSET")
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


def testGetFlashCardsFromSet2():
    url = "http://0.0.0.0:8000/api/getFlashcardsFromSet"

    headers = {"Content-Type": "application/json"}

    json = {
        "user_email": "pwex@gmail.com",
        "title": "Advanced Math FlashCards",
    }
    response = requests.get(url=url, json=json, headers=headers)
    print(f"Got Flash Cards")
    print(response.json())


def testGetAllFlashcardSets():
    url = "http://0.0.0.0:8000/api/getAllFlashcardSets"

    headers = {"Content-Type": "application/json"}

    json = {
        "username": "pierce",
        "email": "pwex@gmail.com",
    }
    response = requests.get(url=url, json=json, headers=headers)
    print(f"Got Flash Card Sets")
    print(response.json())


test_no = 3
match test_no:
    case 0:
        print("No tests ran")
    case 1:
        """
        Test 1: Creation of Summary, Flashcard Sets and Flash Cards:
        """
        testFlashCardSetCreation()
        testFlashCardsCreation()
        testSummarySaving()
    case 2:
        """
        Test 2: Gathering all Flash Cards in a set for front end display purposes, Updating the name of a set, and displaying all sets:
        """
        testGetFlashCardsFromSet2()
        testFlashcardSetUpdates()
        testGetAllFlashcardSets()
    case 3:
        """
        Test 3: Deleting Flash Card sets:
        """
        testGetAllFlashcardSets()
        testFlashCardSetDeletion2()
        testGetAllFlashcardSets()
        testFlashCardSetDeletion1()
        testGetAllFlashcardSets()
