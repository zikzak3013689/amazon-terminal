"""
Google Trends CSV Connector.
Parses Google Trends 'Interest over time' exports for India, detects seasonality,
and provides visualization data with clear disclaimer that Trends = relative search interest, not sales.
"""

from typing import Dict, Any, List, Optional
import io
import pandas as pd
import numpy as np

class GoogleTrendsConnector:
    """Parses and analyzes Google Trends CSV data."""

    @classmethod
    def parse_csv(cls, file_content: str or bytes) -> Dict[str, Any]:
        """
        Parses standard Google Trends CSV export format.
        Google Trends CSV headers usually start around row 2 or 3 with 'Category: ...' or 'Week/Day/Month'.
        """
        if isinstance(file_content, bytes):
            text = file_content.decode("utf-8", errors="replace")
        else:
            text = file_content

        lines = text.strip().splitlines()
        header_idx = -1
        timeframe = "Historical"
        category = "All categories"

        for i, line in enumerate(lines[:10]):
            clean = line.strip().lower()
            if clean.startswith("category:"):
                category = line.split(":", 1)[1].strip()
            elif "week" in clean or "month" in clean or "day" in clean or "date" in clean:
                header_idx = i
                break

        if header_idx == -1:
            # Fallback: assume row 0 is header
            header_idx = 0

        csv_data = "\n".join(lines[header_idx:])
        df = pd.read_csv(io.StringIO(csv_data))

        if df.empty or len(df.columns) < 2:
            raise ValueError("CSV does not contain valid Google Trends interest-over-time columns.")

        date_col = df.columns[0]
        # Clean column names (Google Trends appends ': (India)' or ': (Worldwide)')
        keywords = []
        rename_map = {date_col: "date"}

        for col in df.columns[1:]:
            clean_kw = col.split(":")[0].strip()
            keywords.append(clean_kw)
            rename_map[col] = clean_kw

        df = df.rename(columns=rename_map)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"]).sort_values("date")

        # Convert interest values to numeric (handle '<1' as 0.5)
        for kw in keywords:
            df[kw] = df[kw].astype(str).str.replace("<1", "0.5")
            df[kw] = pd.to_numeric(df[kw], errors="coerce").fillna(0.0)

        # Detect seasonality for the primary keyword
        primary_kw = keywords[0]
        seasonality = cls.calculate_seasonality(df, primary_kw)

        return {
            "keywords": keywords,
            "primary_keyword": primary_kw,
            "record_count": len(df),
            "start_date": str(df["date"].min().date()),
            "end_date": str(df["date"].max().date()),
            "timeframe": f"{df['date'].min().date()} to {df['date'].max().date()}",
            "category": category,
            "geo": "India",
            "is_comparison": len(keywords) > 1,
            "seasonality": seasonality,
            "dataframe": df,
            "summary": {
                kw: {
                    "mean_interest": round(df[kw].mean(), 1),
                    "max_interest": round(df[kw].max(), 1),
                    "min_interest": round(df[kw].min(), 1),
                    "current_interest": round(df[kw].iloc[-1], 1) if not df.empty else 0.0,
                }
                for kw in keywords
            },
            "disclaimer": "CRITICAL: Google Trends measures relative search volume interest (0-100 index) on Google Search in India. It is NOT absolute sales count or Amazon search volume.",
        }

    @staticmethod
    def calculate_seasonality(df: pd.DataFrame, keyword: str) -> Dict[str, Any]:
        """Calculates month-by-month seasonality index and variance."""
        if df.empty or keyword not in df.columns:
            return {"is_seasonal": False, "verdict": "Insufficient data"}

        temp = df.copy()
        temp["month"] = temp["date"].dt.month_name()
        temp["month_num"] = temp["date"].dt.month

        monthly_avg = temp.groupby(["month_num", "month"])[keyword].mean().reset_index()
        monthly_avg = monthly_avg.sort_values("month_num")

        values = monthly_avg[keyword].values
        if len(values) == 0:
            return {"is_seasonal": False, "verdict": "Insufficient data"}

        mean_val = np.mean(values)
        std_val = np.std(values)
        cov = (std_val / mean_val) if mean_val > 0 else 0.0 # Coefficient of variation

        peak_idx = np.argmax(values)
        trough_idx = np.argmin(values)
        peak_month = monthly_avg.iloc[peak_idx]["month"]
        peak_val = round(values[peak_idx], 1)
        trough_month = monthly_avg.iloc[trough_idx]["month"]

        # If CoV > 0.35 or Peak > 2.5x Trough => High Seasonality
        is_seasonal = cov > 0.35 or (values[trough_idx] > 0 and (peak_val / values[trough_idx]) > 2.5)
        
        if is_seasonal:
            verdict = f"High Seasonality detected. Demand peaks in {peak_month} ({peak_val}/100) and slows in {trough_month}."
        else:
            verdict = f"Stable year-round demand. Search interest fluctuates moderately across months (CoV: {cov:.2f})."

        return {
            "is_seasonal": is_seasonal,
            "coefficient_of_variation": round(cov, 2),
            "peak_month": peak_month,
            "peak_value": peak_val,
            "trough_month": trough_month,
            "trough_value": round(values[trough_idx], 1),
            "monthly_distribution": monthly_avg[["month", keyword]].to_dict(orient="records"),
            "verdict": verdict,
        }
