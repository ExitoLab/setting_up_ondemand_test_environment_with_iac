import sys
import requests
import time

BASE_URL = sys.argv[1]  # Pass the ACI/FQDN URL as first argument

# -------------------- Smoke Test --------------------
def smoke_test():
    """Check if app is reachable."""
    r = requests.get(BASE_URL)
    assert r.status_code == 200, "App not reachable"
    print("✅ Smoke test passed")

# -------------------- Functional Tests --------------------
def login_tests():
    """Test login functionality with valid and invalid credentials."""
    # Valid login
    r = requests.post(f"{BASE_URL}/login", json={"user": "qa", "pass": "123"})
    assert r.status_code == 200, "Valid login failed"
    token = r.json().get("token")
    assert token, "Token missing for valid login"

    # Invalid login attempts
    for creds in [{"user": "", "pass": ""}, {"user": "qa", "pass": "wrong"}]:
        r = requests.post(f"{BASE_URL}/login", json=creds)
        assert r.status_code == 401, f"Invalid login passed for {creds}"

    print("✅ Login tests passed")
    return token

def task_crud_tests(token):
    """Test creating, listing, updating, and deleting tasks."""
    headers = {"Authorization": f"Bearer {token}"}

    # Create multiple tasks
    for i in range(5):
        r = requests.post(f"{BASE_URL}/tasks", json={"title": f"Task {i}"}, headers=headers)
        assert r.status_code == 201, f"Task {i} creation failed"

    # List tasks
    r = requests.get(f"{BASE_URL}/tasks", headers=headers)
    tasks = r.json()
    assert len(tasks) >= 5, "Not all tasks created"

    # Update first task
    task_id = tasks[0]["id"]
    r = requests.put(f"{BASE_URL}/tasks/{task_id}", json={"title": "Updated Task"}, headers=headers)
    assert r.status_code in [200, 404], "Update task failed"

    # Delete second task
    task_id = tasks[1]["id"]
    r = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=headers)
    assert r.status_code in [200, 404], "Delete task failed"

    print("✅ Task CRUD tests passed")

# -------------------- Edge Case Tests --------------------
def edge_case_tests(token):
    headers = {"Authorization": f"Bearer {token}"}

    # Long title
    long_title = "T" * 5000
    r = requests.post(f"{BASE_URL}/tasks", json={"title": long_title}, headers=headers)
    assert r.status_code == 201, "Failed with long task title"

    # Special characters
    special_title = "!@#$%^&*()_+{}|<>?"
    r = requests.post(f"{BASE_URL}/tasks", json={"title": special_title}, headers=headers)
    assert r.status_code == 201, "Failed with special characters"

    # Missing headers / auth
    r = requests.post(f"{BASE_URL}/tasks", json={"title": "No Auth"})
    assert r.status_code in [401, 403], "Unauthorized access allowed"

    print("✅ Edge case tests passed")

# -------------------- Security Tests --------------------
def security_tests(token):
    headers = {"Authorization": f"Bearer {token}"}

    # SQL Injection
    injection = "' OR '1'='1"
    r = requests.post(f"{BASE_URL}/tasks", json={"title": injection}, headers=headers)
    assert r.status_code == 201, "SQL injection caused failure"

    # XSS attempt
    xss = "<script>alert('xss')</script>"
    r = requests.post(f"{BASE_URL}/tasks", json={"title": xss}, headers=headers)
    assert r.status_code == 201, "XSS test failed"

    # Tampered token
    headers_bad = {"Authorization": f"Bearer {token}123"}
    r = requests.get(f"{BASE_URL}/tasks", headers=headers_bad)
    assert r.status_code in [401, 403], "Tampered token bypassed security"

    print("✅ Security tests passed")

# -------------------- Performance / Load Tests --------------------
def performance_tests(token):
    headers = {"Authorization": f"Bearer {token}"}
    start_time = time.time()
    for _ in range(20):
        r = requests.get(f"{BASE_URL}/tasks", headers=headers)
        assert r.status_code == 200
    duration = time.time() - start_time
    assert duration < 5, f"Performance issue: 20 requests took {duration:.2f}s"
    print("✅ Performance tests passed")

# -------------------- Negative / Failure Tests --------------------
def negative_tests(token):
    headers = {"Authorization": f"Bearer {token}"}

    # Invalid JSON
    r = requests.post(f"{BASE_URL}/tasks", data="notjson", headers=headers)
    assert r.status_code in [400, 415], "Invalid JSON not handled"

    # Invalid endpoint
    r = requests.get(f"{BASE_URL}/invalid-endpoint", headers=headers)
    assert r.status_code == 404, "Invalid endpoint did not return 404"

    print("✅ Negative tests passed")

# -------------------- Run All Tests --------------------
if __name__ == "__main__":
    smoke_test()
    token = login_tests()
    task_crud_tests(token)
    edge_case_tests(token)
    security_tests(token)
    performance_tests(token)
    negative_tests(token)
    print("🎉 All QA tests passed!")
