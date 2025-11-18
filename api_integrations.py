import asyncio
import random
from datetime import datetime, timedelta

# --- MOCK API INTEGRATIONS ---
# No keys required. Safe for Hackathon Demos.

def extract_pan_from_gstin(gstin: str) -> str:
    """Extract PAN from GSTIN (positions 2-11)"""
    if len(gstin) >= 15:
        return gstin[2:12].upper()
    return "ABCDE1234F"

async def fetch_gstn_data(gstin: str) -> dict:
    """MOCK GSTN DATA GENERATOR"""
    # 1. Fake a small delay to look like a real network call
    await asyncio.sleep(0.8)
    
    # 2. Generate realistic random data
    registration_date = datetime.now() - timedelta(days=random.randint(10, 1500))
    status = random.choice(["Active", "Active", "Active", "Suspended", "Cancelled"])
    trade_name = f"Demo Trader {gstin[:4]}"
    
    return {
        "gstin": gstin,
        "legal_name": f"Demo Enterprise {gstin[:4]} Pvt Ltd",
        "trade_name": trade_name,
        "registration_date": registration_date.strftime("%Y-%m-%d"),
        "status": status,
        "taxpayer_type": "Regular",
        "gstr1_last_filed": "2024-10",
        "gstr3b_last_filed": "2024-10" if status == "Active" else "Not Filed",
        "center_jurisdiction": "Commissioner-5",
        "state_jurisdiction": "Ward-3",
        "api_timestamp": datetime.now().isoformat()
    }

async def fetch_mca_data(pan: str) -> dict:
    """MOCK MCA DATA GENERATOR"""
    await asyncio.sleep(0.6)
    company_count = random.randint(1, 25)
    
    return {
        "pan": pan,
        "director_name": f"Director {pan[:4]}",
        "total_companies": company_count,
        "active_companies": company_count - random.randint(0, 2),
        "dissolved_companies": random.randint(0, 2),
        "recent_incorporations": random.randint(0, 1),
        # Flag as risky if director is in too many companies
        "flagged_entities": 2 if company_count > 20 else 0,
        "compliance_status": "Compliant",
        "api_timestamp": datetime.now().isoformat()
    }

async def fetch_ibbi_data(pan: str) -> dict:
    """MOCK INSOLVENCY CHECK"""
    await asyncio.sleep(0.4)
    is_risky = random.choice([True, False, False, False, False]) # 20% chance of risk
    
    return {
        "pan": pan,
        "insolvency_status": "Under CIRP" if is_risky else "Clear",
        "nclt_cases": 1 if is_risky else 0,
        "ibbi_registered": False,
        "api_timestamp": datetime.now().isoformat()
    }

async def fetch_udyam_data(gstin: str) -> dict:
    """MOCK MSME CHECK"""
    await asyncio.sleep(0.3)
    return {
        "gstin": gstin,
        "udyam_registered": True,
        "msme_category": random.choice(["Micro", "Small", "Medium"]),
        "registration_date": "2021-05-20",
        "api_timestamp": datetime.now().isoformat()
    }

async def run_all_checks(gstin: str) -> dict:
    """Orchestrate all mock checks"""
    pan = extract_pan_from_gstin(gstin)
    
    # In real code we would use asyncio.gather, but sequential is safer for mock
    gstn = await fetch_gstn_data(gstin)
    mca = await fetch_mca_data(pan)
    ibbi = await fetch_ibbi_data(pan)
    udyam = await fetch_udyam_data(gstin)
    
    return {
        "gstin_data": gstn,
        "mca_data": mca,
        "ibbi_data": ibbi,
        "udyam_data": udyam,
        "pan_extracted": pan,
        "check_timestamp": datetime.now().isoformat()
    }

def check_vendor_apis(gstin: str) -> dict:
    """Sync wrapper for Streamlit to call"""
    return asyncio.run(run_all_checks(gstin))
    
