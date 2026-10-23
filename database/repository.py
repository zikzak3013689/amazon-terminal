"""
Database Repository: CRUD and query operations for the Amazon India Research Terminal.
"""

from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from database.connection import get_db_connection

class ProductRepository:
    """Manages products, keywords, competitors, quotes, observations, checks, and scores."""

    # -------------------------------------------------------------
    # Products
    # -------------------------------------------------------------
    @staticmethod
    def create_product(data: Dict[str, Any]) -> int:
        query = """
        INSERT INTO products (
            title, asin, product_url, marketplace, category, subcategory,
            main_keyword, brand, current_observed_price, review_count,
            average_rating, bestseller_rank, weight_kg, length_cm, width_cm,
            height_cm, estimated_demand_notes, competition_notes,
            research_status, is_demo
        ) VALUES (
            :title, :asin, :product_url, :marketplace, :category, :subcategory,
            :main_keyword, :brand, :current_observed_price, :review_count,
            :average_rating, :bestseller_rank, :weight_kg, :length_cm, :width_cm,
            :height_cm, :estimated_demand_notes, :competition_notes,
            :research_status, :is_demo
        )
        """
        defaults = {
            "asin": None, "product_url": None, "marketplace": "amazon.in",
            "category": "Home & Kitchen", "subcategory": None, "brand": None,
            "current_observed_price": None, "review_count": None,
            "average_rating": None, "bestseller_rank": None, "weight_kg": 0.5,
            "length_cm": 15.0, "width_cm": 10.0, "height_cm": 5.0,
            "estimated_demand_notes": None, "competition_notes": None,
            "research_status": "New Idea", "is_demo": 0
        }
        params = {**defaults, **data}
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            product_id = cur.lastrowid
            
            # If main_keyword provided, add it to product_keywords as primary
            if params.get("main_keyword"):
                cur.execute(
                    "INSERT INTO product_keywords (product_id, keyword, keyword_type, is_primary) VALUES (?, ?, 'main', 1)",
                    (product_id, params["main_keyword"])
                )
            return product_id

    @staticmethod
    def get_product(product_id: int) -> Optional[Dict[str, Any]]:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM products WHERE id = ?", (product_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_product_by_asin(asin: str, marketplace: str = "amazon.in") -> Optional[Dict[str, Any]]:
        if not asin:
            return None
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM products WHERE UPPER(asin) = UPPER(?) AND marketplace = ?", (asin.strip(), marketplace))
            row = cur.fetchone()
            return dict(row) if row else None

    @staticmethod
    def list_products(
        category: Optional[str] = None,
        status: Optional[str] = None,
        search_query: Optional[str] = None,
        is_demo: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        conditions = []
        params = []
        if category and category != "All Categories":
            conditions.append("p.category = ?")
            params.append(category)
        if status and status != "All Statuses":
            conditions.append("p.research_status = ?")
            params.append(status)
        if is_demo is not None:
            conditions.append("p.is_demo = ?")
            params.append(is_demo)
        if search_query:
            conditions.append("(p.title LIKE ? OR p.main_keyword LIKE ? OR p.asin LIKE ? OR p.brand LIKE ?)")
            wildcard = f"%{search_query.strip()}%"
            params.extend([wildcard, wildcard, wildcard, wildcard])

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"""
        SELECT p.*,
               (SELECT COUNT(*) FROM competitors c WHERE c.product_id = p.id) as competitor_count,
               (SELECT total_score FROM opportunity_scores o WHERE o.product_id = p.id ORDER BY scored_at DESC LIMIT 1) as opportunity_score,
               (SELECT confidence_level FROM opportunity_scores o WHERE o.product_id = p.id ORDER BY scored_at DESC LIMIT 1) as confidence_level,
               (SELECT has_blocking_risks FROM opportunity_scores o WHERE o.product_id = p.id ORDER BY scored_at DESC LIMIT 1) as has_blocking_risks,
               (SELECT net_profit_unit FROM profit_scenarios ps WHERE ps.product_id = p.id AND ps.scenario_name = 'Base' LIMIT 1) as base_profit_unit,
               (SELECT margin_pct FROM profit_scenarios ps WHERE ps.product_id = p.id AND ps.scenario_name = 'Base' LIMIT 1) as base_margin_pct
        FROM products p
        {where_clause}
        ORDER BY p.updated_at DESC
        """
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def update_product(product_id: int, updates: Dict[str, Any]) -> bool:
        if not updates:
            return False
        fields = [f"{k} = :{k}" for k in updates.keys()]
        fields.append("updated_at = CURRENT_TIMESTAMP")
        query = f"UPDATE products SET {', '.join(fields)} WHERE id = :product_id"
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, {**updates, "product_id": product_id})
            return cur.rowcount > 0

    @staticmethod
    def delete_product(product_id: int) -> bool:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM products WHERE id = ?", (product_id,))
            return cur.rowcount > 0

    @staticmethod
    def clear_all_products() -> int:
        """Deletes all products and cascades deletion to child tables."""
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM products")
            return cur.rowcount

    @staticmethod
    def delete_legacy_products() -> int:
        """Deletes products imported from legacy student templates (marketplace containing 'US Legacy')."""
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM products WHERE marketplace LIKE '%Legacy%' OR marketplace LIKE '%US%'")
            return cur.rowcount

    # -------------------------------------------------------------
    # Keywords
    # -------------------------------------------------------------
    @staticmethod
    def add_keyword(product_id: int, keyword: str, keyword_type: str = "long-tail", is_primary: int = 0) -> int:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO product_keywords (product_id, keyword, keyword_type, is_primary) VALUES (?, ?, ?, ?)",
                (product_id, keyword.strip(), keyword_type, is_primary)
            )
            return cur.lastrowid

    @staticmethod
    def get_keywords(product_id: int) -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM product_keywords WHERE product_id = ? ORDER BY is_primary DESC, id ASC", (product_id,))
            return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def delete_keyword(keyword_id: int) -> bool:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM product_keywords WHERE id = ?", (keyword_id,))
            return cur.rowcount > 0

    # -------------------------------------------------------------
    # Competitors
    # -------------------------------------------------------------
    @staticmethod
    def add_competitor(product_id: int, data: Dict[str, Any]) -> int:
        query = """
        INSERT INTO competitors (
            product_id, competitor_asin, competitor_title, brand, product_url,
            observed_price, rating, review_count, bsr, monthly_sales_est,
            monthly_revenue_est, seller_name, fulfilment_type, strengths,
            weaknesses, differentiation_angle, observation_date, evidence_source, source_url
        ) VALUES (
            :product_id, :competitor_asin, :competitor_title, :brand, :product_url,
            :observed_price, :rating, :review_count, :bsr, :monthly_sales_est,
            :monthly_revenue_est, :seller_name, :fulfilment_type, :strengths,
            :weaknesses, :differentiation_angle, :observation_date, :evidence_source, :source_url
        )
        """
        defaults = {
            "brand": None, "product_url": None, "rating": None, "review_count": None,
            "bsr": None, "monthly_sales_est": None, "monthly_revenue_est": None,
            "seller_name": None, "fulfilment_type": "FBA", "strengths": None,
            "weaknesses": None, "differentiation_angle": None,
            "observation_date": datetime.now().strftime("%Y-%m-%d"),
            "evidence_source": "Amazon.in Listing", "source_url": None
        }
        params = {**defaults, **data, "product_id": product_id}
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return cur.lastrowid

    @staticmethod
    def get_competitors(product_id: int) -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM competitors WHERE product_id = ? ORDER BY observed_price ASC", (product_id,))
            return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def delete_competitor(competitor_id: int) -> bool:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM competitors WHERE id = ?", (competitor_id,))
            return cur.rowcount > 0

    # -------------------------------------------------------------
    # Observations (Product and Keywords)
    # -------------------------------------------------------------
    @staticmethod
    def add_product_observation(product_id: int, data: Dict[str, Any]) -> int:
        query = """
        INSERT INTO product_observations (
            product_id, observed_price, bestseller_rank, review_count, rating,
            source_name, source_url, observation_timestamp, marketplace,
            collection_method, data_type, notes
        ) VALUES (
            :product_id, :observed_price, :bestseller_rank, :review_count, :rating,
            :source_name, :source_url, CURRENT_TIMESTAMP, :marketplace,
            :collection_method, :data_type, :notes
        )
        """
        defaults = {
            "observed_price": None, "bestseller_rank": None, "review_count": None,
            "rating": None, "source_url": None, "marketplace": "amazon.in",
            "collection_method": "Manual Observation", "data_type": "observed", "notes": None
        }
        params = {**defaults, **data, "product_id": product_id}
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return cur.lastrowid

    @staticmethod
    def get_product_observations(product_id: int) -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM product_observations WHERE product_id = ? ORDER BY observation_timestamp DESC", (product_id,))
            return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def add_keyword_observation(product_id: int, data: Dict[str, Any]) -> int:
        query = """
        INSERT INTO keyword_observations (
            product_id, keyword, source_platform, search_volume,
            relative_interest_score, competition_index, cpc_bid_low, cpc_bid_high,
            geo_location, timeframe, observation_date, collection_method, data_type, notes
        ) VALUES (
            :product_id, :keyword, :source_platform, :search_volume,
            :relative_interest_score, :competition_index, :cpc_bid_low, :cpc_bid_high,
            :geo_location, :timeframe, :observation_date, :collection_method, :data_type, :notes
        )
        """
        defaults = {
            "search_volume": None, "relative_interest_score": None, "competition_index": "Medium",
            "cpc_bid_low": None, "cpc_bid_high": None, "geo_location": "IN", "timeframe": "Last 12 Months",
            "observation_date": datetime.now().strftime("%Y-%m-%d"),
            "collection_method": "CSV Import", "data_type": "estimated", "notes": None
        }
        params = {**defaults, **data, "product_id": product_id}
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return cur.lastrowid

    @staticmethod
    def get_keyword_observations(product_id: int) -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM keyword_observations WHERE product_id = ? ORDER BY id DESC", (product_id,))
            return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def delete_keyword_observation(observation_id: int) -> bool:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM keyword_observations WHERE id = ?", (observation_id,))
            return cur.rowcount > 0

    # -------------------------------------------------------------
    # Supplier Quotes & Sourcing
    # -------------------------------------------------------------
    @staticmethod
    def add_supplier_quote(product_id: int, data: Dict[str, Any]) -> int:
        query = """
        INSERT INTO supplier_quotes (
            product_id, supplier_name, supplier_country, supplier_contact,
            supplier_city_hub, product_reference, unit_purchase_cost,
            currency, exchange_rate_to_inr, moq, packaging_cost, sample_cost,
            production_lead_time_days, defect_allowance_pct, tax_rate_pct,
            is_tax_recoverable_itc, freight_cost_per_unit, quotation_date,
            valid_until_date, notes, is_primary_supplier
        ) VALUES (
            :product_id, :supplier_name, :supplier_country, :supplier_contact,
            :supplier_city_hub, :product_reference, :unit_purchase_cost,
            :currency, :exchange_rate_to_inr, :moq, :packaging_cost, :sample_cost,
            :production_lead_time_days, :defect_allowance_pct, :tax_rate_pct,
            :is_tax_recoverable_itc, :freight_cost_per_unit, :quotation_date,
            :valid_until_date, :notes, :is_primary_supplier
        )
        """
        defaults = {
            "supplier_country": "India", "supplier_contact": None, "supplier_city_hub": None,
            "product_reference": None, "currency": "INR", "exchange_rate_to_inr": 1.0,
            "moq": 100, "packaging_cost": 0.0, "sample_cost": 0.0,
            "production_lead_time_days": 15, "defect_allowance_pct": 2.0, "tax_rate_pct": 18.0,
            "is_tax_recoverable_itc": 1, "freight_cost_per_unit": 0.0,
            "quotation_date": datetime.now().strftime("%Y-%m-%d"),
            "valid_until_date": None, "notes": None, "is_primary_supplier": 0
        }
        params = {**defaults, **data, "product_id": product_id}
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return cur.lastrowid

    @staticmethod
    def get_supplier_quotes(product_id: int) -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM supplier_quotes WHERE product_id = ? ORDER BY is_primary_supplier DESC, unit_purchase_cost ASC", (product_id,))
            return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def delete_supplier_quote(quote_id: int) -> bool:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM supplier_quotes WHERE id = ?", (quote_id,))
            return cur.rowcount > 0

    # -------------------------------------------------------------
    # Profit Scenarios
    # -------------------------------------------------------------
    @staticmethod
    def save_profit_scenario(product_id: int, data: Dict[str, Any]) -> int:
        query = """
        INSERT OR REPLACE INTO profit_scenarios (
            product_id, scenario_name, selling_price_gross, gst_rate, is_gst_registered,
            fulfilment_model, referral_fee, closing_fee, weight_handling_fee,
            pick_pack_fee, storage_fee, amazon_fee_gst, landed_cost_unit,
            advertising_spend_unit, advertising_spend_pct, returns_allowance_pct,
            returns_cost_unit, net_revenue_excl_tax, net_profit_unit, margin_pct,
            roi_pct, breakeven_selling_price, breakeven_acos_pct, monthly_units_est,
            monthly_net_profit, assumptions_json, updated_at
        ) VALUES (
            :product_id, :scenario_name, :selling_price_gross, :gst_rate, :is_gst_registered,
            :fulfilment_model, :referral_fee, :closing_fee, :weight_handling_fee,
            :pick_pack_fee, :storage_fee, :amazon_fee_gst, :landed_cost_unit,
            :advertising_spend_unit, :advertising_spend_pct, :returns_allowance_pct,
            :returns_cost_unit, :net_revenue_excl_tax, :net_profit_unit, :margin_pct,
            :roi_pct, :breakeven_selling_price, :breakeven_acos_pct, :monthly_units_est,
            :monthly_net_profit, :assumptions_json, CURRENT_TIMESTAMP
        )
        """
        params = {**data, "product_id": product_id}
        with get_db_connection() as conn:
            cur = conn.cursor()
            # If scenario already exists for product_id + scenario_name, delete it first
            cur.execute("DELETE FROM profit_scenarios WHERE product_id = ? AND scenario_name = ?", (product_id, params["scenario_name"]))
            cur.execute(query, params)
            return cur.lastrowid

    @staticmethod
    def get_profit_scenarios(product_id: int) -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM profit_scenarios WHERE product_id = ? ORDER BY id ASC", (product_id,))
            return [dict(r) for r in cur.fetchall()]

    # -------------------------------------------------------------
    # Validation Checks
    # -------------------------------------------------------------
    @staticmethod
    def save_validation_check(product_id: int, check: Dict[str, Any]) -> int:
        query = """
        INSERT INTO validation_checks (
            product_id, check_key, check_category, title, status, notes, evidence_source, is_blocking, evaluated_at
        ) VALUES (
            :product_id, :check_key, :check_category, :title, :status, :notes, :evidence_source, :is_blocking, CURRENT_TIMESTAMP
        )
        ON CONFLICT(product_id, check_key) DO UPDATE SET
            status = excluded.status,
            notes = excluded.notes,
            evidence_source = excluded.evidence_source,
            evaluated_at = CURRENT_TIMESTAMP
        """
        params = {
            "product_id": product_id,
            "check_key": check["check_key"],
            "check_category": check.get("check_category", "General"),
            "title": check["title"],
            "status": check.get("status", "Needs Investigation"),
            "notes": check.get("notes", ""),
            "evidence_source": check.get("evidence_source", "Manual Check"),
            "is_blocking": check.get("is_blocking", 0),
        }
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return cur.lastrowid

    @staticmethod
    def get_validation_checks(product_id: int) -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM validation_checks WHERE product_id = ? ORDER BY id ASC", (product_id,))
            return [dict(r) for r in cur.fetchall()]

    # -------------------------------------------------------------
    # Opportunity Scores
    # -------------------------------------------------------------
    @staticmethod
    def save_opportunity_score(product_id: int, score_data: Dict[str, Any]) -> int:
        query = """
        INSERT INTO opportunity_scores (
            product_id, total_score, demand_score, competition_score,
            profit_score, stability_score, differentiation_score, sourcing_score,
            confidence_level, missing_data_warnings, has_blocking_risks,
            blocking_reasons, score_breakdown_json, scored_at
        ) VALUES (
            :product_id, :total_score, :demand_score, :competition_score,
            :profit_score, :stability_score, :differentiation_score, :sourcing_score,
            :confidence_level, :missing_data_warnings, :has_blocking_risks,
            :blocking_reasons, :score_breakdown_json, CURRENT_TIMESTAMP
        )
        """
        warnings = score_data.get("missing_data_warnings", "")
        if isinstance(warnings, list):
            warnings = " | ".join(warnings)

        reasons = score_data.get("blocking_reasons", "")
        if isinstance(reasons, list):
            reasons = " | ".join(reasons)

        breakdown = score_data.get("score_breakdown_json")
        if not breakdown and "breakdown" in score_data:
            breakdown = json.dumps(score_data["breakdown"])
        elif isinstance(breakdown, (dict, list)):
            breakdown = json.dumps(breakdown)

        params = {
            "product_id": product_id,
            "total_score": score_data.get("total_score", 0.0),
            "demand_score": score_data.get("demand_score", 0.0),
            "competition_score": score_data.get("competition_score", 0.0),
            "profit_score": score_data.get("profit_score", 0.0),
            "stability_score": score_data.get("stability_score", 0.0),
            "differentiation_score": score_data.get("differentiation_score", 0.0),
            "sourcing_score": score_data.get("sourcing_score", 0.0),
            "confidence_level": score_data.get("confidence_level", "Medium"),
            "missing_data_warnings": str(warnings or ""),
            "has_blocking_risks": 1 if score_data.get("has_blocking_risks") else 0,
            "blocking_reasons": str(reasons or ""),
            "score_breakdown_json": str(breakdown or "{}"),
        }
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return cur.lastrowid

    @staticmethod
    def get_opportunity_score(product_id: int) -> Optional[Dict[str, Any]]:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM opportunity_scores WHERE product_id = ? ORDER BY scored_at DESC LIMIT 1", (product_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    # -------------------------------------------------------------
    # Research Notes
    # -------------------------------------------------------------
    @staticmethod
    def add_note(product_id: int, content: str, title: Optional[str] = None, source_reference: Optional[str] = None) -> int:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO research_notes (product_id, author, title, content, source_reference) VALUES (?, 'Researcher', ?, ?, ?)",
                (product_id, title, content, source_reference)
            )
            return cur.lastrowid

    @staticmethod
    def get_notes(product_id: int) -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM research_notes WHERE product_id = ? ORDER BY created_at DESC", (product_id,))
            return [dict(r) for r in cur.fetchall()]

    # -------------------------------------------------------------
    # Terminal Overview Metrics & Health
    # -------------------------------------------------------------
    @staticmethod
    def get_terminal_metrics(is_demo: Optional[int] = None) -> Dict[str, Any]:
        with get_db_connection() as conn:
            cur = conn.cursor()
            demo_filter = ""
            params = []
            if is_demo is not None:
                demo_filter = "WHERE is_demo = ?"
                params.append(is_demo)

            cur.execute(f"SELECT COUNT(*) FROM products {demo_filter}", params)
            total_products = cur.fetchone()[0]

            cur.execute(f"SELECT research_status, COUNT(*) FROM products {demo_filter} GROUP BY research_status", params)
            status_counts = dict(cur.fetchall())

            cur.execute(f"SELECT COUNT(*) FROM competitors c JOIN products p ON c.product_id = p.id {('WHERE p.is_demo = ?' if is_demo is not None else '')}", params)
            total_competitors = cur.fetchone()[0]

            cur.execute(f"SELECT COUNT(*) FROM supplier_quotes sq JOIN products p ON sq.product_id = p.id {('WHERE p.is_demo = ?' if is_demo is not None else '')}", params)
            total_quotes = cur.fetchone()[0]

            cur.execute(f"SELECT COUNT(*) FROM validation_checks vc JOIN products p ON vc.product_id = p.id WHERE vc.status = 'Fail' {('AND p.is_demo = ?' if is_demo is not None else '')}", params)
            total_failed_checks = cur.fetchone()[0]

            return {
                "total_products": total_products,
                "status_counts": status_counts,
                "total_competitors": total_competitors,
                "total_quotes": total_quotes,
                "total_failed_checks": total_failed_checks,
                "shortlisted_count": status_counts.get("Shortlisted", 0),
                "researching_count": status_counts.get("Researching", 0),
                "awaiting_data_count": status_counts.get("Awaiting Data", 0),
                "approved_count": status_counts.get("Approved for Small Test", 0),
                "rejected_count": status_counts.get("Rejected", 0),
            }

    # -------------------------------------------------------------
    # Hunted Niches (User Research)
    # -------------------------------------------------------------
    @staticmethod
    def add_hunted_niche(data: Dict[str, Any]) -> int:
        query = """
        INSERT INTO hunted_niches (
            niche_name, category, target_cluster, problem_solved,
            target_mrp_low, target_mrp_high, estimated_factory_cost,
            search_volume_est, competition_level, differentiation_hook, notes, status
        ) VALUES (
            :niche_name, :category, :target_cluster, :problem_solved,
            :target_mrp_low, :target_mrp_high, :estimated_factory_cost,
            :search_volume_est, :competition_level, :differentiation_hook, :notes, :status
        )
        """
        defaults = {
            "category": "Home & Kitchen", "target_cluster": None, "problem_solved": None,
            "target_mrp_low": 499.0, "target_mrp_high": 999.0, "estimated_factory_cost": 150.0,
            "search_volume_est": 2500, "competition_level": "Low", "differentiation_hook": None,
            "notes": None, "status": "Active Hunting"
        }
        params = {**defaults, **data}
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return cur.lastrowid

    @staticmethod
    def list_hunted_niches() -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM hunted_niches ORDER BY id DESC")
            return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def delete_hunted_niche(niche_id: int) -> bool:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM hunted_niches WHERE id = ?", (niche_id,))
            return cur.rowcount > 0

    # -------------------------------------------------------------
    # Custom Suppliers & Sources (Sourcing Hub)
    # -------------------------------------------------------------
    @staticmethod
    def add_custom_supplier(data: Dict[str, Any]) -> int:
        query = """
        INSERT INTO custom_suppliers (
            supplier_name, hub_city, state, materials_offered,
            contact_person, phone_whatsapp, indiamart_profile_url,
            moq, typical_unit_cost, sample_cost, lead_time_days,
            gst_invoice_available, notes
        ) VALUES (
            :supplier_name, :hub_city, :state, :materials_offered,
            :contact_person, :phone_whatsapp, :indiamart_profile_url,
            :moq, :typical_unit_cost, :sample_cost, :lead_time_days,
            :gst_invoice_available, :notes
        )
        """
        defaults = {
            "state": None, "materials_offered": None, "contact_person": None,
            "phone_whatsapp": None, "indiamart_profile_url": None, "moq": 100,
            "typical_unit_cost": None, "sample_cost": 0.0, "lead_time_days": 14,
            "gst_invoice_available": 1, "notes": None
        }
        params = {**defaults, **data}
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return cur.lastrowid

    @staticmethod
    def list_custom_suppliers() -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM custom_suppliers ORDER BY id DESC")
            return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def delete_custom_supplier(supplier_id: int) -> bool:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM custom_suppliers WHERE id = ?", (supplier_id,))
            return cur.rowcount > 0

    # -------------------------------------------------------------
    # User Research Criteria (Configurable Excel-style Gates)
    # -------------------------------------------------------------
    @staticmethod
    def get_research_criteria() -> Dict[str, Any]:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM user_research_criteria WHERE id = 1")
            row = cur.fetchone()
            if row:
                return dict(row)
            # Default initialized row matching the student Excel sheet
            default_row = {
                "id": 1,
                "min_profit_margin_pct": 31.0, # From Excel: AT LEAST 31% after ad spend
                "max_competitor_reviews": 100,  # From Excel: Median top 10 sellers < 100
                "min_search_volume": 500,       # From Excel: Monthly search volume 500+
                "max_weight_kg": 0.50,
                "min_mrp_inr": 499.0,
                "max_mrp_inr": 1499.0,
                "require_domestic_sourcing": 1,
                "require_non_consumable": 1,
                "require_non_fragile": 1,
                "require_zero_hazmat": 1,
            }
            conn.execute("""
                INSERT OR IGNORE INTO user_research_criteria (
                    id, min_profit_margin_pct, max_competitor_reviews, min_search_volume,
                    max_weight_kg, min_mrp_inr, max_mrp_inr, require_domestic_sourcing,
                    require_non_consumable, require_non_fragile, require_zero_hazmat
                ) VALUES (1, 31.0, 100, 500, 0.50, 499.0, 1499.0, 1, 1, 1, 1)
            """)
            return default_row

    @staticmethod
    def save_research_criteria(criteria: Dict[str, Any]) -> bool:
        query = """
        INSERT INTO user_research_criteria (
            id, min_profit_margin_pct, max_competitor_reviews, min_search_volume,
            max_weight_kg, min_mrp_inr, max_mrp_inr, require_domestic_sourcing,
            require_non_consumable, require_non_fragile, require_zero_hazmat, updated_at
        ) VALUES (
            1, :min_profit_margin_pct, :max_competitor_reviews, :min_search_volume,
            :max_weight_kg, :min_mrp_inr, :max_mrp_inr, :require_domestic_sourcing,
            :require_non_consumable, :require_non_fragile, :require_zero_hazmat, CURRENT_TIMESTAMP
        )
        ON CONFLICT(id) DO UPDATE SET
            min_profit_margin_pct = excluded.min_profit_margin_pct,
            max_competitor_reviews = excluded.max_competitor_reviews,
            min_search_volume = excluded.min_search_volume,
            max_weight_kg = excluded.max_weight_kg,
            min_mrp_inr = excluded.min_mrp_inr,
            max_mrp_inr = excluded.max_mrp_inr,
            require_domestic_sourcing = excluded.require_domestic_sourcing,
            require_non_consumable = excluded.require_non_consumable,
            require_non_fragile = excluded.require_non_fragile,
            require_zero_hazmat = excluded.require_zero_hazmat,
            updated_at = CURRENT_TIMESTAMP
        """
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, criteria)
            return cur.rowcount > 0

