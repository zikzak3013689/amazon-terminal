"""
Keepa Connector & Manual Price History Adapter.
Supports manual Keepa web chart observations and provides a decoupled interface
for optional future Keepa API access (strictly disabled until valid key provided).
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime

class KeepaAdapter:
    """Manages Keepa price history observations and API readiness."""

    DOMAIN_AMAZON_IN = 10 # Keepa domain ID for amazon.in

    @classmethod
    def is_api_configured(cls) -> bool:
        """Checks if a valid Keepa API key is set in environment or config."""
        key = os.environ.get("KEEPA_API_KEY", "").strip()
        return len(key) >= 32

    @classmethod
    def get_api_status(cls) -> Dict[str, Any]:
        """Returns API enablement status and transparency details."""
        configured = cls.is_api_configured()
        return {
            "is_enabled": configured,
            "status": "Active (Key Configured)" if configured else "Disabled (Phase 1 Manual Mode)",
            "domain": "amazon.in (Domain ID: 10)",
            "message": (
                "Keepa API is active."
                if configured
                else "Phase 1: Free manual Keepa observation mode active. Direct web graph link is provided. Keepa API adapter remains disabled to maintain ₹0 subscription costs."
            ),
        }

    @staticmethod
    def format_manual_observation(
        product_id: int,
        asin: str,
        buy_box_current: Optional[float] = None,
        buy_box_avg_30: Optional[float] = None,
        buy_box_avg_90: Optional[float] = None,
        buy_box_avg_180: Optional[float] = None,
        bsr_current: Optional[int] = None,
        bsr_avg_90: Optional[int] = None,
        price_drops_count_90d: Optional[int] = None,
        is_amazon_selling: bool = False,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Structures a manual Keepa observation entry with explicit provenance.
        """
        obs_notes = []
        if buy_box_avg_90:
            obs_notes.append(f"90-Day Avg Buy Box: ₹{buy_box_avg_90:.2f}")
        if bsr_avg_90:
            obs_notes.append(f"90-Day Avg BSR: #{bsr_avg_90}")
        if is_amazon_selling:
            obs_notes.append("Amazon is an active in-stock seller on listing.")
        if price_drops_count_90d is not None:
            obs_notes.append(f"Price drops in 90d: {price_drops_count_90d}")
        if notes:
            obs_notes.append(notes)

        return {
            "product_id": product_id,
            "observed_price": buy_box_current,
            "bestseller_rank": bsr_current,
            "source_name": "Keepa Web Graph (Manual)",
            "source_url": f"https://keepa.com/#!product/10-{asin.upper()}",
            "observation_timestamp": datetime.now().isoformat(),
            "marketplace": "amazon.in",
            "collection_method": "Manual Inspection of Keepa Web Graph",
            "data_type": "observed",
            "notes": " | ".join(obs_notes),
            "keepa_metrics": {
                "buy_box_current": buy_box_current,
                "buy_box_avg_30": buy_box_avg_30,
                "buy_box_avg_90": buy_box_avg_90,
                "buy_box_avg_180": buy_box_avg_180,
                "bsr_current": bsr_current,
                "bsr_avg_90": bsr_avg_90,
                "price_drops_count_90d": price_drops_count_90d,
                "is_amazon_selling": is_amazon_selling,
            }
        }
