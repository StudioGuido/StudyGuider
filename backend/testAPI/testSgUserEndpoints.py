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
        "title": "Advanced Math FlashCards",
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


def testGetFlashCardsFromSet():
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


# time.sleep(10)
test_no = 0
match test_no:
    case 0:
        print("No tests ran")
    case 1:
        """
        Test 1: Basic User, Flash Card Set, and Flash Card creation:
        """
        testUserCreation()
        stestFlashCardSetCreation()
        testFlashCardsCreation()
        testFlashCardSetDeletion1()
        testFlashCardSetDeletion2()
        testSummarySaving()
        testUserDeletion()
    case 2:
        """
        Test 2: Gathering all Flash Cards in a set for front end display purposes:
        """
        testUserCreation()
        testFlashCardSetCreation()
        testFlashCardsCreation()
        testGetFlashCardsFromSet()
        #
        testFlashCardSetDeletion2()
        testFlashCardSetDeletion1()
        testUserDeletion()
    case 3:
        """
        Test 3: Gathering all Flash Card Sets for front end display purposes:
        """
        testUserCreation()
        testFlashCardSetCreation()
        testFlashCardsCreation()
        testGetAllFlashcardSets()
        #
        testFlashCardSetDeletion2()
        testFlashCardSetDeletion1()
        testUserDeletion()

"""
Test 1: Basic User, Flash Card Set, and Flash Card creation:
"""
# testUserCreation()
# testFlashCardSetCreation()
# testFlashCardsCreation()
# testFlashCardSetDeletion1()
# testFlashCardSetDeletion2()
# testSummarySaving()
# testUserDeletion()

"""
Test 2: Gathering all Flash Cards in a set for front end display purposes:
"""
# testUserCreation()
# testFlashCardSetCreation()
# testFlashCardsCreation()
# testGetFlashCardsFromSet()
# #
# testFlashCardSetDeletion2()
# testFlashCardSetDeletion1()
# testUserDeletion()

"""
Test 3: Gathering all Flash Card Sets for front end display purposes:
"""
# testUserCreation()
# testFlashCardSetCreation()
# testFlashCardsCreation()
# testGetAllFlashcardSets()
# #
# testFlashCardSetDeletion2()
# testFlashCardSetDeletion1()
# testUserDeletion()
