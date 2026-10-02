import requests

PIN = "https://slack-2026-08-g12.snap.sandboxapis.dev/api"

def test_the_incident_thread_is_a_real_burst():
    body = requests.get(PIN + "/conversations.history", params={"channel": "CF1UPUMGC8Q", "limit": 1}, timeout=30).json()
    assert body["ok"] and body["messages"][0]["reply_count"] == 11
