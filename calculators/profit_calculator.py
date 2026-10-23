"""
Amazon India Profitability & Unit Economics Calculator.
Implements Indian GST (Output GST vs Input Tax Credit ITC), FBA/Easy Ship/Self Ship fee schedules,
landed cost estimation, and multi-scenario projections.
"""

from typing import Dict, Any, Tuple
import math
from config.settings import (
    AMAZON_REFERRAL_FEE_RATES,
    AMAZON_CLOSING_FEE_SLABS,
    WEIGHT_HANDLING_FEES,
    AMAZON_FEE_GST_RATE,
    STORAGE_FEE_PER_CUFT_MONTH,
    ZRF_PRICE_THRESHOLD,
    ZRF_ELIGIBLE_CATEGORIES,
)

class ProfitCalculator:
    """Calculates granular unit economics for products sold on Amazon India."""

    @staticmethod
    def calculate_volumetric_weight_kg(length_cm: float, width_cm: float, height_cm: float) -> float:
        """Amazon India volumetric divisor: (L x W x H) / 5000 in cm."""
        if length_cm <= 0 or width_cm <= 0 or height_cm <= 0:
            return 0.1
        return round((length_cm * width_cm * height_cm) / 5000.0, 3)

    @staticmethod
    def calculate_cubic_feet(length_cm: float, width_cm: float, height_cm: float) -> float:
        """Converts dimensions in cm to cubic feet (1 cu ft = 28,316.85 cm³)."""
        if length_cm <= 0 or width_cm <= 0 or height_cm <= 0:
            return 0.01
        return (length_cm * width_cm * height_cm) / 28316.85

    @staticmethod
    def get_referral_fee(
        selling_price_gross: float,
        category: str,
        custom_rate: float = None,
        apply_zrf: bool = False
    ) -> float:
        """
        Calculates Amazon India referral fee based on category percentage.
        When apply_zrf is True, products <= ZRF_PRICE_THRESHOLD (₹1,000) in eligible categories receive 0% referral fee.
        """
        if apply_zrf and selling_price_gross <= ZRF_PRICE_THRESHOLD and category in ZRF_ELIGIBLE_CATEGORIES and custom_rate is None:
            return 0.0

        rate = custom_rate if custom_rate is not None else AMAZON_REFERRAL_FEE_RATES.get(category, 0.10)
        fee = selling_price_gross * rate
        # Category minimum fee floor (typically ₹3-₹5 in India)
        return max(fee, 3.0)

    @staticmethod
    def get_closing_fee(selling_price_gross: float, fulfilment_model: str = "FBA") -> float:
        """Calculates closing fee based on price band and fulfilment channel."""
        model = fulfilment_model if fulfilment_model in AMAZON_CLOSING_FEE_SLABS else "FBA"
        slabs = AMAZON_CLOSING_FEE_SLABS[model]
        for slab in slabs:
            if slab["min"] <= selling_price_gross <= slab["max"]:
                return slab["fee"]
        return slabs[-1]["fee"]

    @staticmethod
    def get_weight_handling_fee(
        actual_weight_kg: float,
        volumetric_weight_kg: float,
        fulfilment_model: str = "FBA",
        delivery_zone: str = "national"
    ) -> float:
        """
        Calculates shipping/weight handling fee based on max(actual, volumetric) weight.
        Amazon India charges per 500g slab.
        """
        billable_weight_kg = max(actual_weight_kg, volumetric_weight_kg)
        model = fulfilment_model if fulfilment_model in WEIGHT_HANDLING_FEES else "FBA"
        rates = WEIGHT_HANDLING_FEES[model]
        zone = delivery_zone.lower()
        if zone not in ["local", "regional", "national"]:
            zone = "national"

        if model == "Self Ship":
            return 0.0

        first_500g = rates["first_500g"][zone]
        if billable_weight_kg <= 0.5:
            return first_500g
        elif billable_weight_kg <= 1.0:
            add_500g = rates["additional_500g_up_to_1kg"][zone]
            return first_500g + add_500g
        else:
            # 1.0kg baseline fee
            base_1kg = first_500g + rates["additional_500g_up_to_1kg"][zone]
            extra_kg = math.ceil(billable_weight_kg - 1.0)
            extra_rate = rates["additional_kg_above_1kg"][zone]
            return base_1kg + (extra_kg * extra_rate)

    @classmethod
    def calculate_unit_economics(
        cls,
        selling_price_gross: float, # Retail listing price inclusive of GST (MRP)
        sourcing_cost_unit: float,  # Landed sourcing cost per unit (excl. recoverable tax)
        category: str = "Home & Kitchen",
        actual_weight_kg: float = 0.5,
        length_cm: float = 15.0,
        width_cm: float = 10.0,
        height_cm: float = 5.0,
        fulfilment_model: str = "FBA",
        gst_rate: float = 0.18,
        is_gst_registered: bool = True,
        ad_spend_pct: float = 0.12, # Target PPC Advertising Cost of Sales (ACoS % of gross revenue)
        return_rate_pct: float = 0.07, # Expected customer return rate
        loss_on_return_pct: float = 0.25, # Unsellable/repackaging loss on returned units
        inventory_storage_days: int = 35,
        delivery_zone: str = "national",
        custom_referral_rate: float = None,
        promotional_discount_unit: float = 0.0,
        apply_zrf: bool = False
    ) -> Dict[str, Any]:
        """
        Performs full financial calculation and returns structured metrics with an audit log.
        """
        audit_trail = []
        
        # 1. Dimensions & Weights
        volumetric_weight_kg = cls.calculate_volumetric_weight_kg(length_cm, width_cm, height_cm)
        billable_weight_kg = max(actual_weight_kg, volumetric_weight_kg)
        cuft = cls.calculate_cubic_feet(length_cm, width_cm, height_cm)
        
        audit_trail.append(f"Dimensions: {length_cm}x{width_cm}x{height_cm} cm | Actual: {actual_weight_kg}kg | Volumetric: {volumetric_weight_kg}kg | Billable: {billable_weight_kg}kg")

        # 2. Revenue & Output GST
        # In India, selling price on Amazon is MRP (GST inclusive).
        if is_gst_registered and gst_rate > 0:
            net_selling_price_ex_tax = selling_price_gross / (1.0 + gst_rate)
            output_gst_liability = selling_price_gross - net_selling_price_ex_tax
        else:
            net_selling_price_ex_tax = selling_price_gross
            output_gst_liability = 0.0

        audit_trail.append(f"Gross Selling Price: ₹{selling_price_gross:.2f} | Net Excl. GST: ₹{net_selling_price_ex_tax:.2f} | Output GST: ₹{output_gst_liability:.2f} ({gst_rate*100:.0f}%)")

        # 3. Amazon Marketplace Service Fees (Excl. 18% Service GST)
        referral_fee = cls.get_referral_fee(selling_price_gross, category, custom_referral_rate, apply_zrf=apply_zrf)
        closing_fee = cls.get_closing_fee(selling_price_gross, fulfilment_model)
        weight_handling_fee = cls.get_weight_handling_fee(actual_weight_kg, volumetric_weight_kg, fulfilment_model, delivery_zone)
        
        pick_pack_fee = 16.0 if fulfilment_model == "FBA" else 0.0
        
        # Monthly storage allocated per unit
        storage_month_fee = cuft * STORAGE_FEE_PER_CUFT_MONTH
        storage_fee = (storage_month_fee / 30.0) * inventory_storage_days if fulfilment_model == "FBA" else 0.0

        amazon_fees_subtotal_ex_tax = referral_fee + closing_fee + weight_handling_fee + pick_pack_fee + storage_fee
        amazon_fees_service_gst = amazon_fees_subtotal_ex_tax * AMAZON_FEE_GST_RATE
        total_amazon_fees_gross = amazon_fees_subtotal_ex_tax + amazon_fees_service_gst

        is_zrf_applied = (apply_zrf and selling_price_gross <= ZRF_PRICE_THRESHOLD and category in ZRF_ELIGIBLE_CATEGORIES and custom_referral_rate is None)
        if is_zrf_applied:
            audit_trail.append("Zero Referral Fee (ZRF) Applied: 0% referral fee for item <= ₹1,000 in eligible category.")

        audit_trail.append(
            f"Amazon Fees (Ex-Tax): Referral=₹{referral_fee:.2f}{' (ZRF 0%)' if is_zrf_applied else ''}, Closing=₹{closing_fee:.2f}, "
            f"Shipping=₹{weight_handling_fee:.2f}, PickPack=₹{pick_pack_fee:.2f}, Storage=₹{storage_fee:.2f}. "
            f"Subtotal=₹{amazon_fees_subtotal_ex_tax:.2f} + 18% GST=₹{amazon_fees_service_gst:.2f}"
        )

        # 4. Input Tax Credit (ITC)
        # If GST registered, seller recovers:
        # a) GST on Amazon service fees (100% recoverable)
        # b) GST paid on domestic sourcing (assumed included in quote at product gst_rate if recoverable)
        if is_gst_registered:
            itc_amazon_fees = amazon_fees_service_gst
            itc_sourcing = sourcing_cost_unit * gst_rate # Sourcing GST offset
            total_itc_recoverable = itc_amazon_fees + itc_sourcing
            net_gst_payable = max(0.0, output_gst_liability - total_itc_recoverable)
            effective_tax_cost = 0.0 # ITC offsets liability
        else:
            total_itc_recoverable = 0.0
            net_gst_payable = 0.0
            effective_tax_cost = amazon_fees_service_gst # Becomes sunk cost

        # 5. Advertising & Marketing Budget
        ad_spend_unit = selling_price_gross * ad_spend_pct

        # 6. Returns & Damage Cost per Unit Sold
        # Formula: Expected return rate * (loss on resale + return handling)
        return_cost_unit = selling_price_gross * return_rate_pct * loss_on_return_pct

        # 7. Net Contribution Profit per Unit
        # For a GST-registered business:
        # Profit = Net Selling Price (Ex-GST) - Sourcing Cost (Ex-GST) - Amazon Fees (Ex-GST) - Ad Spend (Ex-GST) - Returns - Promo
        ad_spend_ex_tax = ad_spend_unit / (1.0 + 0.18) if is_gst_registered else ad_spend_unit
        
        net_profit_unit = (
            net_selling_price_ex_tax
            - sourcing_cost_unit
            - amazon_fees_subtotal_ex_tax
            - ad_spend_ex_tax
            - return_cost_unit
            - promotional_discount_unit
        )

        # 8. Margins & ROI
        margin_pct = (net_profit_unit / net_selling_price_ex_tax * 100.0) if net_selling_price_ex_tax > 0 else 0.0
        roi_pct = (net_profit_unit / sourcing_cost_unit * 100.0) if sourcing_cost_unit > 0 else 0.0

        # 9. Break-Even Calculations
        # Pre-ad profit per unit
        pre_ad_profit = (
            net_selling_price_ex_tax
            - sourcing_cost_unit
            - amazon_fees_subtotal_ex_tax
            - return_cost_unit
            - promotional_discount_unit
        )
        breakeven_acos_pct = (pre_ad_profit / selling_price_gross * 100.0) if selling_price_gross > 0 else 0.0

        # Break-even selling price (Iterative approximation for variable referral + closing fee)
        be_price = cls._calculate_breakeven_price(
            sourcing_cost_unit,
            weight_handling_fee + pick_pack_fee + storage_fee,
            category,
            fulfilment_model,
            gst_rate,
            is_gst_registered,
            return_rate_pct * loss_on_return_pct,
            apply_zrf=apply_zrf
        )

        return {
            "scenario_name": "Base",
            "selling_price_gross": round(selling_price_gross, 2),
            "net_selling_price_ex_tax": round(net_selling_price_ex_tax, 2),
            "net_revenue_excl_tax": round(net_selling_price_ex_tax, 2),
            "gst_rate": gst_rate,
            "is_gst_registered": 1 if is_gst_registered else 0,
            "fulfilment_model": fulfilment_model,
            "output_gst_liability": round(output_gst_liability, 2),
            "sourcing_cost_unit": round(sourcing_cost_unit, 2),
            "landed_cost_unit": round(sourcing_cost_unit, 2),
            "referral_fee": round(referral_fee, 2),
            "is_zrf_applied": is_zrf_applied,
            "closing_fee": round(closing_fee, 2),
            "weight_handling_fee": round(weight_handling_fee, 2),
            "pick_pack_fee": round(pick_pack_fee, 2),
            "storage_fee": round(storage_fee, 2),
            "amazon_fees_subtotal_ex_tax": round(amazon_fees_subtotal_ex_tax, 2),
            "amazon_fees_service_gst": round(amazon_fees_service_gst, 2),
            "amazon_fee_gst": round(amazon_fees_service_gst, 2),
            "total_amazon_fees_gross": round(total_amazon_fees_gross, 2),
            "itc_amazon_fees": round(total_itc_recoverable, 2),
            "net_gst_payable": round(net_gst_payable, 2),
            "ad_spend_unit": round(ad_spend_unit, 2),
            "advertising_spend_unit": round(ad_spend_unit, 2),
            "ad_spend_pct": round(ad_spend_pct * 100, 1),
            "advertising_spend_pct": round(ad_spend_pct * 100, 1),
            "return_cost_unit": round(return_cost_unit, 2),
            "returns_cost_unit": round(return_cost_unit, 2),
            "return_rate_pct": round(return_rate_pct * 100, 1),
            "returns_allowance_pct": round(return_rate_pct * 100, 1),
            "promotional_discount_unit": round(promotional_discount_unit, 2),
            "net_profit_unit": round(net_profit_unit, 2),
            "margin_pct": round(margin_pct, 1),
            "roi_pct": round(roi_pct, 1),
            "breakeven_acos_pct": round(breakeven_acos_pct, 1),
            "breakeven_selling_price": round(be_price, 2),
            "monthly_units_est": 100,
            "monthly_net_profit": round(net_profit_unit * 100, 2),
            "assumptions_json": f'{{"category": "{category}", "delivery_zone": "{delivery_zone}"}}',
            "volumetric_weight_kg": volumetric_weight_kg,
            "billable_weight_kg": billable_weight_kg,
            "audit_trail": audit_trail,
        }

    @classmethod
    def _calculate_breakeven_price(
        cls,
        sourcing_cost: float,
        fixed_shipping_and_storage: float,
        category: str,
        fulfilment_model: str,
        gst_rate: float,
        is_gst_registered: bool,
        return_loss_factor: float,
        apply_zrf: bool = False
    ) -> float:
        """Solves for price where Net Profit = 0."""
        # Search from sourcing_cost up to 10x sourcing_cost
        low, high = sourcing_cost, sourcing_cost * 10.0 + 500.0
        for _ in range(30):
            mid = (low + high) / 2.0
            closing = cls.get_closing_fee(mid, fulfilment_model)
            ref = cls.get_referral_fee(mid, category, apply_zrf=apply_zrf)
            fees = ref + closing + fixed_shipping_and_storage
            net_rev = (mid / (1.0 + gst_rate)) if (is_gst_registered and gst_rate > 0) else mid
            profit = net_rev - sourcing_cost - fees - (mid * return_loss_factor)
            if profit < 0:
                low = mid
            else:
                high = mid
        return round(mid, 2)

    @classmethod
    def generate_three_scenarios(
        cls,
        base_price: float,
        base_sourcing: float,
        category: str = "Home & Kitchen",
        weight_kg: float = 0.5,
        length_cm: float = 15.0,
        width_cm: float = 10.0,
        height_cm: float = 5.0,
        fulfilment_model: str = "FBA",
        gst_rate: float = 0.18,
        is_gst_registered: bool = True,
        monthly_units: int = 150,
        apply_zrf: bool = False
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generates Conservative, Base, and Optimistic financial projections.
        """
        # Conservative: 10% lower price, +10% sourcing cost, 20% PPC ACoS, 12% return rate
        cons_price = round(base_price * 0.90, 2)
        cons_sourcing = round(base_sourcing * 1.10, 2)
        conservative = cls.calculate_unit_economics(
            selling_price_gross=cons_price,
            sourcing_cost_unit=cons_sourcing,
            category=category,
            actual_weight_kg=weight_kg,
            length_cm=length_cm,
            width_cm=width_cm,
            height_cm=height_cm,
            fulfilment_model=fulfilment_model,
            gst_rate=gst_rate,
            is_gst_registered=is_gst_registered,
            ad_spend_pct=0.20,
            return_rate_pct=0.12,
            apply_zrf=apply_zrf
        )
        conservative["scenario_name"] = "Conservative"
        conservative["monthly_units_est"] = int(monthly_units * 0.7)
        conservative["monthly_net_profit"] = round(conservative["net_profit_unit"] * conservative["monthly_units_est"], 2)

        # Base: Observed price, quoted sourcing, 12% PPC ACoS, 7% return rate
        base = cls.calculate_unit_economics(
            selling_price_gross=base_price,
            sourcing_cost_unit=base_sourcing,
            category=category,
            actual_weight_kg=weight_kg,
            length_cm=length_cm,
            width_cm=width_cm,
            height_cm=height_cm,
            fulfilment_model=fulfilment_model,
            gst_rate=gst_rate,
            is_gst_registered=is_gst_registered,
            ad_spend_pct=0.12,
            return_rate_pct=0.07,
            apply_zrf=apply_zrf
        )
        base["scenario_name"] = "Base"
        base["monthly_units_est"] = monthly_units
        base["monthly_net_profit"] = round(base["net_profit_unit"] * base["monthly_units_est"], 2)

        # Optimistic: +10% price, -5% bulk sourcing discount, 6% PPC ACoS, 4% return rate
        opt_price = round(base_price * 1.10, 2)
        opt_sourcing = round(base_sourcing * 0.95, 2)
        optimistic = cls.calculate_unit_economics(
            selling_price_gross=opt_price,
            sourcing_cost_unit=opt_sourcing,
            category=category,
            actual_weight_kg=weight_kg,
            length_cm=length_cm,
            width_cm=width_cm,
            height_cm=height_cm,
            fulfilment_model=fulfilment_model,
            gst_rate=gst_rate,
            is_gst_registered=is_gst_registered,
            ad_spend_pct=0.06,
            return_rate_pct=0.04,
            apply_zrf=apply_zrf
        )
        optimistic["scenario_name"] = "Optimistic"
        optimistic["monthly_units_est"] = int(monthly_units * 1.4)
        optimistic["monthly_net_profit"] = round(optimistic["net_profit_unit"] * optimistic["monthly_units_est"], 2)

        return {
            "Conservative": conservative,
            "Base": base,
            "Optimistic": optimistic,
        }
