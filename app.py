
from flask import Flask, request, render_template_string
import sqlite3
from urllib.parse import urlparse

app = Flask(__name__)

DATABASE = "submissions.db"


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            registration_number TEXT NOT NULL,
            assignment_title TEXT NOT NULL,
            submission_url TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def valid_url(url):
    try:
        parsed = urlparse(url)
        return (
            parsed.scheme in ("http", "https")
            and bool(parsed.netloc)
            and "." in parsed.netloc
        )
    except ValueError:
        return False


HTML = """
<h1>Assignment Submission Portal</h1>

<form method="POST">
    <input name="name" placeholder="Student Name" required><br><br>

    <input name="registration_number"
           placeholder="Registration Number" required><br><br>

    <input name="assignment_title"
           placeholder="Assignment Title" required><br><br>

    <input name="submission_url"
           placeholder="Submission URL" required><br><br>

    <button type="submit">Submit Assignment</button>
</form>

<h3>{{ message }}</h3>

<h2>Saved Submissions</h2>

{% for item in submissions %}
    <p>
        {{ item.name }} |
        {{ item.registration_number }} |
        {{ item.assignment_title }} |
        <a href="{{ item.submission_url }}">Open Assignment</a>
    </p>
{% endfor %}
"""


@app.route("/", methods=["GET", "POST"])
def home():

    message = ""

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        registration = request.form.get("registration_number", "").strip()
        title = request.form.get("assignment_title", "").strip()
        url = request.form.get("submission_url", "").strip()

        if not all([name, registration, title, url]):
            message = "All fields are required."

        elif not valid_url(url):
            message = "Invalid submission URL."

        else:
            connection = get_db()

            connection.execute(
                """INSERT INTO submissions
                (name, registration_number, assignment_title, submission_url)
                VALUES (?, ?, ?, ?)""",
                (name, registration, title, url)
            )

            connection.commit()
            connection.close()

            message = "Assignment submitted successfully!"

    connection = get_db()

    submissions = connection.execute(
        "SELECT * FROM submissions ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return render_template_string(
        HTML,
        message=message,
        submissions=submissions
    )


initialize_database()


if __name__ == "__main__":
    app.run(debug=True)
