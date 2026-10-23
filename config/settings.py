"""
Configuration settings for the Amazon India Product Research Terminal.
"""

from pathlib import Path
import os

# Project Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = os.environ.get("AMAZON_DB_PATH", str(DATA_DIR / "amazon_research.db"))

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Application Meta
APP_NAME = "Amazon India Product Research Terminal"
APP_VERSION = "1.0.0"
MARKETPLACE = "amazon.in"
DEFAULT_CURRENCY = "INR"
CURRENCY_SYMBOL = "₹"

# GST Rate Categories in India
GST_RATES = {
    "0% (Exempt)": 0.00,
    "5% (Essential Goods)": 0.05,
    "12% (Standard Lower)": 0.12,
    "18% (General Goods & Services)": 0.18,
    "28% (Luxury / High Tax)": 0.28,
}
DEFAULT_GST_RATE = 0.18

# Amazon India Referral Fees (Typical base category fee percentages)
# Source: Amazon Seller Central India Fee Schedule (Baseline Reference)
AMAZON_REFERRAL_FEE_RATES = {
    "Home & Kitchen": 0.09,
    "Kitchen & Dining": 0.10,
    "Home Decor": 0.11,
    "Electronics & Accessories": 0.07,
    "Computers & Peripherals": 0.05,
    "Beauty & Personal Care": 0.08,
    "Health & Household": 0.09,
    "Clothing & Accessories": 0.13,
    "Bags & Luggage": 0.12,
    "Toys & Games": 0.095,
    "Sports, Fitness & Outdoors": 0.10,
    "Baby Products": 0.08,
    "Office Products & Stationery": 0.10,
    "Car & Motorbike Accessories": 0.11,
    "Pet Supplies": 0.10,
    "Industrial & Scientific": 0.09,
    "Books": 0.055,
    "Other Categories": 0.12,
}

# Amazon India Closing Fee Slabs (Standard FBA)
# Fee varies by item selling price band
AMAZON_CLOSING_FEE_SLABS = {
    "FBA": [
        {"min": 0, "max": 250, "fee": 5.0},
        {"min": 250.01, "max": 500, "fee": 9.0},
        {"min": 500.01, "max": 1000, "fee": 30.0},
        {"min": 1000.01, "max": 9999999, "fee": 61.0},
    ],
    "Easy Ship": [
        {"min": 0, "max": 250, "fee": 7.0},
        {"min": 250.01, "max": 500, "fee": 15.0},
        {"min": 500.01, "max": 1000, "fee": 32.0},
        {"min": 1000.01, "max": 9999999, "fee": 65.0},
    ],
    "Self Ship": [
        {"min": 0, "max": 250, "fee": 10.0},
        {"min": 250.01, "max": 500, "fee": 20.0},
        {"min": 500.01, "max": 1000, "fee": 40.0},
        {"min": 1000.01, "max": 9999999, "fee": 75.0},
    ],
}

# Fulfilment Weight Handling Fees (Per 500g slab)
WEIGHT_HANDLING_FEES = {
    "FBA": {
        "first_500g": {"local": 38.0, "regional": 48.0, "national": 68.0},
        "additional_500g_up_to_1kg": {"local": 16.0, "regional": 24.0, "national": 33.0},
        "additional_kg_above_1kg": {"local": 19.0, "regional": 28.0, "national": 38.0},
        "pick_and_pack": 16.0,
    },
    "Easy Ship": {
        "first_500g": {"local": 44.0, "regional": 54.0, "national": 74.0},
        "additional_500g_up_to_1kg": {"local": 18.0, "regional": 27.0, "national": 36.0},
        "additional_kg_above_1kg": {"local": 21.0, "regional": 30.0, "national": 40.0},
        "pick_and_pack": 0.0,
    },
    "Self Ship": {
        "first_500g": {"local": 0.0, "regional": 0.0, "national": 0.0},
        "additional_500g_up_to_1kg": {"local": 0.0, "regional": 0.0, "national": 0.0},
        "additional_kg_above_1kg": {"local": 0.0, "regional": 0.0, "national": 0.0},
        "pick_and_pack": 0.0,
    },
}

# Service Tax (GST) charged by Amazon on all marketplace seller fees
AMAZON_FEE_GST_RATE = 0.18

