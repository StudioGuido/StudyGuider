"""
Manual API tests for user study material endpoints.
"""

import requests

SUPABASE_URL = "https://bafblcxwhdvikgcpcnds.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_EHbCfU3Xd5oku8EZZTLD7g_1bxWBYnC"

EMAIL = "test@gmail.com"
PASSWORD = "testpass123"


# ---------------- AUTH ---------------- #

def get_jwt():
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"

    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
    }

    response = requests.post(
        url,
        headers=headers,
        json={"email": EMAIL, "password": PASSWORD},
    )

    if response.status_code != 200:
        print("Login failed:", response.text)
        exit()

    return response.json()["access_token"]


TOKEN = get_jwt()

AUTH_HEADERS = {"Authorization": f"Bearer {TOKEN}"}
JSON_HEADERS = {"Content-Type": "application/json", **AUTH_HEADERS}


BASE_URL = "http://0.0.0.0:8000/api"


# ---------------- FLASHCARD SET ---------------- #

def create_sets():
    print("\n--- Creating Sets ---")
    for title in ["Basic Math FlashCards", "Advanced Math FlashCards"]:
        res = requests.post(
            f"{BASE_URL}/createFlashCardSet",
            json={"title": title},
            headers=JSON_HEADERS,
        )
        print(res.json())


def update_set():
    print("\n--- Updating Set ---")
    res = requests.put(
        f"{BASE_URL}/updateFlashcardSetName",
        params={
            "old_title": "Advanced Math FlashCards",
            "new_title": "REALLY Advanced Math FlashCards",
        },
        headers=JSON_HEADERS,
    )
    print(res.json())


def delete_set(title):
    print(f"\n--- Deleting Set: {title} ---")
    res = requests.delete(
        f"{BASE_URL}/deleteFlashSet",
        json={"title": title},
        headers=JSON_HEADERS,
    )
    print(res.json())


def get_sets():
    print("\n--- All Sets ---")
    res = requests.get(f"{BASE_URL}/getAllFlashcardSets", headers=JSON_HEADERS)
    print(res.json())


# ---------------- FLASHCARDS ---------------- #

def create_and_assign_flashcards():
    print("\n--- Creating & Assigning Flashcards ---")

    create_url = f"{BASE_URL}/addMasterFlashcard"
    assign_url = f"{BASE_URL}/addFlashcardToSet"

    flashcards = [
        {"question": "1 + 1", "answer": "2"},
        {"question": "1 - 1", "answer": "0"},
    ]

    for fc in flashcards:
        # Create master flashcard
        res = requests.post(
            create_url,
            json={
                **fc,
                "textbook_id": 1,
                "chapter_number": 1,
                "chunk_index": 1,
            },
            headers=JSON_HEADERS,
        )

        data = res.json()
        print(data)

        fc_id = data["response"]["fc_id"]

        # Assign to set
        assign_res = requests.post(
            assign_url,
            json={
                "set_title": "Basic Math FlashCards",
                "flashcard_id": fc_id,
            },
            headers=JSON_HEADERS,
        )
        print(assign_res.json())


def get_flashcards_from_set():
    print("\n--- Flashcards From Set ---")
    res = requests.get(
        f"{BASE_URL}/getFlashcardsFromSet",
        params={"title": "REALLY Advanced Math FlashCards"},
        headers=JSON_HEADERS,
    )
    print(res.json())


# ---------------- SUMMARY ---------------- #

def save_summary():
    print("\n--- Saving Summary ---")
    res = requests.post(
        f"{BASE_URL}/saveSummary",
        json={
            "title": "Important Summary",
            "content": "ChatGPT says that ......",
        },
        headers=JSON_HEADERS,
    )
    print(res.json())


def get_summaries():
    print("\n--- Get Summaries ---")
    res = requests.get(f"{BASE_URL}/getSummaries", headers=JSON_HEADERS)
    print(res.json())


# ---------------- SEEN ---------------- #

def get_seen_flashcards():
    print("\n--- Seen Flashcards ---")
    res = requests.get(f"{BASE_URL}/getSeenFlashcards", headers=JSON_HEADERS)
    print(res.json())


# ---------------- RUN ---------------- #

test_no = 3

match test_no:
    case 0:
        print("No tests ran")

    case 1:
        # Full creation flow
        create_sets()
        create_and_assign_flashcards()
        save_summary()

    case 2:
        # Update + retrieval
        update_set()
        get_flashcards_from_set()
        get_sets()
        get_summaries()

    case 3:
        # Deletion flow
        get_sets()
        delete_set("REALLY Advanced Math FlashCards")
        delete_set("Basic Math FlashCards")
        get_sets()