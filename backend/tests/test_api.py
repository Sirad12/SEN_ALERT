import os

os.environ["DATABASE_URL"] = "sqlite:///./test_senalert.db"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

PHOTO = "data:image/png;base64,AA"


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    with TestClient(app) as c:
        yield c


def jeton(client):
    r = client.post("/api/admin/login", json={"username": "admin", "password": "demo123"})
    return {"Authorization": f"Bearer {r.json()['token']}"}


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_donnees_de_demo_chargees(client):
    ids = [s["id"] for s in client.get("/api/signalements").json()]
    assert "SIG-000119" in ids


def test_creation_donne_un_identifiant_unique(client):
    corps = {"type": "Caniveau bouché", "description": "Caniveau bouché devant l’école",
             "x": 10, "y": 10, "photo": PHOTO}
    a = client.post("/api/signalements", json=corps).json()
    b = client.post("/api/signalements", json=corps).json()
    assert a["id"] != b["id"]
    assert a["statut"] == "Signalé"
    assert client.get(f"/api/signalements/{a['id'].lower()}").status_code == 200


def test_description_trop_courte_refusee(client):
    corps = {"type": "Rue bouchée", "description": "court", "x": 1, "y": 1, "photo": PHOTO}
    assert client.post("/api/signalements", json=corps).status_code == 422


def test_mauvais_mot_de_passe(client):
    r = client.post("/api/admin/login", json={"username": "admin", "password": "faux"})
    assert r.status_code == 401


def test_changement_de_statut_reserve_a_l_admin(client):
    r = client.patch("/api/signalements/SIG-000121/statut", json={"statut": "Vérifié"})
    assert r.status_code == 401


def test_historique_et_transitions(client):
    h = jeton(client)
    r = client.patch("/api/signalements/SIG-000121/statut", json={"statut": "Vérifié"}, headers=h)
    assert [e["statut"] for e in r.json()["historique"]] == ["Signalé", "Vérifié"]
    # Passer directement à « Résolu » est interdit
    r = client.patch("/api/signalements/SIG-000121/statut",
                     json={"statut": "Résolu", "note": "x"}, headers=h)
    assert r.status_code == 400


def test_note_obligatoire_pour_resoudre(client):
    h = jeton(client)
    r = client.patch("/api/signalements/SIG-000119/statut", json={"statut": "Résolu"}, headers=h)
    assert r.status_code == 400
