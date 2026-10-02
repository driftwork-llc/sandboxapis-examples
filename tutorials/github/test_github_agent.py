import requests

PIN = "https://gh-2026-03-g12.snap.sandboxapis.dev/repos/olympus-labs/parthenon"

def test_the_incident_fix_shipped():
    pr = requests.get(PIN + "/pulls/53", timeout=30).json()
    assert pr["merged"] and pr["head"]["sha"] == "94dd1fdf3b96e96c242a869801e448edeca9fd85"
