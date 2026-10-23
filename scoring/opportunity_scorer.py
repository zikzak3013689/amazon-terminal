"""
Transparent 100-Point Opportunity Scoring Engine for Amazon India.
Configurable weights, confidence grading, explicit missing-data penalties,
and separate blocking risk detection.
"""

from typing import Dict, Any, List, Optional
import json
from config.settings import DEFAULT_SCORING_WEIGHTS
from database.repository import ProductRepository

class OpportunityScorer:
    """Scores product opportunity on a 0-100 scale using verifiable evidence."""

    @classmethod
    def score_product(
        cls,
        product: Dict[str, Any],
        competitors: List[Dict[str, Any]],
        quotes: List[Dict[str, Any]],
        profit_scenario: Optional[Dict[str, Any]],
        validation_checks: List[Dict[str, Any]],
        keyword_obs: List[Dict[str, Any]],
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Calculates opportunity score, confidence level, and detects blocking compliance risks.
        """
        w = weights if weights else DEFAULT_SCORING_WEIGHTS.copy()
        
        # Ensure weights normalize to 100
        weight_sum = sum(w.values())
        if weight_sum > 0:
            norm_w = {k: (v / weight_sum) * 100.0 for k, v in w.items()}
        else:
            norm_w = DEFAULT_SCORING_WEIGHTS.copy()

        breakdown = {}
        missing_data_warnings = []
        available_datapoints = 0
        total_datapoints = 6

        # ---------------------------------------------------------
        # Factor 1: Demand Evidence (Weight: 25%)
        # ---------------------------------------------------------
        demand_score = 0.0
        demand_explanation = []
        has_demand_evidence = False

        # Google Trends or Keyword Planner signals
        trends = [ko for ko in keyword_obs if ko.get("source_platform") == "Google Trends"]
        planner = [ko for ko in keyword_obs if ko.get("source_platform") == "Google Keyword Planner"]
        
        if planner:
            has_demand_evidence = True
            vol = planner[0].get("search_volume")
            if vol is not None and vol > 0:
                if vol >= 10000:
                    demand_score += 60.0
                    demand_explanation.append(f"High Google monthly searches ({vol:,.0f}/mo)")
                elif vol >= 2500:
                    demand_score += 45.0
                    demand_explanation.append(f"Healthy Google monthly searches ({vol:,.0f}/mo)")
                elif vol >= 500:
                    demand_score += 30.0
                    demand_explanation.append(f"Moderate Google searches ({vol:,.0f}/mo)")
                else:
                    demand_score += 15.0
                    demand_explanation.append(f"Low Google searches ({vol:,.0f}/mo)")

        if trends:
            has_demand_evidence = True
            avg_rel = trends[0].get("relative_interest_score", 50)
            if avg_rel >= 60:
                demand_score += 30.0
                demand_explanation.append(f"Strong Google Trends interest index ({avg_rel}/100)")
            else:
                demand_score += 15.0
                demand_explanation.append(f"Moderate Google Trends index ({avg_rel}/100)")

        # Competitor BSR signals
        bsr_competitors = [c.get("bsr") for c in competitors if c.get("bsr") is not None and c.get("bsr") > 0]
        if bsr_competitors:
            has_demand_evidence = True
            best_bsr = min(bsr_competitors)
            if best_bsr <= 1000:
                demand_score += 40.0
                demand_explanation.append(f"Top competitor has strong BSR #{best_bsr} in main category")
            elif best_bsr <= 5000:
                demand_score += 25.0
                demand_explanation.append(f"Top competitor BSR is #{best_bsr}")
            else:
                demand_score += 10.0
                demand_explanation.append(f"Top competitor BSR is #{best_bsr} (slow mover)")

        if has_demand_evidence:
            available_datapoints += 1
            demand_score = min(100.0, max(0.0, demand_score))
        else:
            demand_score = 0.0
            missing_data_warnings.append("No demand evidence (upload Google Trends/Keyword Planner CSV or record competitor BSRs).")
            demand_explanation.append("Missing demand verification data")

        breakdown["demand_evidence"] = {
            "score": round(demand_score, 1),
            "weight": round(norm_w["demand_evidence"], 1),
            "weighted_score": round((demand_score * norm_w["demand_evidence"]) / 100.0, 2),
            "explanation": " | ".join(demand_explanation),
        }

        # ---------------------------------------------------------
        # Factor 2: Competition Opportunity (Weight: 20%)
        # ---------------------------------------------------------
        comp_score = 0.0
        comp_explanation = []

        if competitors and len(competitors) >= 2:
            available_datapoints += 1
            reviews = [c.get("review_count") for c in competitors if c.get("review_count") is not None]
            ratings = [c.get("rating") for c in competitors if c.get("rating") is not None and c.get("rating") > 0]

            if reviews:
                reviews.sort()
                mid = len(reviews) // 2
                med_rev = (reviews[mid] if len(reviews) % 2 != 0 else (reviews[mid - 1] + reviews[mid]) / 2.0)
                if med_rev < 100:
                    comp_score += 55.0
                    comp_explanation.append(f"Very low review barrier (median {med_rev:.0f} reviews)")
                elif med_rev < 350:
                    comp_score += 40.0
                    comp_explanation.append(f"Manageable review barrier (median {med_rev:.0f} reviews)")
                elif med_rev < 800:
                    comp_score += 20.0
                    comp_explanation.append(f"Established review barrier (median {med_rev:.0f} reviews)")
                else:
                    comp_score += 5.0
                    comp_explanation.append(f"High review barrier (median {med_rev:.0f} reviews)")

            if ratings:
                avg_rat = sum(ratings) / len(ratings)
                if avg_rat < 4.0:
                    comp_score += 45.0
                    comp_explanation.append(f"Vulnerable competitor ratings (avg {avg_rat:.1f}⭐ - quality flaw opportunity)")
                elif avg_rat < 4.3:
                    comp_score += 30.0
                    comp_explanation.append(f"Decent competitor ratings (avg {avg_rat:.1f}⭐)")
                else:
                    comp_score += 15.0
                    comp_explanation.append(f"High competitor ratings (avg {avg_rat:.1f}⭐ - tough to out-delight)")
            comp_score = min(100.0, max(0.0, comp_score))
        else:
            comp_score = 0.0
            missing_data_warnings.append("Insufficient competitor listings (add at least 2-3 competing ASINs).")
            comp_explanation.append("Less than 2 competitors recorded")

        breakdown["competition_opportunity"] = {
            "score": round(comp_score, 1),
            "weight": round(norm_w["competition_opportunity"], 1),
            "weighted_score": round((comp_score * norm_w["competition_opportunity"]) / 100.0, 2),
            "explanation": " | ".join(comp_explanation),
        }

        # ---------------------------------------------------------
        # Factor 3: Profitability (Weight: 25%)
        # ---------------------------------------------------------
        profit_score = 0.0
        profit_explanation = []

        if profit_scenario and profit_scenario.get("net_profit_unit") is not None:
            available_datapoints += 1
            margin = profit_scenario.get("margin_pct", 0.0)
            roi = profit_scenario.get("roi_pct", 0.0)
            unit_profit = profit_scenario.get("net_profit_unit", 0.0)

            # Margin component (50 pts)
            if margin >= 35.0:
                profit_score += 50.0
                profit_explanation.append(f"Outstanding margin ({margin:.1f}%)")
            elif margin >= 28.0:
                profit_score += 40.0
                profit_explanation.append(f"Strong margin ({margin:.1f}%)")
            elif margin >= 20.0:
                profit_score += 25.0
                profit_explanation.append(f"Adequate margin ({margin:.1f}%)")
            elif margin > 0:
                profit_score += 10.0
                profit_explanation.append(f"Thin margin ({margin:.1f}%)")
            else:
                profit_score += 0.0
                profit_explanation.append(f"Unprofitable ({margin:.1f}%)")

            # ROI component (35 pts)
            if roi >= 150.0:
                profit_score += 35.0
                profit_explanation.append(f"Exceptional ROI ({roi:.0f}%)")
            elif roi >= 100.0:
                profit_score += 28.0
                profit_explanation.append(f"Strong ROI ({roi:.0f}%)")
            elif roi >= 60.0:
                profit_score += 15.0
                profit_explanation.append(f"Moderate ROI ({roi:.0f}%)")
            else:
                profit_score += 5.0
                profit_explanation.append(f"Low ROI ({roi:.0f}%)")

            # Absolute Rupee buffer (15 pts)
            if unit_profit >= 250.0:
                profit_score += 15.0
                profit_explanation.append(f"Healthy Rupee profit (₹{unit_profit:.0f}/unit)")
            elif unit_profit >= 120.0:
                profit_score += 10.0
                profit_explanation.append(f"Moderate Rupee profit (₹{unit_profit:.0f}/unit)")
            else:
                profit_score += 5.0
                profit_explanation.append(f"Low Rupee buffer (₹{unit_profit:.0f}/unit)")
            profit_score = min(100.0, max(0.0, profit_score))
        else:
            profit_score = 0.0
            missing_data_warnings.append("Profit scenario not computed (input selling price and sourcing quote).")
            profit_explanation.append("Missing profit calculation")

        breakdown["profitability"] = {
            "score": round(profit_score, 1),
            "weight": round(norm_w["profitability"], 1),
            "weighted_score": round((profit_score * norm_w["profitability"]) / 100.0, 2),
            "explanation": " | ".join(profit_explanation),
        }

        # ---------------------------------------------------------
        # Factor 4: Market Stability / Seasonality (Weight: 10%)
        # ---------------------------------------------------------
        stability_score = 60.0 # Default neutral
        stability_explanation = []

        season_check = next((c for c in validation_checks if c["check_key"] == "seasonality"), None)
        if season_check:
            available_datapoints += 1
            if season_check["status"] == "Pass":
                stability_score = 90.0
                stability_explanation.append("Confirmed year-round stable demand")
            elif season_check["status"] == "Needs Investigation":
                stability_score = 50.0
                stability_explanation.append("Seasonality needs investigation")
            else:
                stability_score = 20.0
                stability_explanation.append("Seasonal / festive spike dependency")
        else:
            missing_data_warnings.append("Seasonality check unverified.")
            stability_explanation.append("Unverified seasonality")

        breakdown["market_stability"] = {
            "score": round(stability_score, 1),
            "weight": round(norm_w["market_stability"], 1),
            "weighted_score": round((stability_score * norm_w["market_stability"]) / 100.0, 2),
            "explanation": " | ".join(stability_explanation),
        }

        # ---------------------------------------------------------
        # Factor 5: Differentiation Feasibility (Weight: 10%)
        # ---------------------------------------------------------
        diff_score = 50.0
        diff_explanation = []

        diff_check = next((c for c in validation_checks if c["check_key"] == "product_differentiation"), None)
        if diff_check:
            available_datapoints += 1
            if diff_check["status"] == "Pass":
                diff_score = 90.0
                diff_explanation.append("Clear differentiation angle documented")
            elif diff_check["status"] == "Needs Investigation":
                diff_score = 50.0
                diff_explanation.append("Differentiation angle unfinalized")
            else:
                diff_score = 25.0
                diff_explanation.append("Commoditized with low differentiation")
        else:
            missing_data_warnings.append("Differentiation check unverified.")
            diff_explanation.append("Check unverified")

        breakdown["differentiation"] = {
            "score": round(diff_score, 1),
            "weight": round(norm_w["differentiation"], 1),
            "weighted_score": round((diff_score * norm_w["differentiation"]) / 100.0, 2),
            "explanation": " | ".join(diff_explanation),
        }

        # ---------------------------------------------------------
        # Factor 6: Sourcing Feasibility & MOQ (Weight: 10%)
        # ---------------------------------------------------------
        sourcing_score = 0.0
        sourcing_explanation = []

        if quotes:
            available_datapoints += 1
            primary = quotes[0]
            moq = primary.get("moq", 500)
            lead_time = primary.get("production_lead_time_days", 30)
            country = primary.get("supplier_country", "India")

            # MOQ component (50 pts)
            if moq <= 100:
                sourcing_score += 50.0
                sourcing_explanation.append(f"Beginner-friendly MOQ ({moq} units)")
            elif moq <= 300:
                sourcing_score += 35.0
                sourcing_explanation.append(f"Moderate MOQ ({moq} units)")
            elif moq <= 1000:
                sourcing_score += 20.0
                sourcing_explanation.append(f"Substantial capital MOQ ({moq} units)")
            else:
                sourcing_score += 10.0
                sourcing_explanation.append(f"High barrier MOQ ({moq} units)")

            # Lead time & domestic cluster (50 pts)
            if country == "India":
                sourcing_score += 30.0
                sourcing_explanation.append("Domestic Indian sourcing (fast restock & no customs)")
            else:
                sourcing_score += 15.0
                sourcing_explanation.append("Overseas sourcing (international transit & customs duty)")

            if lead_time <= 15:
                sourcing_score += 20.0
                sourcing_explanation.append(f"Fast lead time ({lead_time} days)")
            elif lead_time <= 30:
                sourcing_score += 10.0
                sourcing_explanation.append(f"Standard lead time ({lead_time} days)")
            else:
                sourcing_score += 5.0
                sourcing_explanation.append(f"Extended lead time ({lead_time} days)")
            sourcing_score = min(100.0, max(0.0, sourcing_score))
        else:
            sourcing_score = 0.0
            missing_data_warnings.append("No supplier quotation recorded (add at least one supplier quote).")
            sourcing_explanation.append("No quotation received")

        breakdown["sourcing_feasibility"] = {
            "score": round(sourcing_score, 1),
            "weight": round(norm_w["sourcing_feasibility"], 1),
            "weighted_score": round((sourcing_score * norm_w["sourcing_feasibility"]) / 100.0, 2),
            "explanation": " | ".join(sourcing_explanation),
        }

        # ---------------------------------------------------------
        # Total Weighted Score
        # ---------------------------------------------------------
        total_score = sum(b["weighted_score"] for b in breakdown.values())
        total_score = round(min(100.0, max(0.0, total_score)), 1)

        # Confidence Level Calculation
        if available_datapoints >= 5:
            confidence_level = "High"
        elif available_datapoints >= 3:
            confidence_level = "Medium"
        else:
            confidence_level = "Low"

        # Separate Blocking Risks Analysis
        # Notice: Blocking compliance risks must NOT merely depress a numerical score; they must be surfaced as hard gates!
        blocking_risks = [c for c in validation_checks if c.get("is_blocking") and c.get("status") == "Fail"]
        blocking_reasons = [f"FAILED: {b['title']} - {b.get('notes', '')}" for b in blocking_risks]

        return {
            "total_score": total_score,
            "confidence_level": confidence_level,
            "available_datapoints": available_datapoints,
            "total_datapoints": total_datapoints,
            "missing_data_warnings": missing_data_warnings,
            "has_blocking_risks": len(blocking_risks) > 0,
            "blocking_reasons": blocking_reasons,
            "demand_score": breakdown["demand_evidence"]["score"],
            "competition_score": breakdown["competition_opportunity"]["score"],
            "profit_score": breakdown["profitability"]["score"],
            "stability_score": breakdown["market_stability"]["score"],
            "differentiation_score": breakdown["differentiation"]["score"],
            "sourcing_score": breakdown["sourcing_feasibility"]["score"],
            "breakdown": breakdown,
        }
