"""Full integration test: admin register -> upload CSV -> student login -> /me -> access control."""
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import json

BASE = "http://127.0.0.1:8000"

def api(method, path, data=None, token=None, form=False):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if data and not form:
        headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode()
    elif data and form:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        body = data.encode() if isinstance(data, str) else data
    else:
        body = None
    req = Request(f"{BASE}{path}", data=body, headers=headers, method=method)
    try:
        r = urlopen(req)
        return r.status, json.loads(r.read())
    except HTTPError as e:
        return e.code, json.loads(e.read())

print("=" * 60)
print("1. Register admin (teacher)")
status, body = api("POST", "/auth/register", {"username": "teacher", "email": "teacher@school.com", "password": "T123", "role": "admin"})
print(f"   Status: {status} -> {body}")

print("\n2. Admin login")
status, body = api("POST", "/auth/login", "username=teacher&password=T123", form=True)
admin_token = body["access_token"]
print(f"   Status: {status} -> Got token")

print("\n3. Admin loads CSV (auto-creates students)")
status, body = api("POST", "/marks/load-csv", token=admin_token)
print(f"   Status: {status} -> {body['message']}")
print(f"   First 3 credentials: {body.get('student_credentials', [])[:3]}")

print("\n4. Student_1 login (username=Student_1, password=STU001)")
status, body = api("POST", "/auth/login", "username=Student_1&password=STU001", form=True)
student_token = body["access_token"]
print(f"   Status: {status} -> Got token")

print("\n5. Student_1 accesses /auth/me (should show marks)")
status, body = api("GET", "/auth/me", token=student_token)
print(f"   Status: {status} -> {body}")

print("\n6. Student_1 accesses /marks/average (should work)")
status, body = api("GET", "/marks/average", token=student_token)
print(f"   Status: {status} -> {body}")

print("\n7. Student_1 accesses /marks/highest (should work)")
status, body = api("GET", "/marks/highest", token=student_token)
print(f"   Status: {status} -> {body}")

print("\n8. Student_1 tries /marks/ (list all - should FAIL)")
status, body = api("GET", "/marks/", token=student_token)
print(f"   Status: {status} -> {body}")

print("\n9. Student_1 tries /marks/load-csv (should FAIL)")
status, body = api("POST", "/marks/load-csv", token=student_token)
print(f"   Status: {status} -> {body}")

print("\n10. Admin tries /auth/me (should FAIL)")
status, body = api("GET", "/auth/me", token=admin_token)
print(f"   Status: {status} -> {body}")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETE!")
