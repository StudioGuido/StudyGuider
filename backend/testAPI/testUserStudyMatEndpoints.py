import requests
import asyncio
import time

# Flashcard POSTs need a valid chapter_embeddings row; run once: psql < backend/test_seed_minimal.sql

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
    "Authorization": f"Bearer {TOKEN}",
}
JSON_AUTH_HEADERS = {"Content-Type": "application/json", **AUTH_HEADERS}

API_BASE = "http://0.0.0.0:8000"


def _create_master(headers, question: str, answer: str) -> int:
    """POST /api/createMasterFlashcard — needs chapter_embeddings (1,1,0); see test_seed_minimal.sql."""
    r = requests.post(
        f"{API_BASE}/api/createMasterFlashcard",
        headers=headers,
        json={
            "question": question,
            "answer": answer,
            "textbook_id": 1,
            "chapter_number": 1,
            "chunk_index": 0,
        },
    )
    r.raise_for_status()
    return r.json()["response"]["fc_id"]


def _assign_to_set(set_title: str, master_fc_id: int) -> dict:
    """Payload for /api/addToFlashCardSet."""
    return {"flashcardset": {"title": set_title}, "master_fc_id": master_fc_id}


def testFlashCardSetCreation():
    url = f"{API_BASE}/api/createFlashCardSet"
    headers = JSON_AUTH_HEADERS

    json1 = {
        "title": "Basic Math FlashCards",
    }
    response1 = requests.post(url=url, json=json1, headers=headers)
    json2 = {
        "title": "Advanced Math FlashCards",
    }
    response2 = requests.post(url=url, json=json2, headers=headers)
    print(f"CREATED FLASH CARD SETS")
    print(response1.json())
    print(response2.json())

def testFlashcardSetUpdates():
    updated_title = "REALLY Advanced Math FlashCards"
    url = f"{API_BASE}/api/updateFlashSet/{updated_title}"

    headers = JSON_AUTH_HEADERS

    json = {
        "title": "Advanced Math FlashCards",
    }
    response = requests.put(url=url, json=json, headers=headers)
    print("Updated USER")
    print(response.json())

def testFlashCardsCreation():
    url = f"{API_BASE}/api/addToFlashCardSet"
    headers = JSON_AUTH_HEADERS

    basics = [
        ("1 + 1", "2"),
        ("1 - 1", "0"),
        ("1 * 1", "1"),
        ("1 / 1", "1"),
        ("1 ^ 1", "1"),
    ]
    json1 = [
        _assign_to_set("Basic Math FlashCards", _create_master(headers, q, a))
        for q, a in basics
    ]
    response1 = requests.post(url=url, json=json1, headers=headers)

    advanced = [
        ("f(x) = 2x^2, What is f'(x)", "4x"),
        ("f(x) = 2x, What is f'(x)", "2"),
        ("f(x) = 2, What is f'(x)", "0"),
        ("417 % 10", "17"),
        ("5!", "120"),
    ]
    json2 = [
        _assign_to_set("Advanced Math FlashCards", _create_master(headers, q, a))
        for q, a in advanced
    ]
    response2 = requests.post(url=url, json=json2, headers=headers)
    print(f"CREATED FLASH CARDS")
    print(response1.json())
    print(response2.json())


def testFlashCardSetDeletion1():
    url = f"{API_BASE}/api/deleteFlashSet"
    headers = JSON_AUTH_HEADERS

    json = {
        "title": "Basic Math FlashCards",
    }

    response = requests.delete(url=url, json=json, headers=headers)
    print("DELETED FLASHSET")
    print(response.json())


def testFlashCardSetDeletion2():
    url = f"{API_BASE}/api/deleteFlashSet"
    headers = JSON_AUTH_HEADERS

    json = {
        "title": "REALLY Advanced Math FlashCards",
    }

    response = requests.delete(url=url, json=json, headers=headers)
    print("DELETED FLASHSET")
    print(response.json())
    


def testSummarySaving():
    url = f"{API_BASE}/api/saveSummary"
    headers = JSON_AUTH_HEADERS

    json = {
        "title": "Important Generated Summary",
        "content": "Chatgpt says that ......",
    }
    response = requests.post(url=url, json=json, headers=headers)
    print(f"SAVED SUMMARY")
    print(response.json())


def testGetFlashCardsFromSet2():
    url = f"{API_BASE}/api/getFlashcardsFromSet"
    headers = JSON_AUTH_HEADERS

    json = {
        "title": "Advanced Math FlashCards",
    }
    response = requests.get(url=url, json=json, headers=headers)
    print(f"Got Flash Cards")
    print(response.json())


def testGetAllFlashcardSets():
    url = f"{API_BASE}/api/getAllFlashcardSets"
    headers = JSON_AUTH_HEADERS
    response = requests.get(url=url, headers=headers)
    print(f"Got Flash Card Sets")
    print(response.json())


test_no = 1
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