# Default Storage Fee per cubic foot per month in INR
STORAGE_FEE_PER_CUFT_MONTH = 45.0

# Opportunity Scoring Default Weights (Sum = 100%)
DEFAULT_SCORING_WEIGHTS = {
    "demand_evidence": 25.0,
    "competition_opportunity": 20.0,
    "profitability": 25.0,
    "market_stability": 10.0,
    "differentiation": 10.0,
    "sourcing_feasibility": 10.0,
}

# Research Statuses
RESEARCH_STATUSES = [
    "New Idea",
    "Researching",
    "Awaiting Data",
    "Shortlisted",
    "Supplier Validation",
    "Approved for Small Test",
    "Rejected",
]

# Validation Checklist Items
CHECKLIST_DEFINITIONS = [
    {
        "key": "demand_evidence",
        "category": "Demand & Market",
        "title": "Evidence of Consistent Demand",
        "description": "Evidence from Google Trends / Amazon BSR / Search queries indicating sustainable monthly demand.",
        "is_blocking": False,
    },
    {
        "key": "competition_intensity",
        "category": "Competition",
        "title": "Reasonable Competition Barrier",
        "description": "Top 10 competitors have median reviews < 500 or clear listing/quality weaknesses that can be exploited.",
        "is_blocking": False,
    },
    {
        "key": "profit_margin",
        "category": "Financials",
        "title": "Healthy Contribution Margin (≥ 25-30%)",
        "description": "Net margin after all Amazon fees, GST, and PPC ad spend is at least 25% with ROI ≥ 80%.",
        "is_blocking": True,
    },
    {
        "key": "sourcing_availability",
        "category": "Sourcing",
        "title": "Supplier Availability & Feasibility",
        "description": "At least one reliable Indian or overseas manufacturer verified with viable MOQ and lead time.",
        "is_blocking": True,
    },
    {
        "key": "product_differentiation",
        "category": "Product",
        "title": "Feasible Differentiation / Value Add",
        "description": "Can be differentiated via better material, packaging, bundled accessories, or resolved complaints.",
        "is_blocking": False,
    },
    {
        "key": "seasonality",
        "category": "Demand & Market",
        "title": "Non-Seasonal / Year-Round Sales",
        "description": "Demand is stable across 10-12 months rather than concentrated in a 2-week festival spike.",
        "is_blocking": False,
    },
    {
        "key": "packaging_complexity",
        "category": "Logistics",
        "title": "Low Packaging & Volumetric Risk",
        "description": "Product is compact, lightweight (< 1.5kg), and does not require complex assembly.",
        "is_blocking": False,
    },
    {
        "key": "fragility",
        "category": "Logistics",
        "title": "Low Transit Fragility & Breakage Risk",
        "description": "Not made of easily shatterable glass or delicate ceramics that suffer heavy transit damage.",
        "is_blocking": False,
    },
    {
        "key": "returns_risk",
        "category": "Logistics",
        "title": "Controlled Returns Exposure (< 10%)",
        "description": "Not prone to subjective fit/size issues (like shoes or tight clothing) that cause high return rates.",
        "is_blocking": False,
    },
    {
        "key": "trademark_safety",
        "category": "Legal & IP",
        "title": "Trademark Clearance (India IP Portal)",
        "description": "Main keyword and branding do not infringe registered Class trademarks on ipindiaonline.gov.in.",
        "is_blocking": True,
    },
    {
        "key": "patent_safety",
        "category": "Legal & IP",
        "title": "Patent & Design Protection Clearance",
        "description": "Does not violate active utility patents or registered industrial designs in India.",
        "is_blocking": True,
    },
    {
        "key": "restricted_category",
        "category": "Legal & Compliance",
        "title": "Unrestricted Marketplace Category",
        "description": "Does not require restricted ungating, hazardous materials clearance, or medical device approvals.",
        "is_blocking": True,
    },
    {
        "key": "india_compliance",
        "category": "Legal & Compliance",
        "title": "Indian Regulatory Compliance (BIS / FSSAI / EPR / Legal Metrology)",
        "description": "Complies with Indian packaging rules (MRP sticker, importer details), BIS certification (if electronics/toys), or EPR plastic credits.",
        "is_blocking": True,
    },
]
