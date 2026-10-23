"""
Excel Importer Engine for Student Research Spreadsheets and Generic Workbooks.
Parses both legacy and new student templates, preserves formulas and raw values,
detects duplicates, and isolates US legacy figures from Amazon India observations.
"""

from typing import Dict, Any, List, Optional
import os
import re
import json
from datetime import datetime

try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    openpyxl = None
    HAS_OPENPYXL = False

from database.repository import ProductRepository
from database.connection import get_db_connection
from connectors.amazon_manual import AmazonManualConnector

class ExcelImporter:
    """Specialized and generic importer for product research workbooks."""
    HAS_OPENPYXL = HAS_OPENPYXL

    @classmethod
    def import_workbook(cls, filepath: str, is_demo: int = 0) -> Dict[str, Any]:
        """
        Detects workbook type and routes to specialized parser or generic importer.
        """
        if not cls.HAS_OPENPYXL:
            raise ImportError("openpyxl is required for Excel workbook importing. Install with: pip install openpyxl")

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        wb = openpyxl.load_workbook(filepath, data_only=False)
        sheet_names = wb.sheetnames

        # Detect workbook type
        if "🔎 1. Product Spreadsheet" in sheet_names and "💰 2.  Product Margin" in sheet_names:
            return cls.import_old_student_template(filepath, is_demo=is_demo)
        elif "🔎 Product Research Template" in sheet_names:
            return cls.import_new_student_template(filepath, is_demo=is_demo)
        else:
            return cls.import_generic_excel(filepath, is_demo=is_demo)

    @classmethod
    def import_old_student_template(cls, filepath: str, is_demo: int = 0) -> Dict[str, Any]:
        """
        Parses 'OLD Product Research Spreadsheet (_File_ -_ _Make A Copy_).xlsx'.
        Extracts Product Spreadsheet, Product Margin, and Product Checklist.
        """
        wb_formulas = openpyxl.load_workbook(filepath, data_only=False)
        wb_values = openpyxl.load_workbook(filepath, data_only=True)

        imported_products = []
        skipped_count = 0
        raw_rows = []

        # 1. Parse Sheet: '🔎 1. Product Spreadsheet'
        ws_f = wb_formulas["🔎 1. Product Spreadsheet"]
        ws_v = wb_values["🔎 1. Product Spreadsheet"]

        # Row 2 contains headers
        headers = [str(ws_f.cell(2, c).value or "").strip() for c in range(1, ws_f.max_column + 1)]

        for r in range(3, ws_f.max_row + 1):
            title = ws_f.cell(r, 1).value
            if not title:
                continue
            title_str = str(title).strip()
            # Ignore placeholder template rows like 'product idea #3'
            if re.match(r"^product idea #\d+$", title_str, re.IGNORECASE):
                skipped_count += 1
                continue

            google_vol = ws_v.cell(r, 2).value
            amz_seller_url = ws_f.cell(r, 3).value
            median_reviews_f = ws_f.cell(r, 4).value
            median_reviews_v = ws_v.cell(r, 4).value
            amz_rev = ws_v.cell(r, 5).value
            amz_search_vol = ws_v.cell(r, 6).value
            etsy_url = ws_f.cell(r, 7).value
            etsy_rev = ws_v.cell(r, 8).value
            trademark_val = ws_v.cell(r, 9).value
            patent_val = ws_v.cell(r, 10).value
            margin_val = ws_v.cell(r, 11).value
            notes_val = ws_f.cell(r, 12).value

            asin = AmazonManualConnector.extract_asin(str(amz_seller_url or ""))

            # Duplicate Check: Check if product with title already exists
            existing = ProductRepository.list_products(search_query=title_str)
            duplicate_match = next((p for p in existing if p["title"].lower() == title_str.lower()), None)
            
            if duplicate_match:
                product_id = duplicate_match["id"]
                skipped_count += 1
            else:
                product_id = ProductRepository.create_product({
                    "title": title_str.title(),
                    "asin": asin,
                    "product_url": str(amz_seller_url or ""),
                    "marketplace": "amazon.com (US Legacy Reference)",
                    "category": "Home & Kitchen",
                    "main_keyword": title_str.lower(),
                    "review_count": int(median_reviews_v) if median_reviews_v and str(median_reviews_v).isdigit() else None,
                    "estimated_demand_notes": f"Imported from legacy template. Monthly Amz Vol: {amz_search_vol or 'N/A'}, Google Vol: {google_vol or 'N/A'}",
                    "research_status": "Researching",
                    "is_demo": is_demo
                })

            # Store formula & competitor info if formula exists
            if median_reviews_f and str(median_reviews_f).startswith("="):
                # Extract numbers from =MEDIAN(5771,143,3224,...)
                nums = re.findall(r"\d+", str(median_reviews_f))
                for idx, rev_num in enumerate(nums[:10]):
                    ProductRepository.add_competitor(product_id, {
                        "competitor_asin": f"B00LEGACY{idx+1:02d}",
                        "competitor_title": f"Legacy Competitor #{idx+1} ({title_str})",
                        "observed_price": 29.99, # Default reference price
                        "review_count": int(rev_num),
                        "evidence_source": f"Parsed from Excel formula: {median_reviews_f}",
                        "product_url": str(amz_seller_url or "")
                    })

            # Record keyword observations
            if google_vol:
                try:
                    ProductRepository.add_keyword_observation(product_id, {
                        "keyword": title_str,
                        "source_platform": "Google Search (US Legacy Template)",
                        "search_volume": float(google_vol),
                        "geo_location": "US",
                        "notes": "Historical reference volume from student spreadsheet."
                    })
                except Exception:
                    pass

            if amz_search_vol:
                try:
                    ProductRepository.add_keyword_observation(product_id, {
                        "keyword": title_str,
                        "source_platform": "Amazon Search (Legacy Template)",
                        "search_volume": float(amz_search_vol),
                        "geo_location": "US",
                        "notes": "Historical reference search volume."
                    })
                except Exception:
                    pass

            # Store trademark / patent validation check
            if trademark_val:
                status = "Pass" if str(trademark_val).upper() == "PASS" else "Fail"
                ProductRepository.save_validation_check(product_id, {
                    "check_key": "trademark_safety",
                    "title": "Trademark Clearance (India IP Portal)",
                    "status": status,
                    "evidence_source": "Legacy Template Entry",
                    "notes": f"Legacy record status: {trademark_val}"
                })

            if patent_val:
                status = "Pass" if str(patent_val).upper() == "PASS" else "Fail"
                ProductRepository.save_validation_check(product_id, {
                    "check_key": "patent_safety",
                    "title": "Patent & Design Protection Clearance",
                    "status": status,
                    "evidence_source": "Legacy Template Entry",
                    "notes": f"Legacy record status: {patent_val}"
                })

            # Add research note
            note_content = [f"Imported from workbook '{os.path.basename(filepath)}'."]
            if etsy_url:
                note_content.append(f"Etsy Link: {etsy_url}")
            if etsy_rev:
                note_content.append(f"Etsy Estimated Revenue: ${etsy_rev:,.0f}")
            if notes_val:
                note_content.append(f"Original Notes: {notes_val}")
            
            ProductRepository.add_note(product_id, "\n".join(note_content), title="Legacy Template Import Details")

            imported_products.append(title_str)
            raw_rows.append({
                "product_id": product_id,
                "title": title_str,
                "formula_review": str(median_reviews_f),
                "evaluated_review": median_reviews_v,
            })

        # Record import in history table
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO import_history (filename, import_type, total_records, imported_count, skipped_count, raw_payload_json) VALUES (?, ?, ?, ?, ?, ?)",
                (os.path.basename(filepath), "OLD_STUDENT_EXCEL", len(imported_products) + skipped_count, len(imported_products), skipped_count, json.dumps(raw_rows))
            )

        return {
            "status": "Success",
            "filename": os.path.basename(filepath),
            "import_type": "OLD_STUDENT_EXCEL",
            "imported_count": len(imported_products),
            "skipped_count": skipped_count,
            "imported_products": imported_products,
        }

    @classmethod
    def import_new_student_template(cls, filepath: str, is_demo: int = 0) -> Dict[str, Any]:
        """
        Parses '🔎 NEW Student Amazon Product Research Template (_File_ -_ _Make A Copy_).xlsx'.
        Extracts long-tail and short-tail keyword sets, average top 5 revenue formulas, etc.
        """
        wb_formulas = openpyxl.load_workbook(filepath, data_only=False)
        wb_values = openpyxl.load_workbook(filepath, data_only=True)

        ws_f = wb_formulas["🔎 Product Research Template"]
        ws_v = wb_values["🔎 Product Research Template"]

        imported_products = []
        skipped_count = 0
        raw_rows = []

        # Row 3 contains headers
        for r in range(4, ws_f.max_row + 1):
            long_tail = ws_f.cell(r, 1).value
            short_tail = ws_f.cell(r, 7).value
            
            # Use long_tail if present, otherwise short_tail
            product_name = long_tail or short_tail
            if not product_name:
                continue

            product_name_str = str(product_name).strip()
            amz_kw_vol = ws_v.cell(r, 2).value or ws_v.cell(r, 8).value
            google_kw_vol = ws_v.cell(r, 3).value or ws_v.cell(r, 9).value
            amz_rev_top1 = ws_v.cell(r, 4).value
            page1_count = ws_v.cell(r, 6).value
            avg_top5_rev_f = ws_f.cell(r, 10).value
            avg_top5_rev_v = ws_v.cell(r, 10).value
            etsy_rev = ws_v.cell(r, 5).value or ws_v.cell(r, 11).value

            # Check duplicate
            existing = ProductRepository.list_products(search_query=product_name_str)
            duplicate_match = next((p for p in existing if p["title"].lower() == product_name_str.lower()), None)

            if duplicate_match:
                product_id = duplicate_match["id"]
                skipped_count += 1
            else:
                product_id = ProductRepository.create_product({
                    "title": product_name_str.title(),
                    "marketplace": "amazon.com (US Legacy Reference)",
                    "category": "Baby Products" if "blanket" in product_name_str.lower() else "Home & Kitchen",
                    "main_keyword": product_name_str.lower(),
                    "estimated_demand_notes": f"Amz Keyword Vol: {amz_kw_vol or 'N/A'}, Google Vol: {google_kw_vol or 'N/A'}, Page 1 listings: {page1_count or 'N/A'}",
                    "research_status": "Researching",
                    "is_demo": is_demo
                })

            # Add short-tail keyword if distinct
            if short_tail and str(short_tail).strip().lower() != product_name_str.lower():
                ProductRepository.add_keyword(product_id, str(short_tail).strip().lower(), keyword_type="short-tail")

            # Store top 5 revenue formula data as competitors
            if avg_top5_rev_f and str(avg_top5_rev_f).startswith("="):
                # e.g. =(24000+21000+19000+16000+15000)/5
                rev_nums = re.findall(r"\d+", str(avg_top5_rev_f))
                for idx, rev_val in enumerate(rev_nums[:5]):
                    if int(rev_val) > 10: # filter out divisor 5
                        ProductRepository.add_competitor(product_id, {
                            "competitor_asin": f"B00STUDENT{idx+1:02d}",
                            "competitor_title": f"Top Competitor #{idx+1} ({product_name_str})",
                            "observed_price": 24.99,
                            "monthly_revenue_est": float(rev_val),
                            "evidence_source": f"Parsed from student revenue formula: {avg_top5_rev_f}"
                        })

            # Keyword observations
            if google_kw_vol:
                try:
                    ProductRepository.add_keyword_observation(product_id, {
                        "keyword": product_name_str,
                        "source_platform": "Google Keyword Planner (Legacy)",
                        "search_volume": float(google_kw_vol),
                        "geo_location": "US",
                        "notes": "Imported from Student Template"
                    })
                except Exception:
                    pass

            if amz_kw_vol:
                try:
                    ProductRepository.add_keyword_observation(product_id, {
                        "keyword": product_name_str,
                        "source_platform": "Amazon Keyword Volume (Legacy)",
                        "search_volume": float(amz_kw_vol),
                        "geo_location": "US",
                        "notes": "Imported from Student Template"
                    })
                except Exception:
                    pass

            # Research note
            note_lines = [f"Imported from '{os.path.basename(filepath)}'."]
            if amz_rev_top1:
                note_lines.append(f"#1 Amazon Monthly Revenue: ${amz_rev_top1:,.0f}")
            if etsy_rev:
                note_lines.append(f"Top Etsy Revenue: ${etsy_rev:,.0f}")
            if page1_count:
                note_lines.append(f"Amazon Page 1 Products: {page1_count}")
            ProductRepository.add_note(product_id, "\n".join(note_lines), title="Student Research Template Data")

            imported_products.append(product_name_str)
            raw_rows.append({"product_id": product_id, "title": product_name_str, "formula": str(avg_top5_rev_f)})

        # Record import in history table
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO import_history (filename, import_type, total_records, imported_count, skipped_count, raw_payload_json) VALUES (?, ?, ?, ?, ?, ?)",
                (os.path.basename(filepath), "NEW_STUDENT_EXCEL", len(imported_products) + skipped_count, len(imported_products), skipped_count, json.dumps(raw_rows))
            )

        return {
            "status": "Success",
            "filename": os.path.basename(filepath),
            "import_type": "NEW_STUDENT_EXCEL",
            "imported_count": len(imported_products),
            "skipped_count": skipped_count,
            "imported_products": imported_products,
        }

    @classmethod
    def import_generic_excel(cls, filepath: str, is_demo: int = 0) -> Dict[str, Any]:
        """
        Generic Excel importer that maps any standard column headers to products table.
        """
        wb = openpyxl.load_workbook(filepath, data_only=True)
        ws = wb.active
        headers = [str(ws.cell(1, c).value or "").strip().lower() for c in range(1, ws.max_column + 1)]

        imported = []
        skipped = 0

        # Find column indices
        title_col = next((i + 1 for i, h in enumerate(headers) if "title" in h or "product" in h or "name" in h), 1)
        asin_col = next((i + 1 for i, h in enumerate(headers) if "asin" in h), None)
        price_col = next((i + 1 for i, h in enumerate(headers) if "price" in h), None)
        category_col = next((i + 1 for i, h in enumerate(headers) if "category" in h), None)

        for r in range(2, ws.max_row + 1):
            title = ws.cell(r, title_col).value
            if not title:
                continue
            title_str = str(title).strip()
            asin = str(ws.cell(r, asin_col).value).strip() if asin_col else None
            price = ws.cell(r, price_col).value if price_col else None
            category = str(ws.cell(r, category_col).value).strip() if category_col else "Home & Kitchen"

            # Check duplicate
            existing = ProductRepository.list_products(search_query=title_str)
            if existing:
                skipped += 1
                continue

            product_id = ProductRepository.create_product({
                "title": title_str,
                "asin": asin,
                "marketplace": "amazon.in",
                "category": category,
                "main_keyword": title_str.lower(),
                "current_observed_price": float(price) if price else None,
                "research_status": "New Idea",
                "is_demo": is_demo
            })
            imported.append(title_str)

        return {
            "status": "Success",
            "filename": os.path.basename(filepath),
            "import_type": "GENERIC_EXCEL",
            "imported_count": len(imported),
            "skipped_count": skipped,
            "imported_products": imported,
        }
