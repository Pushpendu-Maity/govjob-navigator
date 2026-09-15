"""
test_app_endpoints.py - Automated verification of all Flask HTTP routes and APIs.
"""

from app import app

def run_api_tests():
    client = app.test_client()
    print("==================================================")
    print("Testing GovJob Navigator Web & API Endpoints")
    print("==================================================")

    # 1. Test Home Page
    res = client.get("/")
    assert res.status_code == 200, f"Failed GET / with code {res.status_code}"
    assert b"GovJob Navigator" in res.data, "Brand not found in home page"
    print("1. [GET /]: 200 OK (Interface rendered successfully)")

    # 2. Test /api/jobs (Catalog)
    res = client.get("/api/jobs")
    assert res.status_code == 200, "Failed /api/jobs"
    data = res.get_json()
    assert data["success"] is True, "Catalog failed"
    assert len(data["jobs"]) >= 15, "Insufficient jobs in catalog"
    print(f"2. [GET /api/jobs]: 200 OK (Catalog contains {len(data['jobs'])} curated recruitments)")

    # Test filtering by Tier 1 (10th pass)
    res_t1 = client.get("/api/jobs?tier=1")
    data_t1 = res_t1.get_json()
    assert all(j["tier"] == 1 for j in data_t1["jobs"]), "Tier 1 filter broken"
    print(f"   -> Tier 1 Filter: {len(data_t1['jobs'])} basic entry-level jobs found")

    # 3. Test /api/check-eligibility
    payload_10th = {
        "age": 19,
        "category": "UR",
        "education_level": "10th",
        "stream": "any",
        "percentage": 82.0,
        "gender": "male"
    }
    res_elig = client.post("/api/check-eligibility", json=payload_10th)
    assert res_elig.status_code == 200, "Failed /api/check-eligibility"
    data_elig = res_elig.get_json()
    assert data_elig["success"] is True, "Eligibility evaluation failed"
    assert data_elig["summary"]["eligible_count"] >= 3, "10th pass should qualify for at least 3 recruitments"
    print(f"3. [POST /api/check-eligibility]: 200 OK (10th pass: {data_elig['summary']['eligible_count']} eligible jobs, {data_elig['summary']['total_vacancies']:,} open vacancies)")

    # 4. Test /api/deadlines
    res_deadlines = client.get("/api/deadlines")
    assert res_deadlines.status_code == 200, "Failed /api/deadlines"
    data_deadlines = res_deadlines.get_json()
    assert len(data_deadlines["deadlines"]) >= 10, "Deadlines list empty"
    print(f"4. [GET /api/deadlines]: 200 OK ({len(data_deadlines['deadlines'])} application deadlines tracked)")

    # 5. Test /api/ai-counselor
    res_ai = client.post("/api/ai-counselor", json={"query": "Top paying government jobs for 10th and 12th pass"})
    assert res_ai.status_code == 200, "Failed /api/ai-counselor"
    data_ai = res_ai.get_json()
    assert data_ai["success"] is True, "AI counselor response failed"
    assert "Delhi Police" in data_ai["guidance"]["response"] or "MTS" in data_ai["guidance"]["response"]
    print("5. [POST /api/ai-counselor]: 200 OK (AI advisor returned structured career guidance)")

    # 6. Test /api/subscribe-alert
    res_alert = client.post("/api/subscribe-alert", json={
        "contact": "9876543210",
        "category": "OBC",
        "education": "graduate"
    })
    assert res_alert.status_code == 200, "Failed /api/subscribe-alert"
    data_alert = res_alert.get_json()
    assert data_alert["success"] is True, "Alert subscription failed"
    print("6. [POST /api/subscribe-alert]: 200 OK (Alert registered successfully)")

    print("\n==================================================")
    print("ALL API AND ENDPOINT TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_api_tests()
