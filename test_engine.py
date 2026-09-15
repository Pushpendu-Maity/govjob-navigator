"""
test_engine.py - Automated validation suite for GovJob Navigator eligibility engine.
"""

from engine import match_all_jobs, evaluate_eligibility, calculate_age
from jobs_data import get_all_jobs, get_job_by_id

def run_tests():
    print("==================================================")
    print("Testing GovJob Navigator Eligibility Engine")
    print("==================================================")
    
    # Test 1: Age Calculator
    years, frac = calculate_age("2002-05-15")
    print(f"Test 1 [Age Calculation]: DOB 2002-05-15 -> {years} years ({frac})")
    assert years >= 24, "Age calculation error"
    print("  [PASS]")

    # Test 2: 10th Pass Candidate (19 yrs, UR)
    profile_10th = {
        "age": 19,
        "category": "UR",
        "education_level": "10th",
        "stream": "any",
        "percentage": 78.0,
        "gender": "male"
    }
    res_10th = match_all_jobs(profile_10th)
    print(f"\nTest 2 [10th Pass Candidate, 19 yrs, UR]:")
    print(f"  Eligible: {len(res_10th['eligible'])} jobs (Vacancies: {res_10th['total_eligible_vacancies']:,})")
    print(f"  Ineligible: {len(res_10th['ineligible'])} jobs")
    # Verify 10th pass gets Post Office GDS, SSC MTS, Railway Group D
    eligible_ids = [j["job_id"] for j in res_10th["eligible"]]
    assert "india-post-gds" in eligible_ids, "Post Office GDS should be eligible"
    assert "ssc-mts-havaldar" in eligible_ids, "SSC MTS should be eligible"
    assert "rrb-group-d" in eligible_ids, "Railway Group D should be eligible"
    assert "ssc-cgl" not in eligible_ids, "SSC CGL should NOT be eligible for 10th pass"
    print("  [PASS]")

    # Test 3: 12th PCM Student (21 yrs, OBC)
    profile_12th_pcm = {
        "age": 21,
        "category": "OBC",
        "education_level": "12th",
        "stream": "12th_pcm",
        "percentage": 72.0,
        "gender": "male"
    }
    res_12th = match_all_jobs(profile_12th_pcm)
    print(f"\nTest 3 [12th PCM Candidate, 21 yrs, OBC]:")
    print(f"  Eligible: {len(res_12th['eligible'])} jobs")
    eligible_12th_ids = [j["job_id"] for j in res_12th["eligible"]]
    assert "state-police-constable-up" in eligible_12th_ids, "UP Police Constable should be eligible"
    assert "delhi-police-constable" in eligible_12th_ids, "Delhi Police Constable should be eligible"
    assert "rrb-technician-iii" in eligible_12th_ids, "RRB Technician should be eligible for 12th PCM"
    print("  [PASS]")

    # Test 4: B.Tech Engineering Graduate (26 yrs, SC)
    profile_btech = {
        "age": 26,
        "category": "SC",
        "education_level": "graduate",
        "stream": "mechanical",
        "percentage": 68.0,
        "gender": "male"
    }
    res_btech = match_all_jobs(profile_btech)
    print(f"\nTest 4 [B.Tech Graduate, 26 yrs, SC]:")
    print(f"  Eligible: {len(res_btech['eligible'])} jobs")
    eligible_btech_ids = [j["job_id"] for j in res_btech["eligible"]]
    assert "ssc-cgl" in eligible_btech_ids, "SSC CGL must be eligible"
    assert "ibps-po" in eligible_btech_ids, "IBPS PO must be eligible"
    assert "upsc-civil-services" in eligible_btech_ids, "UPSC CSE must be eligible"
    assert "gate-psu-ongc-iocl" in eligible_btech_ids, "GATE PSU must be eligible"
    assert "rrb-alp" in eligible_btech_ids, "RRB ALP must be eligible"
    print("  [PASS]")

    # Test 5: 33-year-old UR Candidate (Over-age for CGL/Bank PO, but eligible for State PSC up to 40)
    profile_senior = {
        "age": 33,
        "category": "UR",
        "education_level": "graduate",
        "stream": "any",
        "percentage": 60.0,
        "gender": "male"
    }
    res_senior = match_all_jobs(profile_senior)
    print(f"\nTest 5 [33-Year-Old UR Candidate]:")
    print(f"  Eligible: {len(res_senior['eligible'])} jobs")
    eligible_senior_ids = [j["job_id"] for j in res_senior["eligible"]]
    ineligible_senior_ids = [j["job_id"] for j in res_senior["ineligible"]]
    assert "ssc-cgl" in ineligible_senior_ids, "SSC CGL max age 30 should block 33yo UR"
    assert "ibps-po" in ineligible_senior_ids, "IBPS PO max age 30 should block 33yo UR"
    assert "state-psc-uppsc-pcs" in eligible_senior_ids, "UPPSC PCS max age 40 should allow 33yo UR"
    assert "india-post-gds" in eligible_senior_ids, "India Post GDS max age 40 should allow 33yo UR"
    print("  [PASS]")

    print("\n==================================================")
    print("ALL TESTS PASSED SUCCESSFULLY! (100% Deterministic Accuracy)")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
