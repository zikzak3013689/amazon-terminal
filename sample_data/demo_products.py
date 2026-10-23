"""
Demonstration Data Module for Amazon India Research Terminal.
Provides 10 realistic, fully-populated Indian e-commerce private label demonstration products.
Every record is visibly tagged with [DEMO - Fictional Demonstration Data] and is_demo = 1.
"""

from typing import List, Dict, Any
from database.repository import ProductRepository
from calculators.profit_calculator import ProfitCalculator
from modules.validation_checklist import ValidationChecklistEngine
from scoring.opportunity_scorer import OpportunityScorer

DEMO_PRODUCTS = [
    {
        "title": "[DEMO DATA] Stainless Steel Double-Wall Insulated Chai Flask (500ml)",
        "asin": "B09DEMO001",
        "product_url": "https://www.amazon.in/dp/B09DEMO001",
        "category": "Kitchen & Dining",
        "subcategory": "Vacuum Flasks",
        "main_keyword": "insulated chai flask 500ml",
        "brand": "ChaiTherma",
        "current_observed_price": 799.0,
        "review_count": 340,
        "average_rating": 4.3,
        "bestseller_rank": 1420,
        "weight_kg": 0.42,
        "length_cm": 25.0,
        "width_cm": 8.0,
        "height_cm": 8.0,
        "estimated_demand_notes": "Google India searches: 14,800/mo. Steady winter demand peak with strong year-round office usage.",
        "competition_notes": "Incumbent brands like Milton/Borosil have high reviews, but lack specialized narrow-mouth chai spouts.",
        "research_status": "Shortlisted",
        "is_demo": 1,
        "competitors": [
            {
                "competitor_asin": "B08COMP01A",
                "competitor_title": "ThermoCraft 500ml Vacuum Bottle",
                "brand": "ThermoCraft",
                "observed_price": 849.0,
                "rating": 4.1,
                "review_count": 520,
                "bsr": 1150,
                "seller_name": "CloudRetail IN",
                "fulfilment_type": "FBA",
                "weaknesses": "Lid gasket loosens after 2 months causing hot chai leaks in office bags.",
                "differentiation_angle": "Include food-grade silicone leakproof seal with 1 spare gasket."
            },
            {
                "competitor_asin": "B08COMP01B",
                "competitor_title": "HotPot Flask Standard 500ml",
                "brand": "HotPot",
                "observed_price": 699.0,
                "rating": 3.9,
                "review_count": 180,
                "bsr": 2300,
                "seller_name": "MetroSupplies",
                "fulfilment_type": "Easy Ship",
                "weaknesses": "Thin exterior paint scratches easily during daily commute.",
                "differentiation_angle": "Use matte powder-coated fingerprint resistant finish."
            },
            {
                "competitor_asin": "B08COMP01C",
                "competitor_title": "Apex Insulated Beverage Tumbler",
                "brand": "Apex",
                "observed_price": 999.0,
                "rating": 4.4,
                "review_count": 890,
                "bsr": 920,
                "seller_name": "Apex Direct",
                "fulfilment_type": "FBA",
                "weaknesses": "High price; no infuser basket for CTC tea leaves.",
                "differentiation_angle": "Add removable 304 SS mesh tea infuser basket for ₹40 extra cost."
            }
        ],
        "supplier": {
            "supplier_name": "Rajkot Precision Metals & Flasks Ltd",
            "supplier_country": "India",
            "supplier_city_hub": "Rajkot, Gujarat (Kitchenware & Hardware)",
            "unit_purchase_cost": 210.0,
            "currency": "INR",
            "moq": 200,
            "packaging_cost": 25.0,
            "production_lead_time_days": 18,
            "defect_allowance_pct": 2.0,
            "tax_rate_pct": 18.0,
            "is_tax_recoverable_itc": 1,
            "freight_cost_per_unit": 15.0,
            "notes": "Verified ISO9001 factory in Rajkot GIDC. Food-grade SS304 test certificate included."
        },
        "keywords": [
            {"keyword": "insulated chai flask", "volume": 14800, "cpc_low": 12.0, "cpc_high": 24.0},
            {"keyword": "tea flask 500ml for office", "volume": 6200, "cpc_low": 9.5, "cpc_high": 18.0},
            {"keyword": "hot tea thermos bottle", "volume": 4100, "cpc_low": 8.0, "cpc_high": 15.0}
        ]
    },
    {
        "title": "[DEMO DATA] Ergonomic Neem Wood Laptop Stand with Heat Dissipation",
        "asin": "B09DEMO002",
        "product_url": "https://www.amazon.in/dp/B09DEMO002",
        "category": "Office Products & Stationery",
        "subcategory": "Laptop Accessories",
        "main_keyword": "wooden laptop stand ergonomic",
        "brand": "Vrikshika",
        "current_observed_price": 649.0,
        "review_count": 145,
        "average_rating": 4.4,
        "bestseller_rank": 2100,
        "weight_kg": 0.48,
        "length_cm": 28.0,
        "width_cm": 24.0,
        "height_cm": 3.5,
        "estimated_demand_notes": "Demand driven by WFH & IT professionals seeking eco-friendly desk setups.",
        "competition_notes": "Most sellers offer cheap aluminium or MDF board stands that wobble.",
        "research_status": "Shortlisted",
        "is_demo": 1,
        "competitors": [
            {
                "competitor_asin": "B08COMP02A",
                "competitor_title": "EcoWood Portable Riser",
                "brand": "EcoWood",
                "observed_price": 699.0,
                "rating": 4.2,
                "review_count": 210,
                "bsr": 1850,
                "seller_name": "CraftLogistics",
                "fulfilment_type": "FBA",
                "weaknesses": "Rough edges scratch laptop wrists; lacks anti-slip silicone pads.",
                "differentiation_angle": "Hand-buffed smooth finish with 4 recessed silicone grip pads."
            },
            {
                "competitor_asin": "B08COMP02B",
                "competitor_title": "MetalTech Aluminium Stand",
                "brand": "MetalTech",
                "observed_price": 599.0,
                "rating": 3.8,
                "review_count": 1200,
                "bsr": 850,
                "seller_name": "TechDeals",
                "fulfilment_type": "FBA",
                "weaknesses": "Cold metallic aesthetic; heavy carbon footprint.",
                "differentiation_angle": "Position as natural, anti-bacterial Indian Neem wood artisan product."
            }
        ],
        "supplier": {
            "supplier_name": "Jodhpur Heritage Woodcrafts",
            "supplier_country": "India",
            "supplier_city_hub": "Jodhpur / Saharanpur (Wooden Furniture & Decor)",
            "unit_purchase_cost": 160.0,
            "currency": "INR",
            "moq": 150,
            "packaging_cost": 18.0,
            "production_lead_time_days": 14,
            "defect_allowance_pct": 2.5,
            "tax_rate_pct": 12.0,
            "is_tax_recoverable_itc": 1,
            "freight_cost_per_unit": 20.0,
            "notes": "Seasoned neem wood with termite-proof natural oil polish."
        },
        "keywords": [
            {"keyword": "wooden laptop stand", "volume": 18100, "cpc_low": 11.0, "cpc_high": 22.0},
            {"keyword": "ergonomic laptop riser wood", "volume": 4400, "cpc_low": 8.0, "cpc_high": 16.0}
        ]
    },
    {
        "title": "[DEMO DATA] Traditional Brass Agarbatti Stand with Ash Catcher & Glass Cover",
        "asin": "B09DEMO003",
        "product_url": "https://www.amazon.in/dp/B09DEMO003",
        "category": "Home Decor",
        "subcategory": "Puja Articles",
        "main_keyword": "brass agarbatti stand with ash catcher",
        "brand": "Pavitram Crafts",
        "current_observed_price": 549.0,
        "review_count": 280,
        "average_rating": 4.5,
        "bestseller_rank": 850,
        "weight_kg": 0.35,
        "length_cm": 12.0,
        "width_cm": 12.0,
        "height_cm": 26.0,
        "estimated_demand_notes": "High year-round spiritual demand in India with explosive festive surges during Diwali/Navratri.",
        "competition_notes": "Open stands scatter ash everywhere; glass-covered safety stands command 40% margin.",
        "research_status": "Approved for Small Test",
        "is_demo": 1,
        "competitors": [
            {
                "competitor_asin": "B08COMP03A",
                "competitor_title": "DivinePooja Glass Incense Tower",
                "brand": "DivinePooja",
                "observed_price": 599.0,
                "rating": 4.2,
                "review_count": 650,
                "bsr": 620,
                "seller_name": "PoojaMart",
                "fulfilment_type": "FBA",
                "weaknesses": "Thin borosilicate glass cracks during transit due to poor thermocol packing.",
                "differentiation_angle": "Use custom high-density EPE foam moulding box with zero breakage."
            }
        ],
        "supplier": {
            "supplier_name": "Moradabad Brass & Handicrafts Guild",
            "supplier_country": "India",
            "supplier_city_hub": "Moradabad, UP (Brass, Copper, Metal Crafts)",
            "unit_purchase_cost": 140.0,
            "currency": "INR",
            "moq": 100,
            "packaging_cost": 22.0,
            "production_lead_time_days": 12,
            "defect_allowance_pct": 1.5,
            "tax_rate_pct": 12.0,
            "is_tax_recoverable_itc": 1,
            "freight_cost_per_unit": 18.0,
            "notes": "Solid brass base with lacquer polish to prevent blackening."
        },
        "keywords": [
            {"keyword": "brass agarbatti stand", "volume": 22000, "cpc_low": 7.0, "cpc_high": 15.0},
            {"keyword": "incense holder with glass cover", "volume": 8900, "cpc_low": 9.0, "cpc_high": 19.0}
        ]
    },
    {
        "title": "[DEMO DATA] Ayurvedic Pure Copper Hammered Water Bottle (1000ml)",
        "asin": "B09DEMO004",
        "product_url": "https://www.amazon.in/dp/B09DEMO004",
        "category": "Sports, Fitness & Outdoors",
        "subcategory": "Water Bottles",
        "main_keyword": "pure copper water bottle 1 litre",
        "brand": "TamraShuddhi",
        "current_observed_price": 899.0,
        "review_count": 410,
        "average_rating": 4.2,
        "bestseller_rank": 1650,
        "weight_kg": 0.38,
        "length_cm": 28.0,
        "width_cm": 9.0,
        "height_cm": 9.0,
        "estimated_demand_notes": "Evergreen wellness category in India driven by Ayurvedic health benefits.",
        "competition_notes": "Buyers complain about joint leaks and bitter smell; seamless spun copper solves this.",
        "research_status": "Shortlisted",
        "is_demo": 1,
        "competitors": [
            {
                "competitor_asin": "B08COMP04A",
                "competitor_title": "AyurVeda Copper Flask 1000ml",
                "brand": "AyurLife",
                "observed_price": 849.0,
                "rating": 4.0,
                "review_count": 780,
                "bsr": 1300,
                "seller_name": "WellnessHub",
                "fulfilment_type": "FBA",
                "weaknesses": "Lid threads squeak loudly and stick when tightening.",
                "differentiation_angle": "Precision brass threaded cap with smooth food-grade ring."
            }
        ],
        "supplier": {
            "supplier_name": "Mathura Copper Utensils Cluster",
            "supplier_country": "India",
            "supplier_city_hub": "Mathura / Moradabad, UP",
            "unit_purchase_cost": 290.0,
            "currency": "INR",
            "moq": 150,
            "packaging_cost": 25.0,
            "production_lead_time_days": 15,
            "defect_allowance_pct": 2.0,
            "tax_rate_pct": 18.0,
            "is_tax_recoverable_itc": 1,
            "freight_cost_per_unit": 22.0,
            "notes": "99.2% laboratory tested pure copper sheet."
        },
        "keywords": [
            {"keyword": "pure copper water bottle 1 litre", "volume": 27100, "cpc_low": 14.0, "cpc_high": 28.0},
            {"keyword": "hammered copper bottle", "volume": 7300, "cpc_low": 10.0, "cpc_high": 20.0}
        ]
    },
    {
        "title": "[DEMO DATA] Extra-Thick Microfiber Kitchen Dish Drying Mat (Pack of 2)",
        "asin": "B09DEMO005",
        "product_url": "https://www.amazon.in/dp/B09DEMO005",
        "category": "Home & Kitchen",
        "subcategory": "Kitchen Linen",
        "main_keyword": "kitchen dish drying mat microfiber",
        "brand": "DryNest",
        "current_observed_price": 399.0,
        "review_count": 195,
        "average_rating": 4.4,
        "bestseller_rank": 1980,
        "weight_kg": 0.25,
        "length_cm": 30.0,
        "width_cm": 20.0,
        "height_cm": 3.0,
        "estimated_demand_notes": "Growing Indian modular kitchen trend replacing bulky plastic drainer trays.",
        "competition_notes": "Single mats sell for ₹299; pack of 2 at ₹399 offers unbeatable value perception.",
        "research_status": "Shortlisted",
        "is_demo": 1,
        "competitors": [
            {
                "competitor_asin": "B08COMP05A",
                "competitor_title": "QuickDry Single Counter Mat",
                "brand": "QuickDry",
                "observed_price": 299.0,
                "rating": 4.1,
                "review_count": 310,
                "bsr": 2400,
                "seller_name": "HomeLinen Direct",
                "fulfilment_type": "Easy Ship",
                "weaknesses": "Thin foam core stays damp and develops mildew odor.",
                "differentiation_angle": "Honeycomb mesh backing with 450 GSM microfiber for 3x faster drying."
            }
        ],
        "supplier": {
            "supplier_name": "Surat Microfiber Weaving Mills",
            "supplier_country": "India",
            "supplier_city_hub": "Surat, Gujarat (Textiles, Apparel, Packaging)",
            "unit_purchase_cost": 85.0, # for pack of 2
            "currency": "INR",
            "moq": 300,
            "packaging_cost": 15.0,
            "production_lead_time_days": 10,
            "defect_allowance_pct": 1.0,
            "tax_rate_pct": 5.0,
            "is_tax_recoverable_itc": 1,
            "freight_cost_per_unit": 12.0,
            "notes": "Direct textile manufacturer in Surat Ring Road cluster."
        },
        "keywords": [
            {"keyword": "dish drying mat for kitchen", "volume": 12100, "cpc_low": 5.5, "cpc_high": 12.0},
            {"keyword": "microfiber utensil drying mat", "volume": 5800, "cpc_low": 4.5, "cpc_high": 9.5}
        ]
    },
    {
        "title": "[DEMO DATA] Magnetic Car Phone Mount with 360° Metal Arm for Indian Roads",
        "asin": "B09DEMO006",
        "product_url": "https://www.amazon.in/dp/B09DEMO006",
        "category": "Car & Motorbike Accessories",
        "subcategory": "Mobile Accessories",
        "main_keyword": "magnetic car phone holder dashboard",
        "brand": "RoadGrip",
        "current_observed_price": 499.0,
        "review_count": 620,
        "average_rating": 4.3,
        "bestseller_rank": 780,
        "weight_kg": 0.18,
        "length_cm": 10.0,
        "width_cm": 8.0,
        "height_cm": 4.0,
        "estimated_demand_notes": "High recurring volume from Uber/Ola drivers and commuters.",
        "competition_notes": "Potholes in India cause weak magnets to drop phones; 6x N52 neodymium magnets needed.",
        "research_status": "Shortlisted",
        "is_demo": 1,
        "competitors": [
            {
                "competitor_asin": "B08COMP06A",
                "competitor_title": "DriveSafe MagHolder",
                "brand": "DriveSafe",
                "observed_price": 449.0,
                "rating": 3.9,
                "review_count": 1450,
                "bsr": 510,
                "seller_name": "AutoTrendz",
                "fulfilment_type": "FBA",
                "weaknesses": "Adhesive tape melts in Indian summer parked cars (45°C+).",
                "differentiation_angle": "Use authentic 3M VHB heat-resistant automotive adhesive tape."
            }
        ],
        "supplier": {
            "supplier_name": "Shenzhen Precision Auto Tech (via Indian Importer Partner)",
            "supplier_country": "China",
            "supplier_city_hub": "Shenzhen / Delhi Clearing Port",
            "unit_purchase_cost": 115.0,
            "currency": "INR",
            "moq": 500,
            "packaging_cost": 15.0,
            "production_lead_time_days": 25,
            "defect_allowance_pct": 2.0,
            "tax_rate_pct": 18.0,
            "is_tax_recoverable_itc": 1,
            "freight_cost_per_unit": 25.0,
            "notes": "Custom alloy zinc casing with N52 magnets."
        },
        "keywords": [
            {"keyword": "car phone holder magnetic", "volume": 33100, "cpc_low": 12.0, "cpc_high": 25.0},
            {"keyword": "dashboard mobile stand for car", "volume": 18400, "cpc_low": 9.0, "cpc_high": 19.0}
        ]
    },
    {
        "title": "[DEMO DATA] Natural Sisal Fiber Body Exfoliating Dry Brush with Long Handle",
        "asin": "B09DEMO007",
        "product_url": "https://www.amazon.in/dp/B09DEMO007",
        "category": "Beauty & Personal Care",
        "subcategory": "Bath Accessories",
        "main_keyword": "body dry brush for lymphatic drainage",
        "brand": "AyurGlow",
        "current_observed_price": 449.0,
        "review_count": 110,
        "average_rating": 4.6,
        "bestseller_rank": 2900,
        "weight_kg": 0.22,
        "length_cm": 38.0,
        "width_cm": 9.0,
        "height_cm": 4.0,
        "estimated_demand_notes": "High traction on Instagram/YouTube reels regarding skin exfoliation and circulation.",
        "competition_notes": "Synthetic nylon bristles scratch skin; natural sisal bristles command strong repeat loyalty.",
        "research_status": "Shortlisted",
        "is_demo": 1,
        "competitors": [
            {
                "competitor_asin": "B08COMP07A",
                "competitor_title": "GlowSkin Wooden Body Brush",
                "brand": "GlowSkin",
                "observed_price": 499.0,
                "rating": 4.3,
                "review_count": 380,
                "bsr": 2100,
                "seller_name": "BeautyNest",
                "fulfilment_type": "FBA",
                "weaknesses": "Fixed head cannot reach lower back comfortably.",
                "differentiation_angle": "Detachable brush head with palm strap + 15-inch ergonomic curved handle."
            }
        ],
        "supplier": {
            "supplier_name": "Kerala Coir & Sisal Natural Fibers",
            "supplier_country": "India",
            "supplier_city_hub": "Alappuzha, Kerala (Coir & Natural Fibers)",
            "unit_purchase_cost": 95.0,
            "currency": "INR",
            "moq": 150,
            "packaging_cost": 15.0,
            "production_lead_time_days": 12,
            "defect_allowance_pct": 2.0,
            "tax_rate_pct": 5.0,
            "is_tax_recoverable_itc": 1,
            "freight_cost_per_unit": 16.0,
            "notes": "100% biodegradable lotus wood base with untreated sisal."
        },
        "keywords": [
            {"keyword": "body brush for dry brushing", "volume": 15600, "cpc_low": 8.0, "cpc_high": 18.0},
            {"keyword": "exfoliating back scrubber long handle", "volume": 7200, "cpc_low": 6.5, "cpc_high": 14.0}
        ]
    },
    {
        "title": "[DEMO DATA] Waterproof Expandable Travel Cable & Tech Organizer Pouch",
        "asin": "B09DEMO008",
        "product_url": "https://www.amazon.in/dp/B09DEMO008",
        "category": "Bags & Luggage",
        "subcategory": "Travel Accessories",
        "main_keyword": "electronic travel cable organizer bag",
        "brand": "PackSmart IN",
        "current_observed_price": 499.0,
        "review_count": 230,
        "average_rating": 4.4,
        "bestseller_rank": 1820,
        "weight_kg": 0.20,
        "length_cm": 24.0,
        "width_cm": 16.0,
        "height_cm": 5.0,
        "estimated_demand_notes": "Surging domestic leisure travel & corporate trips in India post-pandemic.",
        "competition_notes": "Generic black pouches lack padded dividers for heavy Indian 65W GaN fast chargers.",
        "research_status": "Shortlisted",
        "is_demo": 1,
        "competitors": [
            {
                "competitor_asin": "B08COMP08A",
                "competitor_title": "TechKit Basic Cable Bag",
                "brand": "TechKit",
                "observed_price": 429.0,
                "rating": 4.0,
                "review_count": 540,
                "bsr": 1600,
                "seller_name": "GadgetWorld",
                "fulfilment_type": "FBA",
                "weaknesses": "Flimsy zipper jams when stuffed with power banks.",
                "differentiation_angle": "Use YKK dual zippers and thick water-repellent jacquard nylon fabric."
            }
        ],
        "supplier": {
            "supplier_name": "Kanpur & Delhi Luggage Works",
            "supplier_country": "India",
            "supplier_city_hub": "Delhi-NCR / Kanpur (Bags & Luggage)",
            "unit_purchase_cost": 110.0,
            "currency": "INR",
            "moq": 200,
            "packaging_cost": 12.0,
            "production_lead_time_days": 14,
            "defect_allowance_pct": 2.0,
            "tax_rate_pct": 12.0,
            "is_tax_recoverable_itc": 1,
            "freight_cost_per_unit": 14.0,
            "notes": "Custom internal elastic loops and padded velcro dividers."
        },
        "keywords": [
            {"keyword": "cable organizer travel bag", "volume": 19400, "cpc_low": 9.0, "cpc_high": 19.5},
            {"keyword": "gadget pouch for travel", "volume": 6800, "cpc_low": 7.0, "cpc_high": 14.0}
        ]
    },
    {
        "title": "[DEMO DATA] Orthopedic Memory Foam Lumbar Support Cushion for Office Chairs",
        "asin": "B09DEMO009",
        "product_url": "https://www.amazon.in/dp/B09DEMO009",
        "category": "Health & Household",
        "subcategory": "Back Care",
        "main_keyword": "orthopedic backrest cushion for chair",
        "brand": "SpineRest",
        "current_observed_price": 999.0,
        "review_count": 510,
        "average_rating": 4.3,
        "bestseller_rank": 950,
        "weight_kg": 0.72,
        "length_cm": 36.0,
        "width_cm": 32.0,
        "height_cm": 10.0,
        "estimated_demand_notes": "High awareness of back pain among desk workers and long-distance drivers.",
        "competition_notes": "Standard memory foam gets hot and sweaty in Indian climate; 3D air-mesh cover is key.",
        "research_status": "Shortlisted",
        "is_demo": 1,
        "competitors": [
            {
                "competitor_asin": "B08COMP09A",
                "competitor_title": "ErgoBack Memory Pillow",
                "brand": "ErgoBack",
                "observed_price": 1099.0,
                "rating": 4.2,
                "review_count": 1150,
                "bsr": 720,
                "seller_name": "ComfortZone",
                "fulfilment_type": "FBA",
                "weaknesses": "Single buckle strap slides down chair during use.",
                "differentiation_angle": "Dual adjustable straps with extension belt fitting all car seats & high-back executive chairs."
            }
        ],
        "supplier": {
            "supplier_name": "Bengaluru PU Foam & Cushion Dynamics",
            "supplier_country": "India",
            "supplier_city_hub": "Bengaluru / Hosur (PU Foam & Molded Cushioning)",
            "unit_purchase_cost": 275.0,
            "currency": "INR",
            "moq": 150,
            "packaging_cost": 30.0,
            "production_lead_time_days": 15,
            "defect_allowance_pct": 2.0,
            "tax_rate_pct": 18.0,
            "is_tax_recoverable_itc": 1,
            "freight_cost_per_unit": 35.0,
            "notes": "50D high-density slow-rebound molded memory foam (not shredded foam)."
        },
        "keywords": [
            {"keyword": "lumbar support cushion for office chair", "volume": 24500, "cpc_low": 13.0, "cpc_high": 27.0},
            {"keyword": "orthopedic back rest for car", "volume": 11200, "cpc_low": 10.5, "cpc_high": 22.0}
        ]
    },
    {
        "title": "[DEMO DATA] Montessori Wooden Geometric Sorting & Stacking Toy for Toddlers",
        "asin": "B09DEMO010",
        "product_url": "https://www.amazon.in/dp/B09DEMO010",
        "category": "Toys & Games",
        "subcategory": "Early Development Toys",
        "main_keyword": "wooden sorting and stacking toy toddlers",
        "brand": "KiddieKrafts",
        "current_observed_price": 499.0,
        "review_count": 320,
        "average_rating": 4.6,
        "bestseller_rank": 1100,
        "weight_kg": 0.45,
        "length_cm": 18.0,
        "width_cm": 18.0,
        "height_cm": 6.0,
        "estimated_demand_notes": "Parents actively seeking screen-free wooden toys with BIS safety compliance.",
        "competition_notes": "Plastic toys are disliked by conscious millennial parents; water-based organic paints required.",
        "research_status": "Approved for Small Test",
        "is_demo": 1,
        "competitors": [
            {
                "competitor_asin": "B08COMP10A",
                "competitor_title": "PlayWood Shape Sorter",
                "brand": "PlayWood",
                "observed_price": 549.0,
                "rating": 4.4,
                "review_count": 480,
                "bsr": 950,
                "seller_name": "ToyStore IN",
                "fulfilment_type": "FBA",
                "weaknesses": "Paint chips off when toddlers mouth pieces.",
                "differentiation_angle": "Certified non-toxic water-based German organic dyes with BIS IS 9873 toy test certificate."
            }
        ],
        "supplier": {
            "supplier_name": "Channapatna Wooden Toys Artisans Cooperative",
            "supplier_country": "India",
            "supplier_city_hub": "Channapatna, Karnataka (GI-Tagged Toy Town)",
            "unit_purchase_cost": 130.0,
            "currency": "INR",
            "moq": 100,
            "packaging_cost": 20.0,
            "production_lead_time_days": 14,
            "defect_allowance_pct": 2.0,
            "tax_rate_pct": 12.0,
            "is_tax_recoverable_itc": 1,
            "freight_cost_per_unit": 18.0,
            "notes": "GI-tagged eco-friendly natural wood and vegetable lacquer."
        },
        "keywords": [
            {"keyword": "montessori wooden toys for 2 year old", "volume": 28400, "cpc_low": 11.0, "cpc_high": 24.0},
            {"keyword": "wooden shape sorter stacking toy", "volume": 9200, "cpc_low": 8.0, "cpc_high": 17.5}
        ]
    }
]

