import os
import requests
import time

BASE_URL = os.getenv("STUDYGUIDER_API_BASE_URL", "http://127.0.0.1:8000")
FLASHCARD_ENDPOINT = f"{BASE_URL}/api/generateFlashCard"

def run_flashcard_timing_test(counts=(1, 5, 10), trials_per_count=2, textbook="thinkpython2", chapter="Files"):
    total_cards_returned = 0
    for count in counts:
        for trial in range(1, trials_per_count + 1):
            payload = {"textbook": textbook, "chapter": chapter, "count": count}
            try:
                response = requests.post(FLASHCARD_ENDPOINT, json=payload, timeout=300)
                body = response.json() if response.content else {}
                cards_returned = len(body.get("response", {}))
                print({"count": count, "trial": trial, "status_code": response.status_code, "cards_returned": cards_returned})
                total_cards_returned += cards_returned
            except Exception as e:
                print({"count": count, "trial": trial, "error": str(e)})
    return total_cards_returned

def main():
    suite_start = time.perf_counter()
    total_cards_returned = run_flashcard_timing_test(counts=(1, 5, 10), trials_per_count=2)
    suite_seconds = time.perf_counter() - suite_start
    flashcards_per_second = total_cards_returned / suite_seconds if suite_seconds > 0 else 0.0
    print("Flashcards per second: ", flashcards_per_second)

if __name__ == "__main__":
    main()
