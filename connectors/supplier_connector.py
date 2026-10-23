"""
Supplier Quotation & Landed Cost Connector.
Supports domestic Indian manufacturing clusters (Moradabad, Surat, Panipat, etc.)
and international import sourcing with customs duty modeling.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

class SupplierConnector:
    """Manages supplier quotations and landed cost calculations."""

    INDIAN_CLUSTERS = [
        "Moradabad, UP (Brass, Copper, Metal Crafts)",
        "Surat, Gujarat (Textiles, Apparel, Packaging)",
        "Tirupur, Tamil Nadu (Cotton Knitwear & Garments)",
        "Panipat, Haryana (Home Furnishings & Rugs)",
        "Khurja, UP (Ceramics & Pottery)",
        "Jodhpur / Saharanpur (Wooden Furniture & Decor)",
        "Rajkot / Jamnagar, Gujarat (Kitchenware & Hardware)",
        "Agra / Kanpur, UP (Leather & Footwear)",
        "Bengaluru / Pune (Electronics Assembly & Plastics)",
        "Delhi-NCR (General Consumer Goods & Packaging)",
    ]

    @classmethod
    def calculate_domestic_landed_cost(
        cls,
        unit_purchase_cost: float,
        packaging_cost: float = 0.0,
        inward_freight_per_unit: float = 0.0,
        inspection_cost_per_unit: float = 0.0,
        defect_allowance_pct: float = 2.0,
        gst_rate_pct: float = 18.0,
        is_gst_registered: bool = True
    ) -> Dict[str, Any]:
        """
        Calculates domestic landed cost per unit in INR.
        For a GST-registered business, sourcing GST is an Input Tax Credit (ITC).
        """
        defect_cost = unit_purchase_cost * (defect_allowance_pct / 100.0)
        base_cost_excl_tax = unit_purchase_cost + packaging_cost + inward_freight_per_unit + inspection_cost_per_unit + defect_cost
        
        sourcing_gst_amount = base_cost_excl_tax * (gst_rate_pct / 100.0)

        if is_gst_registered:
            # ITC is recovered against output tax liability
            effective_landed_cost = base_cost_excl_tax
            itc_recoverable = sourcing_gst_amount
            sunk_tax = 0.0
        else:
            effective_landed_cost = base_cost_excl_tax + sourcing_gst_amount
            itc_recoverable = 0.0
            sunk_tax = sourcing_gst_amount

        return {
            "sourcing_type": "Domestic (India)",
            "unit_purchase_cost": round(unit_purchase_cost, 2),
            "packaging_cost": round(packaging_cost, 2),
            "inward_freight_per_unit": round(inward_freight_per_unit, 2),
            "defect_cost_per_unit": round(defect_cost, 2),
            "inspection_cost_per_unit": round(inspection_cost_per_unit, 2),
            "base_cost_excl_tax": round(base_cost_excl_tax, 2),
            "sourcing_gst_amount": round(sourcing_gst_amount, 2),
            "itc_recoverable": round(itc_recoverable, 2),
            "effective_landed_cost": round(effective_landed_cost, 2),
        }

    @classmethod
    def calculate_import_landed_cost(
        cls,
        fob_cost_foreign: float,
        exchange_rate_to_inr: float = 84.0, # e.g. USD to INR
        international_freight_inr: float = 40.0,
        insurance_inr: float = 5.0,
        bcd_rate_pct: float = 10.0, # Basic Customs Duty (10-20% standard)
        sws_rate_pct: float = 10.0, # Social Welfare Surcharge (10% of BCD)
        import_igst_pct: float = 18.0,
        clearing_port_handling_inr: float = 15.0,
        packaging_inr: float = 10.0,
        is_gst_registered: bool = True
    ) -> Dict[str, Any]:
        """
        Calculates imported goods landed cost into India according to Indian Customs rules.
        Assessable Value (CIF) = FOB + Freight + Insurance
        BCD = BCD% on Assessable Value
        SWS = 10% on BCD
        IGST = 18% on (Assessable Value + BCD + SWS). *IGST is eligible for ITC.*
        """
        fob_inr = fob_cost_foreign * exchange_rate_to_inr
        cif_assessable_value = fob_inr + international_freight_inr + insurance_inr

        bcd_amount = cif_assessable_value * (bcd_rate_pct / 100.0)
        sws_amount = bcd_amount * (sws_rate_pct / 100.0)
        
        customs_duty_total = bcd_amount + sws_amount
        igst_base = cif_assessable_value + customs_duty_total
        igst_amount = igst_base * (import_igst_pct / 100.0)

        # Non-tax logistics
        other_costs = clearing_port_handling_inr + packaging_inr

        if is_gst_registered:
            # IGST is recoverable as Input Tax Credit with bill of entry
            effective_landed_cost = cif_assessable_value + customs_duty_total + other_costs
            itc_recoverable = igst_amount
        else:
            effective_landed_cost = cif_assessable_value + customs_duty_total + igst_amount + other_costs
            itc_recoverable = 0.0

        return {
            "sourcing_type": "Overseas Import",
            "fob_inr": round(fob_inr, 2),
            "cif_assessable_value": round(cif_assessable_value, 2),
            "bcd_amount": round(bcd_amount, 2),
            "sws_amount": round(sws_amount, 2),
            "customs_duty_total": round(customs_duty_total, 2),
            "igst_amount": round(igst_amount, 2),
            "itc_recoverable": round(itc_recoverable, 2),
            "other_handling_costs": round(other_costs, 2),
            "effective_landed_cost": round(effective_landed_cost, 2),
        }
