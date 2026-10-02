import requests

PIN = "https://jira-v3-g12.snap.sandboxapis.dev/rest/api/3"

def test_the_incident_closed_as_done():
    fields = requests.get(PIN + "/issue/FATE-51?fields=status,resolutiondate", timeout=30).json()["fields"]
    assert fields["status"]["name"] == "Done" and fields["resolutiondate"] == "2026-06-19T16:21:17.000+0000"
