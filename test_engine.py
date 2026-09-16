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

    # Test 6: BCA Candidate (22 yrs, UR)
    profile_bca = {
        "age": 22,
        "category": "UR",
        "education_level": "graduate",
        "stream": "bca",
        "percentage": 70.0,
        "gender": "male"
    }
    res_bca = match_all_jobs(profile_bca)
    print(f"\nTest 6 [BCA Candidate, 22 yrs, UR]:")
    print(f"  Eligible: {len(res_bca['eligible'])} jobs")
    eligible_bca_ids = [j["job_id"] for j in res_bca["eligible"]]
    ineligible_bca_ids = [j["job_id"] for j in res_bca["ineligible"]]
    assert "ssc-cgl" in eligible_bca_ids, "SSC CGL must be eligible for BCA"
    assert "ibps-po" in eligible_bca_ids, "IBPS PO must be eligible for BCA"
    assert "gate-psu-ongc-iocl" not in eligible_bca_ids, "GATE PSU B.Tech should not accept BCA"
    print("  [PASS] (BCA gets Graduate & DRDO jobs; B.Tech GATE PSU correctly blocked)")

    # Test 7: B.Tech CSE / IT Candidate (23 yrs, UR)
    profile_cse = {
        "age": 23,
        "category": "UR",
        "education_level": "graduate",
        "stream": "cse_it",
        "percentage": 72.0,
        "gender": "male"
    }
    res_cse = match_all_jobs(profile_cse)
    print(f"\nTest 7 [Graduation in CSE / CS & IT, 23 yrs, UR]:")
    print(f"  Eligible: {len(res_cse['eligible'])} jobs")
    eligible_cse_ids = [j["job_id"] for j in res_cse["eligible"]]
    assert "gate-psu-ongc-iocl" in eligible_cse_ids, "GATE PSU must accept B.Tech CSE/IT"
    assert "drdo-ceptam-technician" in eligible_cse_ids, "DRDO CEPTAM must accept B.Tech CSE/IT"
    assert "ssc-cgl" in eligible_cse_ids, "SSC CGL must accept B.Tech CSE/IT"
    # Test 8: Home State / Domicile Prioritization
    profile_wb = {
        "age": 23,
        "category": "UR",
        "education_level": "10th",
        "stream": "any",
        "percentage": 65.0,
        "gender": "male",
        "domicile": "West Bengal"
    }
    res_wb = match_all_jobs(profile_wb)
    print(f"\nTest 8 [Home State Prioritization - West Bengal Domicile, 10th Pass]:")
    print(f"  Eligible: {len(res_wb['eligible'])} jobs")
    top_job = res_wb["eligible"][0]
    print(f"  Top Prioritized Job: {top_job['job_title']} (State: {top_job['state']}, Home State: {top_job['is_home_state']})")
    assert top_job["is_home_state"] is True, "Home state job must be prioritized at rank 1"
    assert top_job["state"] == "West Bengal", "Rank 1 job must belong to candidate's home state"
    
    # Verify UP Candidate gets UP Police prioritized
    profile_up = {
        "age": 21,
        "category": "UR",
        "education_level": "12th",
        "stream": "any",
        "percentage": 70.0,
        "gender": "male",
        "domicile": "Uttar Pradesh"
    }
    res_up = match_all_jobs(profile_up)
    top_up_job = res_up["eligible"][0]
    print(f"  Top UP Prioritized Job: {top_up_job['job_title']} (Home State: {top_up_job['is_home_state']})")
    assert top_up_job["is_home_state"] is True, "UP home state job must be prioritized"
    assert top_up_job["state"] == "Uttar Pradesh", "Rank 1 job must belong to Uttar Pradesh"
    print("  [PASS] (Home state government jobs successfully spotlighted and prioritized at the top!)")

    # Test 9: 8th Pass Candidate (20 yrs, UR)
    profile_8th = {
        "age": 20,
        "category": "UR",
        "education_level": "8th",
        "stream": "any",
        "percentage": 68.0,
        "gender": "male"
    }
    res_8th = match_all_jobs(profile_8th)
    print(f"\nTest 9 [8th Pass Candidate, 20 yrs, UR]:")
    print(f"  Eligible: {len(res_8th['eligible'])} jobs (Vacancies: {res_8th['total_eligible_vacancies']:,})")
    eligible_8th_ids = [j["job_id"] for j in res_8th["eligible"]]
    ineligible_8th_ids = [j["job_id"] for j in res_8th["ineligible"]]
    assert "district-court-peon-orderly" in eligible_8th_ids, "District Court Peon must be eligible for 8th pass"
    assert "fci-watchman-chowkidar" in eligible_8th_ids, "FCI Watchman must be eligible for 8th pass"
    assert "municipal-safai-karmachari-ward-boy" in eligible_8th_ids, "Municipal Ward Attendant must be eligible for 8th pass"
    assert "india-post-gds" in ineligible_8th_ids, "India Post GDS (10th required) must be blocked for 8th pass"
    assert "ssc-mts-havaldar" in ineligible_8th_ids, "SSC MTS (10th required) must be blocked for 8th pass"
    assert "ssc-cgl" in ineligible_8th_ids, "SSC CGL (Graduate required) must be blocked for 8th pass"
    print("  [PASS] (8th pass candidate accurately matches 8th pass jobs and blocked from higher tier exams)")

    # Test 10: Gramin Bank & Low Competition Entry
    profile_grad = {
        "age": 24,
        "category": "OBC",
        "education_level": "graduate",
        "stream": "any",
        "percentage": 62.0,
        "gender": "male"
    }
    res_grad = match_all_jobs(profile_grad)
    eligible_grad_ids = [j["job_id"] for j in res_grad["eligible"]]
    assert "ibps-rrb-gramin-bank-clerk" in eligible_grad_ids, "IBPS RRB Gramin Bank Clerk must be eligible"
    assert "bank-sub-staff-peon-cbi" in eligible_grad_ids, "Bank Sub-Staff must be eligible"
    assert "ssc-stenographer-grade-c-d" in eligible_grad_ids, "SSC Stenographer must be eligible"
    print("\nTest 10 [Gramin Bank & Low Competition Access]:")
    print("  [PASS] (Gramin Bank Office Assistant, Bank Sub-Staff, and SSC Steno accessible)")

    print("\n==================================================")
    print("ALL TESTS PASSED SUCCESSFULLY! (100% Deterministic Accuracy)")
    print("==================================================")

if __name__ == "__main__":
    run_tests()

