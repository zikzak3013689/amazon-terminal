"""
Google Keyword Planner CSV Connector.
Parses Google Ads Keyword Planner reports for India, extracts search volumes and bid ranges,
and marks data explicitly as Google Ads search data (never misrepresenting it as Amazon search volume).
"""

from typing import Dict, Any, List
import io
import pandas as pd
from datetime import datetime

class GoogleKeywordPlannerConnector:
    """Parses Google Ads Keyword Planner CSV files."""

    @classmethod
    def parse_csv(cls, file_content: str or bytes) -> Dict[str, Any]:
        """
        Parses Google Ads Keyword Planner export.
        Handles variations in column headers across different Google Ads versions.
        """
        if isinstance(file_content, bytes):
            text = file_content.decode("utf-8", errors="replace")
        else:
            text = file_content

        lines = text.strip().splitlines()
        header_idx = -1

        for i, line in enumerate(lines[:15]):
            low = line.lower()
            if "keyword" in low and ("avg. monthly searches" in low or "searches" in low or "competition" in low):
                header_idx = i
                break

        if header_idx == -1:
            header_idx = 0

        csv_data = "\n".join(lines[header_idx:])
        df = pd.read_csv(io.StringIO(csv_data))

        # Standardize columns
        col_map = {}
        for c in df.columns:
            low = c.strip().lower()
            if "keyword" in low:
                col_map[c] = "keyword"
            elif "avg. monthly searches" in low or "average monthly searches" in low or "volume" in low:
                col_map[c] = "search_volume"
            elif "competition" in low and "indexed" not in low:
                col_map[c] = "competition"
            elif "top of page bid (low range)" in low or "low range bid" in low or "bid low" in low:
                col_map[c] = "cpc_bid_low"
            elif "top of page bid (high range)" in low or "high range bid" in low or "bid high" in low:
                col_map[c] = "cpc_bid_high"

        df = df.rename(columns=col_map)
        if "keyword" not in df.columns:
            raise ValueError("Could not find 'Keyword' column in Keyword Planner CSV.")

        # Clean search volume
        if "search_volume" in df.columns:
            df["search_volume"] = (
                df["search_volume"]
                .astype(str)
                .str.replace(",", "")
                .str.extract(r"(\d+)", expand=False)
            )
            df["search_volume"] = pd.to_numeric(df["search_volume"], errors="coerce").fillna(0)
        else:
            df["search_volume"] = 0

        # Clean bids
        for bid_col in ["cpc_bid_low", "cpc_bid_high"]:
            if bid_col in df.columns:
                df[bid_col] = (
                    df[bid_col]
                    .astype(str)
                    .str.replace("₹", "")
                    .str.replace("$", "")
                    .str.replace(",", "")
                    .str.strip()
                )
                df[bid_col] = pd.to_numeric(df[bid_col], errors="coerce")
            else:
                df[bid_col] = None

        if "competition" not in df.columns:
            df["competition"] = "Medium"

        cleaned_records = []
        for _, row in df.iterrows():
            kw = str(row["keyword"]).strip()
            if kw and kw != "nan":
                cleaned_records.append({
                    "keyword": kw,
                    "search_volume": int(row["search_volume"]),
                    "competition": str(row.get("competition", "Medium")).strip(),
                    "cpc_bid_low": float(row["cpc_bid_low"]) if pd.notnull(row["cpc_bid_low"]) else None,
                    "cpc_bid_high": float(row["cpc_bid_high"]) if pd.notnull(row["cpc_bid_high"]) else None,
                    "geo_location": "India",
                    "source_platform": "Google Keyword Planner (Google Ads)",
                    "data_type": "estimated",
                    "observation_date": datetime.now().strftime("%Y-%m-%d"),
                })

        return {
            "total_keywords": len(cleaned_records),
            "records": cleaned_records,
            "disclaimer": "CRITICAL ATTRIBUTION: These search volumes reflect Google Search queries in India, NOT Amazon buyer search frequency. High Google volume reflects broad interest, but Amazon purchase intent must be confirmed via Amazon BSR & competitor reviews.",
        }
