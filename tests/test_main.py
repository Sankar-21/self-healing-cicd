from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))
from main import app

client = TestClient(app)

def test_root():
    r = client.get("/")
    assert r.status_code == 200

def test_health():
    r = client.get("/health")
    assert r.json()["healthy"] == True

def test_add():
    r = client.get("/add?a=3&b=4")
    assert r.json()["result"] == 7