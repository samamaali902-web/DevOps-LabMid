
import app
import sqlite3


def setup_database(tmp_path, monkeypatch):
    test_database = tmp_path / "test_submissions.db"
    monkeypatch.setattr(app, "DATABASE", str(test_database))
    app.initialize_database()


def test_valid_submission(tmp_path, monkeypatch):
    setup_database(tmp_path, monkeypatch)
    client = app.app.test_client()

    response = client.post("/", data={
        "name": "Ali Ahmed",
        "registration_number": "FA23-BAI-024",
        "assignment_title": "DevOps Lab",
        "submission_url": "https://github.com/"
    })

    assert b"Assignment submitted successfully!" in response.data

    connection = sqlite3.connect(app.DATABASE)
    count = connection.execute(
        "SELECT COUNT(*) FROM submissions"
    ).fetchone()[0]
    connection.close()

    assert count == 1


def test_missing_registration_number(tmp_path, monkeypatch):
    setup_database(tmp_path, monkeypatch)
    client = app.app.test_client()

    response = client.post("/", data={
        "name": "Ali Ahmed",
        "registration_number": "",
        "assignment_title": "DevOps Lab",
        "submission_url": "https://github.com/"
    })

    assert b"All fields are required." in response.data

    connection = sqlite3.connect(app.DATABASE)
    count = connection.execute(
        "SELECT COUNT(*) FROM submissions"
    ).fetchone()[0]
    connection.close()

    assert count == 0


def test_invalid_submission_url(tmp_path, monkeypatch):
    setup_database(tmp_path, monkeypatch)
    client = app.app.test_client()

    response = client.post("/", data={
        "name": "Ali Ahmed",
        "registration_number": "FA23-BAI-024",
        "assignment_title": "DevOps Lab",
        "submission_url": "invalid-url"
    })

    assert b"Invalid submission URL." in response.data

    connection = sqlite3.connect(app.DATABASE)
    count = connection.execute(
        "SELECT COUNT(*) FROM submissions"
    ).fetchone()[0]
    connection.close()

    assert count == 0