def load_demo_data(force_refresh: bool = False):
    """
    Populates the database with 10 high-quality Amazon India demonstration products,
    including suppliers, competitors, profit calculations, validation checks, and opportunity scores.
    """
    existing_demo = ProductRepository.list_products(is_demo=1)
    if existing_demo and not force_refresh:
        return len(existing_demo)

    if force_refresh and existing_demo:
        for p in existing_demo:
            ProductRepository.delete_product(p["id"])

    created_count = 0
    for p_data in DEMO_PRODUCTS:
        # Create product
        prod_payload = {
            "title": p_data["title"],
            "asin": p_data["asin"],
            "product_url": p_data["product_url"],
            "marketplace": "amazon.in",
            "category": p_data["category"],
            "subcategory": p_data.get("subcategory"),
            "main_keyword": p_data["main_keyword"],
            "brand": p_data["brand"],
            "current_observed_price": p_data["current_observed_price"],
            "review_count": p_data["review_count"],
            "average_rating": p_data["average_rating"],
            "bestseller_rank": p_data["bestseller_rank"],
            "weight_kg": p_data["weight_kg"],
            "length_cm": p_data["length_cm"],
            "width_cm": p_data["width_cm"],
            "height_cm": p_data["height_cm"],
            "estimated_demand_notes": p_data["estimated_demand_notes"],
            "competition_notes": p_data["competition_notes"],
            "research_status": p_data["research_status"],
            "is_demo": 1
        }
        product_id = ProductRepository.create_product(prod_payload)

        # Competitors
        competitors_list = []
        for c in p_data.get("competitors", []):
            cid = ProductRepository.add_competitor(product_id, c)
            c["id"] = cid
            competitors_list.append(c)

        # Supplier
        supp = p_data.get("supplier", {})
        if supp:
            supp["is_primary_supplier"] = 1
            ProductRepository.add_supplier_quote(product_id, supp)

        # Keywords & Observations
        for kw in p_data.get("keywords", []):
            ProductRepository.add_keyword(product_id, kw["keyword"], keyword_type="long-tail")
            ProductRepository.add_keyword_observation(product_id, {
                "keyword": kw["keyword"],
                "source_platform": "Google Keyword Planner",
                "search_volume": kw["volume"],
                "cpc_bid_low": kw["cpc_low"],
                "cpc_bid_high": kw["cpc_high"],
                "geo_location": "India",
                "data_type": "estimated",
                "notes": "Demonstration Keyword Planner data for India"
            })

        # Google Trends relative interest observation
        ProductRepository.add_keyword_observation(product_id, {
            "keyword": p_data["main_keyword"],
            "source_platform": "Google Trends",
            "relative_interest_score": 68,
            "geo_location": "India",
            "timeframe": "Past 12 Months",
            "data_type": "estimated",
            "notes": "Demonstration Google Trends interest score"
        })

        # Calculate Landed Cost and Profit Scenarios
        total_landed = supp["unit_purchase_cost"] + supp.get("packaging_cost", 0) + supp.get("freight_cost_per_unit", 0)
        scenarios = ProfitCalculator.generate_three_scenarios(
            base_price=p_data["current_observed_price"],
            base_sourcing=total_landed,
            category=p_data["category"],
            weight_kg=p_data["weight_kg"],
            length_cm=p_data["length_cm"],
            width_cm=p_data["width_cm"],
            height_cm=p_data["height_cm"],
            fulfilment_model="FBA",
            gst_rate=0.18,
            is_gst_registered=True,
            monthly_units=120
        )
        for sname, s in scenarios.items():
            ProductRepository.save_profit_scenario(product_id, s)

        # Initialize and evaluate Validation Checklist
        checks = ValidationChecklistEngine.initialize_checklist_for_product(product_id)
        # Mark compliant checks as Pass
        for check in checks:
            if check["check_key"] in ["trademark_safety", "patent_safety", "restricted_category", "demand_evidence", "sourcing_availability", "india_compliance"]:
                check["status"] = "Pass"
                check["evidence_source"] = "Pre-screened Demo Verification"
                check["notes"] = "Verified safe for Amazon India marketplace demonstration."
                ProductRepository.save_validation_check(product_id, check)

        updated_checks = ValidationChecklistEngine.evaluate_automated_signals(
            prod_payload | {"id": product_id},
            competitors_list,
            scenarios["Base"]
        )

        # Score Opportunity
        score_res = OpportunityScorer.score_product(
            prod_payload | {"id": product_id},
            competitors_list,
            [supp],
            scenarios["Base"],
            updated_checks,
            ProductRepository.get_keyword_observations(product_id)
        )
        ProductRepository.save_opportunity_score(product_id, score_res)

        # Add initial research note
        ProductRepository.add_note(
            product_id,
            f"Fictional Demonstration Record created for {p_data['title']}. Use this record to explore Amazon India fee modeling, competitor dispersion, and opportunity scores.",
            title="Demonstration Portfolio Asset"
        )
        created_count += 1

    return created_count
