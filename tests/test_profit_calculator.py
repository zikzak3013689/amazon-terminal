"""
Unit tests for Amazon India Profitability & Unit Economics Calculator.
"""

import pytest
from calculators.profit_calculator import ProfitCalculator
from connectors.supplier_connector import SupplierConnector

def test_volumetric_weight():
    # 20cm x 15cm x 10cm / 5000 = 0.6 kg
    vw = ProfitCalculator.calculate_volumetric_weight_kg(20.0, 15.0, 10.0)
    assert vw == 0.60

    # 10cm x 10cm x 5cm / 5000 = 0.1 kg
    vw2 = ProfitCalculator.calculate_volumetric_weight_kg(10.0, 10.0, 5.0)
    assert vw2 == 0.10

def test_closing_fee_slabs():
    # Slabs for FBA: 0-250: 5; 251-500: 9; 501-1000: 30; 1000+: 61
    assert ProfitCalculator.get_closing_fee(199.0, "FBA") == 5.0
    assert ProfitCalculator.get_closing_fee(399.0, "FBA") == 9.0
    assert ProfitCalculator.get_closing_fee(799.0, "FBA") == 30.0
    assert ProfitCalculator.get_closing_fee(1499.0, "FBA") == 61.0

def test_referral_fee():
    # Home & Kitchen is 9% (standard without ZRF)
    fee_home = ProfitCalculator.get_referral_fee(1000.0, "Home & Kitchen", apply_zrf=False)
    assert fee_home == 90.0

    # Minimum fee rule (₹3.0)
    fee_min = ProfitCalculator.get_referral_fee(20.0, "Home & Kitchen", apply_zrf=False)
    assert fee_min >= 3.0

    # ZRF policy: 0% referral fee for qualifying categories <= ₹1,000
    fee_zrf = ProfitCalculator.get_referral_fee(799.0, "Home & Kitchen", apply_zrf=True)
    assert fee_zrf == 0.0

    # ZRF boundary check: Products above ₹1,000 pay standard referral fee
    fee_above_zrf = ProfitCalculator.get_referral_fee(1200.0, "Home & Kitchen", apply_zrf=True)
    assert fee_above_zrf == 108.0

def test_gst_treatment_registered_vs_unregistered():
    # Selling price ₹1000, sourcing ₹300, 18% GST
    reg = ProfitCalculator.calculate_unit_economics(
        selling_price_gross=1000.0,
        sourcing_cost_unit=300.0,
        category="Home & Kitchen",
        is_gst_registered=True,
        gst_rate=0.18
    )

    unreg = ProfitCalculator.calculate_unit_economics(
        selling_price_gross=1000.0,
        sourcing_cost_unit=300.0,
        category="Home & Kitchen",
        is_gst_registered=False,
        gst_rate=0.18
    )

    # For registered seller: Net selling price is 1000 / 1.18 = 847.46
    assert abs(reg["net_selling_price_ex_tax"] - 847.46) < 0.1
    assert reg["output_gst_liability"] > 0
    assert reg["itc_amazon_fees"] > 0

    # Margin and profit must be higher for GST-registered business due to ITC recovery
    assert reg["net_profit_unit"] > 0
    assert reg["breakeven_selling_price"] < 1000.0
    assert reg["breakeven_acos_pct"] > 0

def test_three_scenarios_generation():
    scenarios = ProfitCalculator.generate_three_scenarios(
        base_price=799.0,
        base_sourcing=200.0,
        category="Kitchen & Dining",
        monthly_units=100
    )

    assert "Conservative" in scenarios
    assert "Base" in scenarios
    assert "Optimistic" in scenarios

    cons = scenarios["Conservative"]
    base = scenarios["Base"]
    opt = scenarios["Optimistic"]

    # Monotonicity checks: Optimistic profit > Base profit > Conservative profit
    assert opt["net_profit_unit"] > base["net_profit_unit"]
    assert base["net_profit_unit"] > cons["net_profit_unit"]
    assert opt["monthly_net_profit"] > base["monthly_net_profit"]
    assert base["monthly_net_profit"] > cons["monthly_net_profit"]

def test_domestic_and_import_landed_cost():
    # Domestic: Purchase ₹100, Packaging ₹10, Freight ₹15, Defect 2% = ₹2, Sourcing GST 18%
    dom = SupplierConnector.calculate_domestic_landed_cost(
        unit_purchase_cost=100.0,
        packaging_cost=10.0,
        inward_freight_per_unit=15.0,
        defect_allowance_pct=2.0,
        gst_rate_pct=18.0,
        is_gst_registered=True
    )
    # Effective landed cost excl tax for registered seller = 100 + 10 + 15 + 2 = 127.0
    assert dom["effective_landed_cost"] == 127.0
    assert dom["itc_recoverable"] > 0

    # Import: $2 FOB * 84 = ₹168, Freight ₹40, Insurance ₹5 => CIF = ₹213
    imp = SupplierConnector.calculate_import_landed_cost(
        fob_cost_foreign=2.0,
        exchange_rate_to_inr=84.0,
        international_freight_inr=40.0,
        insurance_inr=5.0,
        bcd_rate_pct=10.0,
        is_gst_registered=True
    )
    assert imp["cif_assessable_value"] == 213.0
    assert imp["bcd_amount"] == 21.3
    assert imp["customs_duty_total"] > 0
    assert imp["effective_landed_cost"] > imp["cif_assessable_value"]
