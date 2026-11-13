import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

report_path = Path("pytest-report.json")

if report_path.exists():
    with open(report_path, encoding="utf-8") as file:
        pytest_data = json.load(file)
else:
    pytest_data = {"tests": []}

tests = []

for test in pytest_data.get("tests", []):
    outcome = test.get("outcome", "unknown")
    call = test.get("call", {})
    failure = call.get("longrepr", "")

    tests.append({
        "name": test.get("nodeid", "Unknown test"),
        "result": outcome,
        "failure_message": str(failure) if outcome == "failed" else ""
    })

total = len(tests)
passed = sum(1 for test in tests if test["result"] == "passed")
failed = sum(1 for test in tests if test["result"] == "failed")

report = {
    "repository": os.environ.get("GITHUB_REPOSITORY", "Unknown"),
    "branch": os.environ.get("GITHUB_REF_NAME", "Unknown"),
    "commit_sha": os.environ.get("GITHUB_SHA", "Unknown"),
    "run_id": os.environ.get("GITHUB_RUN_ID", "Unknown"),
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "tests": tests,
    "total": total,
    "passed": passed,
    "failed": failed,
    "status": "passed" if failed == 0 and total > 0 else "failed"
}

url = os.environ["REPORT_URL"]
token = os.environ["REPORT_TOKEN"]

data = json.dumps(report).encode("utf-8")

request = urllib.request.Request(
    url,
    data=data,
    headers={
        "Content-Type": "application/json",
        "X-Report-Token": token
    },
    method="POST"
)

with urllib.request.urlopen(request, timeout=30) as response:
    print("Report delivery:", response.status)
    print(response.read().decode("utf-8"))

print(f"Tests: {total}, Passed: {passed}, Failed: {failed}")
print("Overall status:", report["status"])