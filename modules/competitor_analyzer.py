"""
Competitor Analyzer Module for Amazon India Research Terminal.
Computes statistical benchmarks (median price, price dispersion, review concentration,
top-seller dominance) and guides differentiation analysis.
"""

from typing import List, Dict, Any, Optional
import statistics

class CompetitorAnalyzer:
    """Analyzes competing ASINs for a product idea without fabricating sales estimates."""

    @staticmethod
    def analyze_competitors(competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates price, rating, and review concentration benchmarks across competing listings.
        """
        if not competitors:
            return {
                "count": 0,
                "has_sufficient_data": False,
                "median_price": None,
                "min_price": None,
                "max_price": None,
                "price_range": None,
                "price_std_dev": None,
                "price_dispersion_pct": None,
                "median_reviews": None,
                "min_reviews": None,
                "max_reviews": None,
                "total_reviews": 0,
                "top3_review_concentration_pct": None,
                "average_rating": None,
                "median_rating": None,
                "concentration_verdict": "No Competitor Data",
                "insights": ["No competing ASINs added yet. Add at least 3-5 competing listings."],
            }

        prices = [float(c["observed_price"]) for c in competitors if c.get("observed_price") is not None and float(c["observed_price"]) > 0]
        reviews = [int(c["review_count"]) for c in competitors if c.get("review_count") is not None]
        ratings = [float(c["rating"]) for c in competitors if c.get("rating") is not None and float(c["rating"]) > 0]

        # Price Stats
        median_price = round(statistics.median(prices), 2) if prices else None
        min_price = min(prices) if prices else None
        max_price = max(prices) if prices else None
        price_range = round(max_price - min_price, 2) if (min_price is not None and max_price is not None) else None
        
        price_std_dev = round(statistics.stdev(prices), 2) if len(prices) >= 2 else 0.0
        price_dispersion_pct = round((price_std_dev / median_price * 100), 1) if (median_price and median_price > 0 and len(prices) >= 2) else 0.0

        # Review Stats (Important: Review counts do NOT directly equal sales volume!)
        median_reviews = round(statistics.median(reviews), 0) if reviews else None
        min_reviews = min(reviews) if reviews else None
        max_reviews = max(reviews) if reviews else None
        total_reviews = sum(reviews)

        # Top 3 review concentration (% of total reviews captured by top 3 most-reviewed sellers)
        if total_reviews > 0 and len(reviews) >= 3:
            sorted_rev = sorted(reviews, reverse=True)
            top3_sum = sum(sorted_rev[:3])
            top3_concentration = round((top3_sum / total_reviews) * 100, 1)
        elif total_reviews > 0:
            top3_concentration = 100.0
        else:
            top3_concentration = None

        # Rating Stats
        avg_rating = round(statistics.mean(ratings), 2) if ratings else None
        median_rating = round(statistics.median(ratings), 2) if ratings else None

        # Concentration Verdict
        insights = []
        if top3_concentration is not None:
            if top3_concentration > 75.0:
                concentration_verdict = "High Concentration (Dominant Incumbents)"
                insights.append(f"Top 3 sellers control {top3_concentration}% of all social proof (reviews). Breaking through requires strong differentiation or niche focus.")
            elif top3_concentration > 50.0:
                concentration_verdict = "Moderate Concentration (Fragmented Leaders)"
                insights.append(f"Top 3 sellers hold {top3_concentration}% of reviews. Healthy opportunity for a compelling private label offering.")
            else:
                concentration_verdict = "Low Concentration (Open / Fragmented)"
                insights.append(f"Reviews are distributed across many sellers ({top3_concentration}% in top 3). Low moats against new entrants.")
        else:
            concentration_verdict = "Insufficient Review Data"

        if median_reviews is not None:
            if median_reviews < 150:
                insights.append(f"Low review barrier (median {median_reviews:.0f} reviews). Fast social proof ramp achievable.")
            elif median_reviews > 800:
                insights.append(f"High review barrier (median {median_reviews:.0f} reviews). Incumbents have long-standing customer trust.")

        if price_dispersion_pct is not None and price_dispersion_pct > 25.0:
            insights.append(f"High price variance ({price_dispersion_pct}% dispersion). Market accommodates budget, mid-tier, and premium tiers.")
        elif price_dispersion_pct is not None:
            insights.append(f"Tight price clustering ({price_dispersion_pct}% dispersion around ₹{median_price}). Clear customer price expectation.")

        return {
            "count": len(competitors),
            "has_sufficient_data": len(competitors) >= 3,
            "median_price": median_price,
            "min_price": min_price,
            "max_price": max_price,
            "price_range": price_range,
            "price_std_dev": price_std_dev,
            "price_dispersion_pct": price_dispersion_pct,
            "median_reviews": median_reviews,
            "min_reviews": min_reviews,
            "max_reviews": max_reviews,
            "total_reviews": total_reviews,
            "top3_review_concentration_pct": top3_concentration,
            "average_rating": avg_rating,
            "median_rating": median_rating,
            "concentration_verdict": concentration_verdict,
            "insights": insights,
        }

    @staticmethod
    def get_differentiation_checklist() -> List[Dict[str, str]]:
        """Checklist for uncovering competitive differentiation angles on Amazon India."""
        return [
            {
                "area": "1-Star & 2-Star Review Mining",
                "focus": "Product Quality & Durability",
                "action": "Read negative reviews of top sellers. What breaks? What leaks? What smells bad? Engineer a fix."
            },
            {
                "area": "Packaging & Unboxing Experience",
                "focus": "Transit Protection & Giftability",
                "action": "Indian courier transit is rough. Use reinforced 5-ply mailer boxes, bubble wrap, or gift-ready magnetic boxes."
            },
            {
                "area": "Bundle / Accessory Addition",
                "focus": "Perceived Value Proposition",
                "action": "Add a complementary ₹20-₹40 accessory (e.g. cleaning brush, extra gaskets, carrying pouch) to justify a ₹150 higher selling price."
            },
            {
                "area": "Clear Instructions in Hindi & English",
                "focus": "Customer Support & Returns Reduction",
                "action": "Include a printed bilingual user guide with a QR code linking to a 60-second video demo to slash avoidable returns."
            },
            {
                "area": "Size / Capacity Optimization for Indian Homes",
                "focus": "Local Context Fit",
                "action": "Tune dimensions for compact Indian kitchens/wardrobes or local power/water conditions."
            },
        ]
