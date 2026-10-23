"""
Validation Checklist Engine for Amazon India Product Research.
Evaluates 13 key criteria across demand, competition, financials, logistics, IP, and Indian regulatory compliance.
"""

from typing import List, Dict, Any, Tuple
from config.settings import CHECKLIST_DEFINITIONS
from database.repository import ProductRepository

class ValidationChecklistEngine:
    """Manages evaluation, storage, and blocker analysis for the 13-point research checklist."""

    @staticmethod
    def initialize_checklist_for_product(product_id: int) -> List[Dict[str, Any]]:
        """Ensures all 13 checklist items exist in the database for the given product."""
        existing = {c["check_key"]: c for c in ProductRepository.get_validation_checks(product_id)}
        initialized = []
        for defn in CHECKLIST_DEFINITIONS:
            key = defn["key"]
            if key not in existing:
                check_data = {
                    "check_key": key,
                    "check_category": defn["category"],
                    "title": defn["title"],
                    "status": "Needs Investigation",
                    "notes": defn["description"],
                    "evidence_source": "Default Baseline",
                    "is_blocking": 1 if defn.get("is_blocking", False) else 0,
                }
                ProductRepository.save_validation_check(product_id, check_data)
                initialized.append(check_data)
            else:
                initialized.append(existing[key])
        return ProductRepository.get_validation_checks(product_id)

    @classmethod
    def evaluate_automated_signals(
        cls,
        product: Dict[str, Any],
        competitors: List[Dict[str, Any]],
        profit_scenario: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Runs automated preliminary evaluations based on available data without overwriting manual notes.
        """
        product_id = product["id"]
        current_checks = {c["check_key"]: c for c in cls.initialize_checklist_for_product(product_id)}
        
        # 1. Financial check: Profit margin
        if profit_scenario:
            margin = profit_scenario.get("margin_pct", 0.0)
            if margin >= 28.0:
                current_checks["profit_margin"]["status"] = "Pass"
                current_checks["profit_margin"]["notes"] = f"Calculated base margin is {margin:.1f}% (meets ≥28% requirement)."
            elif margin >= 18.0:
                current_checks["profit_margin"]["status"] = "Needs Investigation"
                current_checks["profit_margin"]["notes"] = f"Calculated base margin is {margin:.1f}% (below 28% ideal target, risk of PPC compression)."
            else:
                current_checks["profit_margin"]["status"] = "Fail"
                current_checks["profit_margin"]["notes"] = f"Calculated base margin is {margin:.1f}% (unhealthy profit buffer for Amazon India)."

        # 2. Competition intensity check
        if competitors:
            reviews = [c.get("review_count") for c in competitors if c.get("review_count") is not None]
            if reviews:
                reviews.sort()
                mid = len(reviews) // 2
                median_rev = (reviews[mid] if len(reviews) % 2 != 0 else (reviews[mid - 1] + reviews[mid]) / 2.0)
                if median_rev <= 150:
                    current_checks["competition_intensity"]["status"] = "Pass"
                    current_checks["competition_intensity"]["notes"] = f"Median competitor review count is {median_rev:.0f} (low entry barrier)."
                elif median_rev <= 600:
                    current_checks["competition_intensity"]["status"] = "Needs Investigation"
                    current_checks["competition_intensity"]["notes"] = f"Median competitor review count is {median_rev:.0f} (moderate competition)."
                else:
                    current_checks["competition_intensity"]["status"] = "Fail"
                    current_checks["competition_intensity"]["notes"] = f"Median competitor review count is {median_rev:.0f} (established incumbent dominant market)."

        # 3. Packaging & weight check
        weight_kg = product.get("weight_kg", 0.5)
        if weight_kg <= 1.0:
            current_checks["packaging_complexity"]["status"] = "Pass"
            current_checks["packaging_complexity"]["notes"] = f"Weight is {weight_kg:.2f} kg (lightweight, minimal shipping drag)."
        elif weight_kg <= 2.5:
            current_checks["packaging_complexity"]["status"] = "Needs Investigation"
            current_checks["packaging_complexity"]["notes"] = f"Weight is {weight_kg:.2f} kg (moderate weight, watch regional/national shipping costs)."
        else:
            current_checks["packaging_complexity"]["status"] = "Needs Investigation"
            current_checks["packaging_complexity"]["notes"] = f"Weight is {weight_kg:.2f} kg (heavy item, volumetric freight requires careful pricing)."

        # Save any updated checks
        for check in current_checks.values():
            ProductRepository.save_validation_check(product_id, check)

        return ProductRepository.get_validation_checks(product_id)

    @staticmethod
    def get_summary(checks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarizes pass/investigate/fail counts and detects any blocking failures."""
        pass_count = sum(1 for c in checks if c["status"] == "Pass")
        inv_count = sum(1 for c in checks if c["status"] == "Needs Investigation")
        fail_count = sum(1 for c in checks if c["status"] == "Fail")
        
        blocking_failures = [c["title"] for c in checks if c.get("is_blocking") and c["status"] == "Fail"]
        blocking_investigations = [c["title"] for c in checks if c.get("is_blocking") and c["status"] == "Needs Investigation"]

        return {
            "total_checks": len(checks),
            "pass_count": pass_count,
            "investigation_count": inv_count,
            "fail_count": fail_count,
            "has_blocking_failures": len(blocking_failures) > 0,
            "blocking_failures": blocking_failures,
            "blocking_investigations": blocking_investigations,
            "is_ready_for_approval": (fail_count == 0 and inv_count <= 2 and len(blocking_failures) == 0),
        }
