import pytest
import app as application


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"

    monkeypatch.setattr(application, "DATABASE", str(db_path))

    application.init_db()

    application.app.config["TESTING"] = True

    with application.app.test_client() as client:
        yield client


def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200


def test_add_expense(client):
    response = client.post("/add", data={
        "amount": "250",
        "category": "Food",
        "expense_date": "2026-11-01"
    })

    assert response.status_code == 302

    response = client.get("/")
    assert b"Food" in response.data
    assert b"250" in response.data


def test_edit_expense(client):
    client.post("/add", data={
        "amount": "250",
        "category": "Food",
        "expense_date": "2026-11-01"
    })

    response = client.post("/edit/1", data={
        "amount": "500",
        "category": "Travel",
        "expense_date": "2026-11-01"
    })

    assert response.status_code == 302

    response = client.get("/")
    assert b"Travel" in response.data
    assert b"500" in response.data


def test_delete_expense(client):
    client.post("/add", data={
        "amount": "250",
        "category": "Food",
        "expense_date": "2026-11-01"
    })

    response = client.post("/delete/1")

    assert response.status_code == 302

    response = client.get("/")
    assert b"0.0" in response.data