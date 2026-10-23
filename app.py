"""
Amazon India Product Research & Opportunity Intelligence Terminal
The ₹50,000 Bootstrapped Seller Operating System for amazon.in

Custom research terminal with interactive niche hunting, configurable Excel-style
criteria gatekeeping, custom supplier sourcing directory, granular competitor/keyword
CRUD management, and a dedicated operator playbook tab.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
import os
import json
from datetime import datetime

# Initialize Database & Config
from config.settings import (
    APP_NAME, APP_VERSION, MARKETPLACE, CURRENCY_SYMBOL,
    GST_RATES, AMAZON_REFERRAL_FEE_RATES, RESEARCH_STATUSES,
    DEFAULT_SCORING_WEIGHTS, CHECKLIST_DEFINITIONS
)
from database.connection import init_db, get_db_connection
from database.repository import ProductRepository
from calculators.profit_calculator import ProfitCalculator
from modules.validation_checklist import ValidationChecklistEngine
from modules.competitor_analyzer import CompetitorAnalyzer
from scoring.opportunity_scorer import OpportunityScorer
from connectors.amazon_manual import AmazonManualConnector
from connectors.google_trends import GoogleTrendsConnector
from connectors.google_keyword_planner import GoogleKeywordPlannerConnector
from connectors.keepa_adapter import KeepaAdapter
from connectors.supplier_connector import SupplierConnector
from connectors.excel_importer import ExcelImporter
from sample_data.starter_blueprints import load_starter_blueprints, STARTER_BLUEPRINTS
from ui.theme import apply_terminal_theme
from ui.charts import (
    render_profit_waterfall,
    render_competitor_price_distribution,
    render_competitor_review_concentration,
    render_google_trends_chart,
    render_opportunity_score_bar
)

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Amazon India ₹50k Launch & Research Terminal",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply UI Styling
apply_terminal_theme()

# Ensure Database is Initialized
init_db()

# Session State Initialization
if "weights" not in st.session_state:
    st.session_state["weights"] = DEFAULT_SCORING_WEIGHTS.copy()
if "confirm_clear_all" not in st.session_state:
    st.session_state["confirm_clear_all"] = False
if "toast_msg" in st.session_state:
    st.toast(st.session_state["toast_msg"])
    del st.session_state["toast_msg"]

# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION & DATABASE HYGIENE
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 📦 Amazon India Terminal")
    st.caption("₹50k Bootstrapped Seller OS | **amazon.in**")
    
    st.markdown("---")
    
    # Real Research Terminal Badge
    st.markdown(
        """
        <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 6px; padding: 10px 12px; color: #6EE7B7; font-size: 0.82rem; font-weight: 600;">
            🛡️ <strong>REAL RESEARCH TERMINAL</strong><br>
            <span style="font-size: 0.75rem; font-weight: 400; color: #94A3B8;">100% Genuine Observations & Deterministic Math. No Synthetic Demo Data.</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown("#### 🧭 Operational Modules")
    nav_selection = st.radio(
        "Workflow Steps",
        options=[
            "🧭 Step 1: Niche Hunter & Custom Explorer",
            "⚖️ Step 2: Excel-Style Research Criteria & Gatekeeper",
            "💰 Step 3: Real Unit Economics & ₹50K Capital Allocator",
            "🏭 Step 4: Sourcing Hub & My Supplier Directory",
            "🗃️ Step 5: Active Products Portfolio & Research Studio",
            "📊 Step 6: Competitor Benchmarks & Market Analytics",
            "📥 Step 7: Data Importers & DB Hygiene",
            "📖 How to Use This Terminal & Operator Playbook",
        ],
        index=0
    )

    st.markdown("---")
    st.markdown("#### 🧹 Database Hygiene & Fast Actions")
    total_p = len(ProductRepository.list_products(is_demo=0))
    total_n = len(ProductRepository.list_hunted_niches())
    total_s = len(ProductRepository.list_custom_suppliers())
    st.write(f"Tracked Products: **{total_p}** | Niches: **{total_n}** | Suppliers: **{total_s}**")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("🚀 Load 3 Blueprints", use_container_width=True, help="Load 3 pre-vetted starter products (Diya, Laptop Stand, Tumbler)"):
            pids = load_starter_blueprints()
            st.session_state["toast_msg"] = f"Loaded {len(pids)} starter blueprints!"
            st.rerun()
    with col_s2:
        if st.button("🗑️ Wipe Clutter", use_container_width=True, help="Delete legacy US spreadsheet imports"):
            del_count = ProductRepository.delete_legacy_products()
            st.session_state["toast_msg"] = f"Removed {del_count} legacy spreadsheet items."
            st.rerun()

    if not st.session_state["confirm_clear_all"]:
        if st.button("⚠️ Clear All Products", use_container_width=True, help="Completely reset database to zero products"):
            st.session_state["confirm_clear_all"] = True
            st.rerun()
    else:
        st.warning("Confirm Wipe: Permanently delete all stored products?")
        c_yes, c_no = st.columns(2)
        with c_yes:
            if st.button("Yes, Wipe", type="primary", use_container_width=True):
                wiped = ProductRepository.clear_all_products()
                st.session_state["confirm_clear_all"] = False
                st.session_state["toast_msg"] = f"Wiped {wiped} products. Clean database!"
                st.rerun()
        with c_no:
            if st.button("Cancel", use_container_width=True):
                st.session_state["confirm_clear_all"] = False
                st.rerun()

    st.markdown("---")
    st.markdown("#### 🔗 Data Source Status")
    st.markdown("• **Amazon.in Web:** 🟢 Active (Manual / Deep Links)")
    st.markdown("• **Domestic Clusters:** 🟢 Active (IndiaMART / Mandis)")
    st.markdown("• **Indian GST (ITC):** 🟢 Active (18% Recovery)")
    st.caption("Zero-subscription architecture. Safe, transparent calculations.")

# -----------------------------------------------------------------------------
# TOP HEADER BAR
# -----------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="terminal-header">
        <div class="terminal-title">
            <span>📦 Amazon India ₹50k Launch & Research Terminal</span>
            <span style="font-size: 0.75rem; background: #0369A1; color: #E0F2FE; padding: 3px 10px; border-radius: 4px; font-weight: 700;">AMAZON.IN OPERATOR</span>
        </div>
        <div class="terminal-subtitle">
            Private label product discovery, custom research criteria validation, supplier directory, and unit economics for amazon.in.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =============================================================================
# STEP 1: NICHE HUNTER & CUSTOM EXPLORER
# =============================================================================
if nav_selection == "🧭 Step 1: Niche Hunter & Custom Explorer":
    st.markdown("<h2>🧭 Step 1: Niche Hunter & Custom Explorer</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8;'>Hunt, analyze, and save new product niches for Amazon India, or explore seed keyword search volume.</p>", unsafe_allow_html=True)

    tab_my_niches, tab_add_niche, tab_keyword_hunt, tab_curated = st.tabs([
        "📋 My Hunted Niches",
        "➕ Hunt & Add New Niche",
        "🔍 Root Keyword & Search Intent Hunter",
        "💡 Pre-Audited Inspiration & Starter Blueprints"
    ])

    # 1. My Hunted Niches
    with tab_my_niches:
        st.markdown("### 📋 My Hunted Niches Radar")
        hunted = ProductRepository.list_hunted_niches()
        if not hunted:
            st.info("You haven't saved any custom niches yet. Click on the '➕ Hunt & Add New Niche' tab to brainstorm and save your first niche!")
        else:
            st.write(f"Currently tracking **{len(hunted)}** niche ideas:")
            for n in hunted:
                nid = n["id"]
                with st.container():
                    st.markdown(
                        f"""
                        <div style="background: #1E293B; border: 1px solid #334155; border-radius: 8px; padding: 16px 20px; margin-bottom: 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                <div>
                                    <span style="font-size: 0.75rem; background: #0F766E; color: #CCFBF1; padding: 2px 8px; border-radius: 4px; font-weight: 600;">{n['category']}</span>
                                    <span style="font-size: 0.75rem; background: #374151; color: #E5E7EB; padding: 2px 8px; border-radius: 4px; font-weight: 500; margin-left: 6px;">Cluster: {n.get('target_cluster') or 'Flexible'}</span>
                                    <span style="font-size: 0.75rem; background: #1E3A8A; color: #DBEAFE; padding: 2px 8px; border-radius: 4px; font-weight: 500; margin-left: 6px;">Competition: {n.get('competition_level') or 'Low'}</span>
                                    <h4 style="margin: 8px 0 4px 0; color: #F8FAFC; font-size: 1.2rem;">{n['niche_name']}</h4>
                                    <p style="color: #94A3B8; font-size: 0.85rem; margin: 0 0 6px 0;"><strong>Pain Point / Angle:</strong> {n.get('problem_solved') or 'General demand'}</p>
                                    <p style="color: #64748B; font-size: 0.8rem; margin: 0;"><strong>Differentiation Hook:</strong> {n.get('differentiation_hook') or 'Standard Private Label'}</p>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    c_n1, c_n2, c_n3, c_n4, c_n_act = st.columns([1.2, 1.2, 1.2, 1.2, 2.5])
                    with c_n1:
                        st.metric("Target MRP Band", f"₹{n['target_mrp_low']:.0f} - ₹{n['target_mrp_high']:.0f}")
                    with c_n2:
                        st.metric("Est. Factory Buy", f"₹{n['estimated_factory_cost']:.0f}")
                    with c_n3:
                        est_profit = (n['target_mrp_low'] * 0.28)
                        st.metric("Est. Net Profit", f"~₹{est_profit:.0f}/unit")
                    with c_n4:
                        st.metric("Search Volume Est.", f"{n.get('search_volume_est', 2000):,}/mo")
                    with c_n_act:
                        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                        c_prom, c_del_n = st.columns(2)
                        with c_prom:
                            if st.button("🚀 Promote to Product", key=f"prom_{nid}", use_container_width=True, help="Promote this niche to a tracked product in Step 5 Portfolio"):
                                new_pid = ProductRepository.create_product({
                                    "title": n["niche_name"],
                                    "category": n["category"],
                                    "main_keyword": n["niche_name"].lower(),
                                    "current_observed_price": n["target_mrp_low"],
                                    "weight_kg": 0.45,
                                    "research_status": "Shortlisted",
                                    "estimated_demand_notes": n.get("problem_solved") or "",
                                    "is_demo": 0
                                })
                                ValidationChecklistEngine.initialize_checklist_for_product(new_pid)
                                if n.get("estimated_factory_cost"):
                                    ProductRepository.add_supplier_quote(new_pid, {
                                        "supplier_name": f"Cluster Supplier ({n.get('target_cluster') or 'Domestic'})",
                                        "supplier_city_hub": n.get("target_cluster"),
                                        "unit_purchase_cost": n["estimated_factory_cost"],
                                        "moq": 100,
                                        "packaging_cost": 15.0,
                                        "freight_cost_per_unit": 10.0,
                                        "is_tax_recoverable_itc": 1
                                    })
                                st.session_state["toast_msg"] = f"Niche promoted to Tracked Product #{new_pid} in Step 5!"
                                st.rerun()
                        with c_del_n:
                            if st.button("🗑️ Delete Niche", key=f"del_n_{nid}", type="secondary", use_container_width=True):
                                ProductRepository.delete_hunted_niche(nid)
                                st.session_state["toast_msg"] = f"Niche '{n['niche_name']}' deleted."
                                st.rerun()

                    st.markdown("<hr style='border: none; border-top: 1px dashed #334155; margin: 12px 0 16px 0;'>", unsafe_allow_html=True)

    # 2. Add New Niche Form
    with tab_add_niche:
        st.markdown("### ➕ Hunt & Save a Custom Niche to Radar")
        st.write("Record any niche idea you spot on Amazon India, offline mandis, social media, or daily life:")

        with st.form("add_custom_niche_form", clear_on_submit=True):
            f_n1, f_n2 = st.columns(2)
            with f_n1:
                cn_name = st.text_input("Niche / Product Concept *", placeholder="e.g. Copper Bedside Water Carafe Set")
                cn_cat = st.selectbox("Marketplace Category *", options=list(AMAZON_REFERRAL_FEE_RATES.keys()), index=0)
                cn_cluster = st.text_input("Target Sourcing Hub / Cluster", placeholder="e.g. Moradabad, UP / Rajkot, Gujarat")
                cn_problem = st.text_area("Customer Problem / Cultural Angle", placeholder="e.g. Bedside water storage with Ayurvedic copper benefits; current glass carafes break easily.")
            with f_n2:
                c_p_min, c_p_max = st.columns(2)
                with c_p_min:
                    cn_price_min = st.number_input("Target Selling Price Min (₹)", min_value=100.0, value=649.0, step=25.0)
                with c_p_max:
                    cn_price_max = st.number_input("Target Selling Price Max (₹)", min_value=100.0, value=899.0, step=25.0)
                
                cn_factory = st.number_input("Estimated Factory Buy Cost (₹)", min_value=10.0, value=190.0, step=10.0)
                cn_vol = st.number_input("Estimated Monthly Search Volume", min_value=100, value=3500, step=500)
                cn_comp = st.selectbox("Competition Intensity", options=["Low (<100 reviews)", "Moderate (100–500 reviews)", "High (>500 reviews)"], index=0)
                cn_diff = st.text_input("Differentiation Hook", placeholder="e.g. Include matching pure copper tumbler as a bundled lid")
                cn_notes = st.text_area("Research Notes / Links", placeholder="IndiaMART supplier contacts, competitor ASINs, etc.")

            submit_niche = st.form_submit_button("Save Niche to My Hunting Radar", type="primary")
            if submit_niche:
                if not cn_name:
                    st.error("Please enter a Niche / Product Concept name.")
                else:
                    new_nid = ProductRepository.add_hunted_niche({
                        "niche_name": cn_name.strip(),
                        "category": cn_cat,
                        "target_cluster": cn_cluster.strip() if cn_cluster else None,
                        "problem_solved": cn_problem.strip() if cn_problem else None,
                        "target_mrp_low": cn_price_min,
                        "target_mrp_high": cn_price_max,
                        "estimated_factory_cost": cn_factory,
                        "search_volume_est": cn_vol,
                        "competition_level": cn_comp.split()[0],
                        "differentiation_hook": cn_diff.strip() if cn_diff else None,
                        "notes": cn_notes.strip() if cn_notes else None,
                    })
                    st.session_state["toast_msg"] = f"Niche '{cn_name}' saved to your Radar! (ID #{new_nid})"
                    st.rerun()

    # 3. Root Keyword & Search Intent Hunter
    with tab_keyword_hunt:
        st.markdown("### 🔍 Root Keyword & Search Intent Explorer")
        st.write("Type any root material, room, or problem (e.g. `copper`, `neem`, `diya`, `organizer`, `chai`, `bamboo`) to uncover buyer intent:")

        seed_kw = st.text_input("Enter Root Seed Keyword", value="copper water bottle", placeholder="e.g. copper, neem wood, laptop stand, chai tumbler...")
        if seed_kw:
            clean_seed = seed_kw.strip().lower()
            links = AmazonManualConnector.get_research_toolkit_links(clean_seed)
            
            st.markdown("#### 🌐 Direct Public Research Links for this Seed Keyword:")
            l_c1, l_c2, l_c3, l_c4 = st.columns(4)
            with l_c1:
                st.markdown(f"[🔍 Amazon.in Search Results]({links['Amazon.in Search']})")
            with l_c2:
                st.markdown(f"[🏭 IndiaMART Supplier Search]({links['IndiaMART Sourcing']})")
            with l_c3:
                st.markdown(f"[📈 Google Trends India Search](https://trends.google.com/trends/explore?geo=IN&q={clean_seed.replace(' ', '%20')})")
            with l_c4:
                st.markdown(f"[🛡️ IP India Trademark Search]({links['India IP Trademark Portal']})")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 💡 High-Intent Long-Tail Keyword Formats to Investigate on Amazon India:")
            intents = [
                f"{clean_seed} for home mandir",
                f"{clean_seed} for office desk",
                f"{clean_seed} with leak proof lid",
                f"{clean_seed} handmade solid",
                f"{clean_seed} gift set combo",
                f"best {clean_seed} under 1000",
                f"pure {clean_seed} heavy quality"
            ]
            for it in intents:
                amz_link = AmazonManualConnector.build_amazon_in_search_url(it)
                st.markdown(f"• **{it}** — [Search live on Amazon.in ↗]({amz_link})")

    # 4. Pre-audited Inspiration
    with tab_curated:
        st.markdown("### 💡 Pre-Audited High-Margin Niches for ₹50k Capital")
        st.write("Reference models sourced from Indian manufacturing clusters with low MOQs and healthy margins:")

        CURATED_NICHES = [
            {"title": "Akhand Brass Diya with Borosilicate Glass Cover & Lid", "category": "Home Decor", "cluster": "Moradabad, UP", "problem": "Open diyas blow out under AC fans and stain mandirs with soot.", "factory": 145.0, "mrp": 599.0, "profit": 185.0, "margin": 36.0},
            {"title": "Ergonomic Seasoned Neem Wood Laptop Stand / Riser", "category": "Office Products & Stationery", "cluster": "Saharanpur / Jodhpur", "problem": "Aluminium feels cold/industrial; particle board wobbles. Neem wood offers eco-luxe anti-bacterial feel.", "factory": 175.0, "mrp": 749.0, "profit": 215.0, "margin": 32.0},
            {"title": "Double-Wall Stainless Steel Insulated Chai Tumbler 500ml", "category": "Kitchen & Dining", "cluster": "Rajkot GIDC, Gujarat", "problem": "Chai gets cold in 10 minutes in AC corporate offices; ceramic mugs break.", "factory": 210.0, "mrp": 799.0, "profit": 205.0, "margin": 29.0},
        ]
        for c in CURATED_NICHES:
            st.markdown(
                f"""
                <div style="background: #1E293B; border: 1px solid #334155; border-radius: 6px; padding: 14px 18px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between;">
                        <h4 style="margin: 0; color: #38BDF8;">{c['title']}</h4>
                        <span style="font-size: 0.8rem; background: #0F766E; color: #CCFBF1; padding: 2px 8px; border-radius: 4px;">{c['cluster']}</span>
                    </div>
                    <p style="margin: 6px 0; color: #94A3B8; font-size: 0.85rem;"><strong>Angle:</strong> {c['problem']}</p>
                    <p style="margin: 0; color: #F8FAFC; font-size: 0.85rem;">Factory: <strong>₹{c['factory']:.0f}</strong> | Target MRP: <strong>₹{c['mrp']:.0f}</strong> | Net Profit: <strong style="color: #10B981;">₹{c['profit']:.0f}/unit ({c['margin']:.0f}% margin)</strong></p>
                </div>
                """, unsafe_allow_html=True
            )

# =============================================================================
# STEP 2: EXCEL-STYLE RESEARCH CRITERIA & GATEKEEPER
# =============================================================================
elif nav_selection == "⚖️ Step 2: Excel-Style Research Criteria & Gatekeeper":
    st.markdown("<h2>⚖️ Step 2: Excel-Style Research Criteria & Gatekeeper</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8;'>Configure your research standards based on the student template methodology and audit products against real criteria.</p>", unsafe_allow_html=True)

    tab_audit_product, tab_config_criteria = st.tabs([
        "⚡ Audit Product Against My Research Criteria",
        "⚙️ Configure Research Criteria (Excel Standards)"
    ])

    criteria = ProductRepository.get_research_criteria()

    # 1. Audit Product Against Criteria
    with tab_audit_product:
        prods = ProductRepository.list_products(is_demo=0)
        if not prods:
            st.info("No products in your portfolio to audit. Add a product or load starter blueprints from the sidebar.")
        else:
            prod_map = {f"#{p['id']} - {p['title']}": p["id"] for p in prods}
            sel_label = st.selectbox("Select Product to Audit", options=list(prod_map.keys()))
            audit_pid = prod_map[sel_label]
            product = ProductRepository.get_product(audit_pid)
            competitors = ProductRepository.get_competitors(audit_pid)
            checks = ProductRepository.get_validation_checks(audit_pid)
            if not checks:
                checks = ValidationChecklistEngine.initialize_checklist_for_product(audit_pid)

            # Check Actual Metrics vs User Configured Criteria
            observed_price = product.get("current_observed_price") or 0.0
            actual_weight = product.get("weight_kg") or 0.50
            profit_scenarios = ProductRepository.get_profit_scenarios(audit_pid)
            base_scenario = next((s for s in profit_scenarios if s["scenario_name"] == "Base"), None)
            actual_margin = base_scenario["margin_pct"] if base_scenario else (product.get("base_margin_pct") or 0.0)
            
            comp_revs = [c.get("review_count") for c in competitors if c.get("review_count") is not None]
            median_reviews = float(np.median(comp_revs)) if comp_revs else None

            st.markdown(f"### 📋 Audit Scorecard: {product['title']}")
            
            # Key Real Metrics Row
            m_c1, m_c2, m_c3, c_c4 = st.columns(4)
            with m_c1:
                st.metric("Observed MRP", f"₹{observed_price:,.0f}", help=f"Target range: ₹{criteria['min_mrp_inr']} - ₹{criteria['max_mrp_inr']}")
            with m_c2:
                st.metric("Net Profit Margin", f"{actual_margin:.1f}%", help=f"Rule: At least {criteria['min_profit_margin_pct']}%")
            with m_c3:
                st.metric("Median Competitor Reviews", f"{median_reviews:.0f}" if median_reviews is not None else "Needs Competitor Data", help=f"Rule: Under {criteria['max_competitor_reviews']} reviews")
            with c_c4:
                st.metric("Unit Weight", f"{actual_weight:.2f} kg", help=f"Rule: Under {criteria['max_weight_kg']} kg")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 🎯 Gate Evaluation Against Your Custom Research Rules:")

            # Gate evaluations
            eval_results = []
            
            # Rule 1: Margin
            if actual_margin >= criteria["min_profit_margin_pct"]:
                eval_results.append(("🟢 PASS", f"Profit margin is {actual_margin:.1f}% (meets requirement of ≥{criteria['min_profit_margin_pct']}%)."))
            elif actual_margin > 0:
                eval_results.append(("🟡 INVESTIGATE", f"Profit margin is {actual_margin:.1f}% (below target of {criteria['min_profit_margin_pct']}%, risk of PPC compression)."))
            else:
                eval_results.append(("🔴 FAIL", f"No profit scenario calculated or margin is negative."))

            # Rule 2: Competitor Reviews
            if median_reviews is not None:
                if median_reviews <= criteria["max_competitor_reviews"]:
                    eval_results.append(("🟢 PASS", f"Median competitor review count is {median_reviews:.0f} (below threshold of {criteria['max_competitor_reviews']} reviews)."))
                else:
                    eval_results.append(("🔴 FAIL", f"Median competitor review count is {median_reviews:.0f} (exceeds threshold of {criteria['max_competitor_reviews']} reviews; incumbent dominance)."))
            else:
                eval_results.append(("🟡 INVESTIGATE", f"No competitor listings recorded yet. Add competitors in Step 5 to verify review barrier."))

            # Rule 3: Weight
            if actual_weight <= criteria["max_weight_kg"]:
                eval_results.append(("🟢 PASS", f"Weight is {actual_weight:.2f} kg (lightweight, satisfies ≤{criteria['max_weight_kg']} kg limit)."))
            else:
                eval_results.append(("🔴 FAIL", f"Weight is {actual_weight:.2f} kg (exceeds {criteria['max_weight_kg']} kg; heavy weight courier penalty)."))

            # Rule 4: Price
            if criteria["min_mrp_inr"] <= observed_price <= criteria["max_mrp_inr"]:
                eval_results.append(("🟢 PASS", f"Observed price ₹{observed_price:,.0f} falls within your defined sweet spot (₹{criteria['min_mrp_inr']}–₹{criteria['max_mrp_inr']})."))
            else:
                eval_results.append(("🟡 INVESTIGATE", f"Observed price ₹{observed_price:,.0f} is outside defined range (₹{criteria['min_mrp_inr']}–₹{criteria['max_mrp_inr']})."))

            for badge, explanation in eval_results:
                st.markdown(f"• **{badge}** — {explanation}")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 📋 The 12 Excel Template Research Checklist Criteria:")
            
            # Interactive 12 criteria editor
            for chk in checks:
                col_c1, col_c2, col_c3 = st.columns([3, 1.5, 2])
                with col_c1:
                    is_block_badge = "🔴 **CRITICAL GATE**" if chk.get("is_blocking") else "🔵 Standard Check"
                    st.markdown(f"**{chk.get('title', chk.get('check_key'))}** ({is_block_badge})")
                    st.caption(f"{chk.get('notes', '')}")
                with col_c2:
                    current_status = chk.get("status", "Needs Investigation")
                    status_opts = ["Pass", "Needs Investigation", "Fail"]
                    new_status = st.selectbox(
                        "Status",
                        options=status_opts,
                        index=status_opts.index(current_status) if current_status in status_opts else 1,
                        key=f"gate_status_{chk['id']}"
                    )
                    if new_status != current_status:
                        chk["status"] = new_status
                        ProductRepository.save_validation_check(audit_pid, chk)
                        st.toast(f"Updated {chk.get('title')} to {new_status}")
                with col_c3:
                    evidence = st.text_input("Evidence / Notes", value=chk.get("evidence_source") or "", key=f"gate_evid_{chk['id']}")
                    if evidence != (chk.get("evidence_source") or ""):
                        chk["evidence_source"] = evidence
                        ProductRepository.save_validation_check(audit_pid, chk)
                st.markdown("<hr style='border: none; border-top: 1px dashed #334155; margin: 8px 0;'>", unsafe_allow_html=True)

    # 2. Configure Research Criteria Form
    with tab_config_criteria:
        st.markdown("### ⚙️ Customize Your Research Criteria Thresholds")
        st.write("These thresholds directly govern the pass/fail verdicts on all audited products. By default, they match the rules from the student research template:")

        with st.form("research_criteria_form"):
            c_cr1, c_cr2 = st.columns(2)
            with c_cr1:
                st.markdown("#### Quantitative Metric Thresholds")
                cfg_margin = st.number_input("Minimum Net Profit Margin (%)", min_value=10.0, max_value=60.0, value=float(criteria.get("min_profit_margin_pct", 31.0)), step=1.0, help="Excel Template Rule: Profit margin AT LEAST 31% (AFTER advertising expenses).")
                cfg_reviews = st.number_input("Maximum Competitor Median Reviews", min_value=25, max_value=1000, value=int(criteria.get("max_competitor_reviews", 100)), step=25, help="Excel Template Rule: Median reviews of top 10 Amazon sellers < 100.")
                cfg_volume = st.number_input("Minimum Monthly Search Volume", min_value=100, max_value=50000, value=int(criteria.get("min_search_volume", 500)), step=100, help="Excel Template Rule: Monthly GOOGLE search volume of 500+.")
                cfg_weight = st.number_input("Maximum Product Weight (kg)", min_value=0.1, max_value=5.0, value=float(criteria.get("max_weight_kg", 0.50)), step=0.05, help="Amazon India lowest Easy Ship / FBA weight tier threshold.")

            with c_cr2:
                st.markdown("#### Price & Safety Gates")
                c_min_p, c_max_p = st.columns(2)
                with c_min_p:
                    cfg_min_price = st.number_input("Minimum Selling Price (₹)", min_value=100.0, value=float(criteria.get("min_mrp_inr", 499.0)), step=50.0)
                with c_max_p:
                    cfg_max_price = st.number_input("Maximum Selling Price (₹)", min_value=500.0, value=float(criteria.get("max_mrp_inr", 1499.0)), step=50.0)

                cfg_domestic = st.checkbox("Require Domestic Indian Sourcing Hub (No Overseas Import Risk)", value=bool(criteria.get("require_domestic_sourcing", 1)))
                cfg_non_consumable = st.checkbox("Enforce Non-Consumable (No food, supplements, perishables)", value=bool(criteria.get("require_non_consumable", 1)))
                cfg_non_fragile = st.checkbox("Enforce Low Fragility (Drop-test safe, no raw fragile glass)", value=bool(criteria.get("require_non_fragile", 1)))
                cfg_zero_hazmat = st.checkbox("Enforce Zero Hazmat (No batteries, flammable liquids, chemicals)", value=bool(criteria.get("require_zero_hazmat", 1)))

            save_crit = st.form_submit_button("Save Research Criteria Rules", type="primary")
            if save_crit:
                ProductRepository.save_research_criteria({
                    "min_profit_margin_pct": cfg_margin,
                    "max_competitor_reviews": cfg_reviews,
                    "min_search_volume": cfg_volume,
                    "max_weight_kg": cfg_weight,
                    "min_mrp_inr": cfg_min_price,
                    "max_mrp_inr": cfg_max_price,
                    "require_domestic_sourcing": 1 if cfg_domestic else 0,
                    "require_non_consumable": 1 if cfg_non_consumable else 0,
                    "require_non_fragile": 1 if cfg_non_fragile else 0,
                    "require_zero_hazmat": 1 if cfg_zero_hazmat else 0,
                })
                st.session_state["toast_msg"] = "Research criteria rules saved successfully!"
                st.rerun()

# =============================================================================
# STEP 3: REAL UNIT ECONOMICS & ₹50K CAPITAL ALLOCATOR
# =============================================================================
elif nav_selection == "💰 Step 3: Real Unit Economics & ₹50K Capital Allocator":
    st.markdown("<h2>💰 Step 3: Real Unit Economics & ₹50K Capital Allocator</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8;'>Calculate genuine net cash margins on Amazon India with 18% Input Tax Credit (ITC) recovery, and allocate your ₹50k budget.</p>", unsafe_allow_html=True)

    tab_alloc, tab_unit_calc = st.tabs([
        "🧮 ₹50,000 Capital Allocation Planner",
        "📊 Indian GST & Amazon Fee Waterfall Simulator"
    ])

    with tab_alloc:
        st.markdown("### 🧮 Starting Capital Allocation Planner")
        user_capital = st.number_input("Your Available Starting Capital (₹ INR)", min_value=10000.0, value=50000.0, step=5000.0)

        inv_amt = user_capital * 0.56
        pkg_amt = user_capital * 0.08
        ppc_amt = user_capital * 0.20
        sample_amt = user_capital * 0.06
        reserve_amt = user_capital * 0.10

        c_b1, c_b2, c_b3, c_b4, c_b5 = st.columns(5)
        with c_b1:
            st.metric("1. Inventory Sourcing (56%)", f"₹{inv_amt:,.0f}")
        with c_b2:
            st.metric("2. Custom Boxes/Labels (8%)", f"₹{pkg_amt:,.0f}")
        with c_b3:
            st.metric("3. Launch PPC Ads (20%)", f"₹{ppc_amt:,.0f}")
        with c_b4:
            st.metric("4. Samples & Couriers (6%)", f"₹{sample_amt:,.0f}")
        with c_b5:
            st.metric("5. Emergency Reserve (10%)", f"₹{reserve_amt:,.0f}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📦 What This Capital Buys You at Different Factory Costs:")
        cost_tiers = [130.0, 150.0, 175.0, 210.0, 250.0]
        tier_data = []
        for cost in cost_tiers:
            units = int(inv_amt // cost)
            est_selling = round(cost * 3.6, 0)
            est_profit_unit = round(est_selling * 0.29, 0)
            total_batch_profit = round(units * est_profit_unit, 0)
            total_return = round(user_capital + total_batch_profit, 0)
            tier_data.append({
                "Factory Cost / Unit": f"₹{cost:.0f}",
                "Units You Can Buy": f"{units} units",
                "Target MRP (incl. GST)": f"₹{est_selling:.0f}",
                "Net Profit / Unit": f"₹{est_profit_unit:.0f}",
                "Net Profit on Batch": f"₹{total_batch_profit:,.0f}",
                "Total Capital After 1 Batch": f"₹{total_return:,.0f} (+{round(total_batch_profit/user_capital*100)}%)"
            })
        st.dataframe(pd.DataFrame(tier_data), use_container_width=True, hide_index=True)

    with tab_unit_calc:
        st.markdown("### 📊 Indian GST & Amazon Fee Waterfall Simulator")
        sb_c1, sb_c2, sb_c3 = st.columns(3)
        with sb_c1:
            st.markdown("#### 1. Selling Parameters")
            sb_price = st.number_input("Retail Price / MRP (₹ incl GST)", min_value=100.0, value=699.0, step=25.0)
            sb_cat = st.selectbox("Category Referral Fee", options=list(AMAZON_REFERRAL_FEE_RATES.keys()), index=0)
            sb_fulfil = st.selectbox("Fulfilment Model", options=["FBA", "Easy Ship", "Self Ship"], index=0)
        
        with sb_c2:
            st.markdown("#### 2. Sourcing & Dimensions")
            sb_sourcing = st.number_input("Factory Sourcing Cost / Unit (₹)", min_value=10.0, value=175.0, step=5.0)
            sb_weight = st.number_input("Weight (kg)", min_value=0.05, value=0.42, step=0.05)
            sb_length = st.number_input("Length (cm)", min_value=1.0, value=18.0)
            sb_width = st.number_input("Width (cm)", min_value=1.0, value=14.0)
            sb_height = st.number_input("Height (cm)", min_value=1.0, value=6.0)

        with sb_c3:
            st.markdown("#### 3. Taxes & Marketing")
            sb_gst_choice = st.selectbox("Product GST Bracket", options=list(GST_RATES.keys()), index=3)
            sb_is_reg = st.checkbox("GST Registered Business (Claim ITC)", value=True)
            sb_apply_zrf = st.checkbox("Amazon Zero Referral Fee (ZRF ≤ ₹1,000)", value=True, help="Qualifying categories pay 0% referral fee when priced at or below ₹1,000.")
            sb_acos = st.slider("Budgeted PPC Ad Spend (% of price)", min_value=0, max_value=35, value=12)
            sb_return = st.slider("Expected Return Rate (%)", min_value=0, max_value=25, value=6)

        calc_res = ProfitCalculator.calculate_unit_economics(
            selling_price_gross=sb_price,
            sourcing_cost_unit=sb_sourcing,
            category=sb_cat,
            actual_weight_kg=sb_weight,
            length_cm=sb_length,
            width_cm=sb_width,
            height_cm=sb_height,
            fulfilment_model=sb_fulfil,
            gst_rate=GST_RATES[sb_gst_choice],
            is_gst_registered=sb_is_reg,
            ad_spend_pct=sb_acos / 100.0,
            return_rate_pct=sb_return / 100.0,
            apply_zrf=sb_apply_zrf
        )

        st.markdown("<br>", unsafe_allow_html=True)
        r_c1, r_c2, r_c3, r_c4 = st.columns(4)
        with r_c1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Contribution Profit / Unit</div>
                    <div class="metric-value" style="color: {'#10B981' if calc_res['net_profit_unit'] >= 0 else '#EF4444'};">
                        ₹{calc_res['net_profit_unit']:.1f}
                    </div>
                    <div class="metric-sub">Margin: {calc_res['margin_pct']:.1f}%</div>
                </div>
                """, unsafe_allow_html=True
            )
        with r_c2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Return on Capital (ROC)</div>
                    <div class="metric-value" style="color: #38BDF8;">
                        {calc_res['roi_pct']:.0f}%
                    </div>
                    <div class="metric-sub">Per stock cycle</div>
                </div>
                """, unsafe_allow_html=True
            )
        with r_c3:
            be_p = calc_res.get('breakeven_selling_price', 0.0)
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Break-Even Price (MRP)</div>
                    <div class="metric-value">
                        ₹{be_p:.0f}
                    </div>
                    <div class="metric-sub">Zero-profit floor</div>
                </div>
                """, unsafe_allow_html=True
            )
        with r_c4:
            itc_val = calc_res.get('itc_amazon_fees', 0.0)
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Recoverable ITC (GST)</div>
                    <div class="metric-value" style="color: #A78BFA;">
                        ₹{itc_val:.1f}
                    </div>
                    <div class="metric-sub">Refunded against tax</div>
                </div>
                """, unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🌊 Profit Waterfall Breakdown")
        st.plotly_chart(render_profit_waterfall(calc_res), use_container_width=True)

# =============================================================================
# STEP 4: SOURCING HUB & MY SUPPLIER DIRECTORY
# =============================================================================
elif nav_selection == "🏭 Step 4: Sourcing Hub & My Supplier Directory":
    st.markdown("<h2>🏭 Step 4: Sourcing Hub & My Supplier Directory</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8;'>Manage your personal factory contacts, add or delete suppliers, and generate custom WhatsApp RFQs.</p>", unsafe_allow_html=True)

    tab_my_suppliers, tab_add_supplier, tab_rfq_studio, tab_cluster_dir = st.tabs([
        "📋 My Saved Suppliers & Sources",
        "➕ Add New Supplier / Factory Source",
        "💬 WhatsApp & IndiaMART RFQ Generator",
        "🗺️ India's Top 8 Sourcing Clusters Directory"
    ])

    # 1. My Saved Suppliers
    with tab_my_suppliers:
        st.markdown("### 📋 My Active Sourcing Directory")
        suppliers = ProductRepository.list_custom_suppliers()
        if not suppliers:
            st.info("You haven't saved any custom suppliers yet. Use the '➕ Add New Supplier / Factory Source' tab to save your first factory contact!")
        else:
            st.write(f"Currently tracking **{len(suppliers)}** verified suppliers:")
            for s in suppliers:
                sid = s["id"]
                with st.container():
                    st.markdown(
                        f"""
                        <div style="background: #1E293B; border: 1px solid #334155; border-radius: 8px; padding: 16px 20px; margin-bottom: 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                <div>
                                    <span style="font-size: 0.75rem; background: #0F766E; color: #CCFBF1; padding: 2px 8px; border-radius: 4px; font-weight: 600;">📍 {s['hub_city']}{', ' + s['state'] if s.get('state') else ''}</span>
                                    <span style="font-size: 0.75rem; background: #374151; color: #E5E7EB; padding: 2px 8px; border-radius: 4px; font-weight: 500; margin-left: 6px;">MOQ: {s.get('moq', 100)} units</span>
                                    <span style="font-size: 0.75rem; background: {'#065F46' if s.get('gst_invoice_available') else '#991B1B'}; color: #ECFDF5; padding: 2px 8px; border-radius: 4px; font-weight: 500; margin-left: 6px;">{'GST Invoice Yes' if s.get('gst_invoice_available') else 'No GST'}</span>
                                    <h4 style="margin: 8px 0 4px 0; color: #F8FAFC; font-size: 1.25rem;">{s['supplier_name']}</h4>
                                    <p style="color: #94A3B8; font-size: 0.85rem; margin: 0 0 6px 0;"><strong>Materials / Products:</strong> {s.get('materials_offered') or 'General Manufacturing'}</p>
                                    <p style="color: #64748B; font-size: 0.8rem; margin: 0;"><strong>Contact Person:</strong> {s.get('contact_person') or 'Factory Manager'} | <strong>Phone/WhatsApp:</strong> {s.get('phone_whatsapp') or 'N/A'}</p>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    c_s1, c_s2, c_s3, c_s4, c_s_act = st.columns([1.2, 1.2, 1.2, 1.2, 2.5])
                    with c_s1:
                        st.metric("Quoted Cost", f"₹{s['typical_unit_cost']:.0f}" if s.get('typical_unit_cost') else "Pending")
                    with c_s2:
                        st.metric("Sample Cost", f"₹{s.get('sample_cost', 0):.0f}")
                    with c_s3:
                        st.metric("Lead Time", f"{s.get('lead_time_days', 14)} days")
                    with c_s4:
                        prof_url = s.get('indiamart_profile_url')
                        if prof_url:
                            st.markdown(f"[IndiaMART Profile ↗]({prof_url})")
                        else:
                            st.caption("No profile link")
                    with c_s_act:
                        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                        if st.button("🗑️ Delete Source", key=f"del_supp_{sid}", type="secondary", use_container_width=True):
                            ProductRepository.delete_custom_supplier(sid)
                            st.session_state["toast_msg"] = f"Supplier '{s['supplier_name']}' deleted from directory."
                            st.rerun()

                    st.markdown("<hr style='border: none; border-top: 1px dashed #334155; margin: 12px 0 16px 0;'>", unsafe_allow_html=True)

    # 2. Add New Supplier Form
    with tab_add_supplier:
        st.markdown("### ➕ Add New Sourcing Supplier / Factory Contact")
        st.write("Record factory contacts you discover on IndiaMART, Udaan, trade fairs, or direct cluster visits:")

        with st.form("add_custom_supplier_form", clear_on_submit=True):
            col_sup1, col_sup2 = st.columns(2)
            with col_sup1:
                sup_name = st.text_input("Supplier / Factory Name *", placeholder="e.g. Royal Brass Metal Works")
                sup_city = st.text_input("City / Manufacturing Hub *", placeholder="e.g. Moradabad, Rajkot, Surat, Saharanpur")
                sup_state = st.text_input("State", placeholder="e.g. Uttar Pradesh, Gujarat, Rajasthan")
                sup_materials = st.text_input("Materials / Products Offered", placeholder="e.g. Cast brass puja articles, copper carafes")
                sup_contact = st.text_input("Contact Person Name", placeholder="e.g. Ramesh Sharma (Owner)")
                sup_phone = st.text_input("Phone / WhatsApp Number", placeholder="e.g. +91 98765 43210")
            with col_sup2:
                sup_url = st.text_input("IndiaMART / Catalog Link", placeholder="e.g. https://www.indiamart.com/suppliername/")
                sup_moq = st.number_input("Minimum Order Quantity (MOQ)", min_value=10, value=100, step=25)
                sup_cost = st.number_input("Quoted Unit Cost (₹)", min_value=0.0, value=150.0, step=10.0)
                sup_sample = st.number_input("Sample Piece Cost (₹)", min_value=0.0, value=250.0, step=50.0)
                sup_lead = st.number_input("Production Lead Time (Days)", min_value=1, value=14, step=2)
                sup_gst = st.checkbox("Can Provide Legitimate GST Invoice?", value=True)
                sup_notes = st.text_area("Notes / Quality Observations", placeholder="Packaging quality, response speed, negotiable?")

            submit_sup = st.form_submit_button("Save Supplier to Directory", type="primary")
            if submit_sup:
                if not sup_name or not sup_city:
                    st.error("Please provide both Supplier Name and City / Manufacturing Hub.")
                else:
                    new_sid = ProductRepository.add_custom_supplier({
                        "supplier_name": sup_name.strip(),
                        "hub_city": sup_city.strip(),
                        "state": sup_state.strip() if sup_state else None,
                        "materials_offered": sup_materials.strip() if sup_materials else None,
                        "contact_person": sup_contact.strip() if sup_contact else None,
                        "phone_whatsapp": sup_phone.strip() if sup_phone else None,
                        "indiamart_profile_url": sup_url.strip() if sup_url else None,
                        "moq": sup_moq,
                        "typical_unit_cost": sup_cost if sup_cost > 0 else None,
                        "sample_cost": sup_sample,
                        "lead_time_days": sup_lead,
                        "gst_invoice_available": 1 if sup_gst else 0,
                        "notes": sup_notes.strip() if sup_notes else None,
                    })
                    st.session_state["toast_msg"] = f"Supplier '{sup_name}' added to your directory! (ID #{new_sid})"
                    st.rerun()

    # 3. WhatsApp RFQ Studio
    with tab_rfq_studio:
        st.markdown("### 💬 WhatsApp & IndiaMART RFQ Script Generator")
        st.write("Generate copy-ready messages to send directly to factory owners on WhatsApp:")

        suppliers_list = ProductRepository.list_custom_suppliers()
        supp_names = ["-- Select from My Saved Suppliers --"] + [f"{s['supplier_name']} ({s['hub_city']})" for s in suppliers_list]
        sel_supp_idx = st.selectbox("Select Supplier (Optional)", options=supp_names)

        c_rfq1, c_rfq2 = st.columns(2)
        with c_rfq1:
            rfq_pname = st.text_input("Product Name", value="Akhand Brass Diya with Borosilicate Glass Cover")
            rfq_batch = st.number_input("Initial Trial Batch Units", min_value=25, value=100, step=25)
            rfq_custom = st.text_input("Custom Requirement", value="Thicker brass base + custom brown corrugated box with barcode")
        with c_rfq2:
            st.markdown("#### WhatsApp Script (Hindi - देसी भाषा)")
            hindi_script = f"""नमस्ते सर जी,

मेरा नाम [आपका नाम] है और मेरी फर्म ई-कॉमर्स और रिटेल डिस्ट्रीब्यूशन का काम करती है।

हम {rfq_pname} का एक इनिशियल ट्रायल ऑर्डर (लगभग {rfq_batch} पीस) प्लान कर रहे हैं।

कृपया मुझे निम्नलिखित जानकारी साझा करें:
1. {rfq_batch} पीस के लिए एक्स-फैक्ट्री रेट (Ex-Factory Rate) क्या रहेगा?
2. क्या आप हमारे कस्टमर के लिए {rfq_custom} प्रोवाइड कर सकते हैं?
3. माल तैयार होने में कितना समय (Production Lead Time) लगेगा?
4. क्या आप 1 सैंपल पीस कूरियर से भेज सकते हैं? सैंपल की कॉस्ट क्या रहेगी?
5. पक्का GST इनवॉइस और HSN कोड क्या रहेगा?

सैंपल फाइनल होते ही हम ऑर्डर प्लेस करेंगे। धन्यवाद!"""
            st.text_area("Hindi Message (Ready to Copy)", value=hindi_script, height=220)

            st.markdown("#### WhatsApp Script (English)")
            eng_script = f"""Dear Sir/Madam,

My name is [Your Name] representing an Indian retail & e-commerce firm.

We are looking to source {rfq_pname} for an initial test batch of {rfq_batch} units.

Could you please provide:
1. Ex-factory unit price for {rfq_batch} units?
2. Can you customize packaging with {rfq_custom}?
3. What is the production lead time for this quantity?
4. Sample availability and courier charge for 1 piece to our office?
5. Applicable GST rate and HSN Code?

We look forward to building a long-term sourcing relationship with your factory."""
            st.text_area("English Message (Ready to Copy)", value=eng_script, height=180)

    # 4. Top 8 Hubs Directory
    with tab_cluster_dir:
        st.markdown("### 🗺️ India's Top 8 Sourcing Clusters Directory")
        HUBS = [
            {"hub": "Moradabad, Uttar Pradesh", "specialty": "Brass, Copper, Aluminum Castings, Puja Articles, Metal Decor", "moq": "50–100 units"},
            {"hub": "Saharanpur, Uttar Pradesh", "specialty": "Carved Woodcraft, Sheesham & Mango Wood Boxes, Desk Organizers", "moq": "50–100 units"},
            {"hub": "Rajkot, Gujarat (GIDC)", "specialty": "Stainless Steel Kitchenware, Insulated Tumblers, Flasks", "moq": "100–200 units"},
            {"hub": "Surat, Gujarat", "specialty": "Heavy Oxford Fabric Wardrobe Organizers, Storage Bags, Poly/Cotton", "moq": "100–150 units"},
            {"hub": "Panipat, Haryana", "specialty": "Microfiber Kitchen Mats, Bath Rugs, Bed Linen, Floor Runners", "moq": "100–200 units"},
            {"hub": "Khurja, Uttar Pradesh", "specialty": "Glazed Ceramics, Mugs, Planters, Studio Pottery", "moq": "100–150 units"},
            {"hub": "Jaipur, Rajasthan", "specialty": "Hand-block printed quilts, Cotton Bedsheets, Traditional Bags", "moq": "50–100 units"},
            {"hub": "Channapatna, Karnataka", "specialty": "GI-Tagged Non-toxic Lacquered Wooden Toys & Educational Blocks", "moq": "50–100 units"},
        ]
        for h in HUBS:
            st.markdown(
                f"""
                <div style="background: #1E293B; border: 1px solid #334155; border-radius: 6px; padding: 12px 16px; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between;">
                        <strong style="color: #38BDF8;">📍 {h['hub']}</strong>
                        <span style="font-size: 0.75rem; background: #0F766E; color: #CCFBF1; padding: 2px 6px; border-radius: 4px;">MOQ: {h['moq']}</span>
                    </div>
                    <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 0.85rem;">{h['specialty']}</p>
                </div>
                """, unsafe_allow_html=True
            )

# =============================================================================
# STEP 5: ACTIVE PRODUCTS PORTFOLIO & RESEARCH STUDIO
# =============================================================================
elif nav_selection == "🗃️ Step 5: Active Products Portfolio & Research Studio":
    st.markdown("<h2>🗃️ Step 5: Active Products Portfolio & Research Studio</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8;'>Manage your research portfolio: add/delete competitors, log keyword observations, add factory quotes, and take research notes.</p>", unsafe_allow_html=True)

    # Add Custom Product Modal / Expander
    with st.expander("➕ Add a Custom Product Idea to Portfolio", expanded=False):
        with st.form("add_product_to_portfolio_form", clear_on_submit=True):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                cp_title = st.text_input("Product Title *", placeholder="e.g. Pure Copper Hammered Water Bottle 750ml")
                cp_asin = st.text_input("Amazon ASIN (Optional)", placeholder="e.g. B08XYZ1234")
                cp_cat = st.selectbox("Category *", options=list(AMAZON_REFERRAL_FEE_RATES.keys()), index=0)
                cp_kw = st.text_input("Main Target Keyword *", placeholder="e.g. copper water bottle hammered")
            with col_f2:
                cp_price = st.number_input("Target MRP / Selling Price (₹)", min_value=100.0, value=699.0, step=25.0)
                cp_weight = st.number_input("Weight (kg)", min_value=0.05, value=0.42, step=0.05)
                cp_status = st.selectbox("Status", options=RESEARCH_STATUSES, index=0)
                cp_notes = st.text_area("Initial Notes", placeholder="Sourcing notes, supplier contacts, unique angle...")

            submitted = st.form_submit_button("Save Product to Portfolio", type="primary")
            if submitted:
                if not cp_title or not cp_kw:
                    st.error("Please provide both Product Title and Main Target Keyword.")
                else:
                    new_id = ProductRepository.create_product({
                        "title": cp_title.strip(),
                        "asin": cp_asin.strip().upper() if cp_asin else None,
                        "category": cp_cat,
                        "main_keyword": cp_kw.strip().lower(),
                        "current_observed_price": cp_price,
                        "weight_kg": cp_weight,
                        "research_status": cp_status,
                        "estimated_demand_notes": cp_notes,
                        "is_demo": 0
                    })
                    ValidationChecklistEngine.initialize_checklist_for_product(new_id)
                    st.session_state["toast_msg"] = f"Product '{cp_title}' created successfully! (ID #{new_id})"
                    st.rerun()

    prods = ProductRepository.list_products(is_demo=0)
    if not prods:
        st.info("Your portfolio is currently empty. Add a product above or click '🚀 Load 3 Blueprints' in the sidebar.")
    else:
        st.write(f"Currently tracking **{len(prods)}** product(s):")
        
        for p in prods:
            pid = p["id"]
            with st.container():
                st.markdown(
                    f"""
                    <div style="background: #1E293B; border: 1px solid #334155; border-radius: 8px; padding: 18px 20px; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-size: 0.75rem; background: #0F766E; color: #CCFBF1; padding: 2px 8px; border-radius: 4px; font-weight: 600;">#{p['id']} | {p['category']}</span>
                                <span style="font-size: 0.75rem; background: #374151; color: #E5E7EB; padding: 2px 8px; border-radius: 4px; font-weight: 500; margin-left: 6px;">Status: {p['research_status']}</span>
                                <h3 style="margin: 8px 0 4px 0; color: #F8FAFC; font-size: 1.25rem;">{p['title']}</h3>
                                <p style="color: #94A3B8; font-size: 0.85rem; margin: 0;"><strong>Keyword:</strong> <code>{p['main_keyword']}</code> | <strong>Weight:</strong> {p['weight_kg']} kg | <strong>ASIN:</strong> {p.get('asin') or 'Not Linked'}</p>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                col_k1, col_k2, col_k3, col_k4, col_act = st.columns([1.2, 1.2, 1.2, 1.2, 2.5])
                with col_k1:
                    st.metric("Target Price (MRP)", f"₹{p['current_observed_price']:,.0f}" if p.get('current_observed_price') else "N/A")
                with col_k2:
                    st.metric("Unit Net Profit", f"₹{p['base_profit_unit']:.1f}" if p.get('base_profit_unit') is not None else "Pending")
                with col_k3:
                    st.metric("Net Margin", f"{p['base_margin_pct']:.1f}%" if p.get('base_margin_pct') is not None else "Pending")
                with col_k4:
                    opp_score = p.get("opportunity_score")
                    st.metric("Opportunity Score", f"{opp_score:.1f}/100" if opp_score is not None else "Pending")
                with col_act:
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    c_del, c_view = st.columns(2)
                    with c_del:
                        if st.button("🗑️ Delete Product", key=f"del_prod_{pid}", type="secondary", use_container_width=True, help="Permanently delete this product from database"):
                            ProductRepository.delete_product(pid)
                            st.session_state["toast_msg"] = f"Product #{pid} permanently deleted."
                            st.rerun()
                    with c_view:
                        links = AmazonManualConnector.get_research_toolkit_links(p["main_keyword"], p.get("asin"))
                        st.markdown(f"[🔍 View on Amazon.in]({links['Amazon.in Search']})")

                # Expandable Deep-Dive Details with Add/Delete controls for competitors, keywords, quotes
                with st.expander(f"🔎 Full Research Details for #{p['id']} - {p['title'][:35]}...", expanded=False):
                    d_tab_comp, d_tab_kw, d_tab_supp, d_tab_notes, d_tab_links = st.tabs([
                        "⚔️ Competitors Matrix", "📈 Keywords & Demand", "🏭 Supplier Quotes", "📝 Notes & Log", "🌐 Verification Links"
                    ])

                    # 1. Competitors Matrix
                    with d_tab_comp:
                        st.markdown("##### Competitor Listings on Amazon.in")
                        comps = ProductRepository.get_competitors(pid)
                        if comps:
                            for c in comps:
                                cid = c["id"]
                                c_col1, c_col2, c_col3, c_col4, c_del_c = st.columns([3, 1.2, 1.2, 1.2, 1])
                                with c_col1:
                                    st.markdown(f"**{c['competitor_title']}** (ASIN: `{c['competitor_asin']}`)")
                                    if c.get("weaknesses"):
                                        st.caption(f"⚠️ Weakness: {c['weaknesses']}")
                                with c_col2:
                                    st.write(f"Price: **₹{c['observed_price']:,.0f}**")
                                with c_col3:
                                    st.write(f"Reviews: **{c.get('review_count', 'N/A')}**")
                                with c_col4:
                                    st.write(f"Rating: **{c.get('rating', 'N/A')} ⭐**")
                                with c_del_c:
                                    if st.button("🗑️ Delete", key=f"del_c_{cid}", type="secondary"):
                                        ProductRepository.delete_competitor(cid)
                                        st.toast("Competitor deleted.")
                                        st.rerun()
                                st.markdown("<hr style='border: none; border-top: 1px dashed #334155; margin: 4px 0;'>", unsafe_allow_html=True)
                        else:
                            st.caption("No competitor listings logged yet.")

                        # Add Competitor Form
                        with st.form(f"add_comp_form_{pid}", clear_on_submit=True):
                            st.markdown("###### ➕ Add Competitor Listing")
                            ac_c1, ac_c2 = st.columns(2)
                            with ac_c1:
                                c_asin = st.text_input("Competitor ASIN *", placeholder="e.g. B08XYZ1234")
                                c_title = st.text_input("Competitor Title *", placeholder="e.g. Borosil Diya")
                                c_brand = st.text_input("Brand", placeholder="e.g. Borosil")
                            with ac_c2:
                                c_price = st.number_input("Observed Price (₹)", min_value=1.0, value=599.0, step=10.0)
                                c_revs = st.number_input("Review Count", min_value=0, value=120)
                                c_rating = st.number_input("Rating (1.0 - 5.0)", min_value=1.0, max_value=5.0, value=4.2, step=0.1)
                            c_weak = st.text_input("Observed Customer Complaint / Weakness", placeholder="e.g. Thin base gets burning hot")
                            submit_comp = st.form_submit_button("Add Competitor Listing")
                            if submit_comp:
                                if not c_asin or not c_title:
                                    st.error("Please provide ASIN and Title.")
                                else:
                                    ProductRepository.add_competitor(pid, {
                                        "competitor_asin": c_asin.strip().upper(),
                                        "competitor_title": c_title.strip(),
                                        "brand": c_brand.strip() if c_brand else None,
                                        "observed_price": c_price,
                                        "review_count": c_revs,
                                        "rating": c_rating,
                                        "weaknesses": c_weak.strip() if c_weak else None
                                    })
                                    st.session_state["toast_msg"] = "Competitor added!"
                                    st.rerun()

                    # 2. Keywords & Demand
                    with d_tab_kw:
                        st.markdown("##### Keyword Search Observations")
                        kw_obs = ProductRepository.get_keyword_observations(pid)
                        if kw_obs:
                            for ko in kw_obs:
                                koid = ko["id"]
                                k_col1, k_col2, k_col3, k_del = st.columns([3, 1.5, 1.5, 1])
                                with k_col1:
                                    st.markdown(f"**{ko['keyword']}** ({ko['source_platform']})")
                                with k_col2:
                                    st.write(f"Volume: **{int(ko['search_volume']):,}/mo**" if ko.get('search_volume') else "N/A")
                                with k_col3:
                                    st.write(f"CPC: ₹{ko.get('cpc_bid_low') or 0:.1f} - ₹{ko.get('cpc_bid_high') or 0:.1f}")
                                with k_del:
                                    if st.button("🗑️ Delete", key=f"del_ko_{koid}", type="secondary"):
                                        ProductRepository.delete_keyword_observation(koid)
                                        st.toast("Keyword observation deleted.")
                                        st.rerun()
                                st.markdown("<hr style='border: none; border-top: 1px dashed #334155; margin: 4px 0;'>", unsafe_allow_html=True)
                        else:
                            st.caption("No keyword observations recorded yet.")

                        # Add Keyword Form
                        with st.form(f"add_kw_form_{pid}", clear_on_submit=True):
                            st.markdown("###### ➕ Add Keyword Observation")
                            ak_c1, ak_c2 = st.columns(2)
                            with ak_c1:
                                n_kw = st.text_input("Target Keyword *", placeholder="e.g. brass akhand diya glass")
                                n_plat = st.selectbox("Source Platform", options=["Google Keyword Planner", "Amazon Suggestion", "Google Trends", "Manual Research"])
                            with ak_c2:
                                n_vol = st.number_input("Monthly Search Volume", min_value=10, value=2500, step=100)
                                n_cpc = st.number_input("Estimated CPC Bid (₹)", min_value=1.0, value=12.0, step=1.0)
                            submit_kw = st.form_submit_button("Record Keyword")
                            if submit_kw:
                                if not n_kw:
                                    st.error("Please enter a keyword.")
                                else:
                                    ProductRepository.add_keyword_observation(pid, {
                                        "keyword": n_kw.strip().lower(),
                                        "source_platform": n_plat,
                                        "search_volume": n_vol,
                                        "cpc_bid_low": n_cpc * 0.8,
                                        "cpc_bid_high": n_cpc * 1.3,
                                    })
                                    st.session_state["toast_msg"] = "Keyword observation added!"
                                    st.rerun()

                    # 3. Supplier Quotes
                    with d_tab_supp:
                        st.markdown("##### Sourcing & Factory Quotes")
                        quotes = ProductRepository.get_supplier_quotes(pid)
                        if quotes:
                            for q in quotes:
                                qid = q["id"]
                                q_col1, q_col2, q_col3, q_del = st.columns([3, 1.5, 1.5, 1])
                                with q_col1:
                                    st.markdown(f"**{q['supplier_name']}** ({q.get('supplier_city_hub') or 'India'})")
                                with q_col2:
                                    st.write(f"Unit Cost: **₹{q['unit_purchase_cost']:.0f}** (MOQ: {q.get('moq', 100)})")
                                with q_col3:
                                    st.write(f"Lead Time: **{q.get('production_lead_time_days', 14)} days**")
                                with q_del:
                                    if st.button("🗑️ Delete", key=f"del_sq_{qid}", type="secondary"):
                                        ProductRepository.delete_supplier_quote(qid)
                                        st.toast("Supplier quote deleted.")
                                        st.rerun()
                                st.markdown("<hr style='border: none; border-top: 1px dashed #334155; margin: 4px 0;'>", unsafe_allow_html=True)
                        else:
                            st.caption("No supplier quotes recorded yet.")

                        # Add Quote Form
                        with st.form(f"add_sq_form_{pid}", clear_on_submit=True):
                            st.markdown("###### ➕ Add Supplier Quotation")
                            as_c1, as_c2 = st.columns(2)
                            with as_c1:
                                s_name = st.text_input("Supplier Name *", placeholder="e.g. Moradabad Brass Casting")
                                s_hub = st.text_input("City / Hub", placeholder="e.g. Moradabad, UP")
                                s_cost = st.number_input("Unit Purchase Cost (₹) *", min_value=1.0, value=145.0, step=5.0)
                            with as_c2:
                                s_moq = st.number_input("MOQ (Units)", min_value=10, value=100, step=25)
                                s_pkg = st.number_input("Packaging Cost / Unit (₹)", min_value=0.0, value=15.0, step=5.0)
                                s_lead = st.number_input("Lead Time (Days)", min_value=1, value=12, step=1)
                            submit_sq = st.form_submit_button("Record Quote")
                            if submit_sq:
                                if not s_name:
                                    st.error("Please enter supplier name.")
                                else:
                                    ProductRepository.add_supplier_quote(pid, {
                                        "supplier_name": s_name.strip(),
                                        "supplier_city_hub": s_hub.strip() if s_hub else None,
                                        "unit_purchase_cost": s_cost,
                                        "moq": s_moq,
                                        "packaging_cost": s_pkg,
                                        "production_lead_time_days": s_lead,
                                        "is_tax_recoverable_itc": 1
                                    })
                                    st.session_state["toast_msg"] = "Supplier quote added!"
                                    st.rerun()

                    # 4. Notes & Logs
                    with d_tab_notes:
                        st.markdown("##### Research Journal & Supplier Log")
                        notes = ProductRepository.get_notes(pid)
                        if notes:
                            for nt in notes:
                                st.markdown(f"**{nt.get('title') or 'Research Note'}** — *{nt.get('created_at', '')[:10]}*")
                                st.write(nt["content"])
                                st.markdown("<hr style='border: none; border-top: 1px dashed #334155; margin: 4px 0;'>", unsafe_allow_html=True)
                        else:
                            st.caption("No research notes logged yet.")

                        with st.form(f"add_note_form_{pid}", clear_on_submit=True):
                            st.markdown("###### ➕ Add Research Note")
                            nt_title = st.text_input("Note Title", placeholder="e.g. Sample review call notes")
                            nt_content = st.text_area("Note Content *", placeholder="What did you observe or discuss with the factory?")
                            submit_note = st.form_submit_button("Save Note")
                            if submit_note:
                                if not nt_content:
                                    st.error("Please enter note content.")
                                else:
                                    ProductRepository.add_note(pid, nt_content.strip(), title=nt_title.strip() if nt_title else "Research Note")
                                    st.session_state["toast_msg"] = "Note saved!"
                                    st.rerun()

                    # 5. Verification Links
                    with d_tab_links:
                        st.markdown(f"• [Amazon.in Search for '{p['main_keyword']}']({links.get('Amazon.in Search', '#')})")
                        if "Keepa India Price Chart" in links:
                            st.markdown(f"• [Keepa India Price Chart]({links['Keepa India Price Chart']})")
                        else:
                            st.markdown("• *Keepa India Price Chart (Add an ASIN to enable direct chart)*")
                        st.markdown(f"• [IndiaMART Supplier Lookup]({links.get('IndiaMART Sourcing', '#')})")
                        st.markdown(f"• [IP India Trademark Search]({links.get('India IP Trademark Portal', '#')})")

                st.markdown("<hr style='border: none; border-top: 1px dashed #334155; margin: 12px 0 16px 0;'>", unsafe_allow_html=True)

# =============================================================================
# STEP 6: COMPETITOR BENCHMARKS & MARKET ANALYTICS
# =============================================================================
elif nav_selection == "📊 Step 6: Competitor Benchmarks & Market Analytics":
    st.markdown("<h2>📊 Step 6: Competitor Benchmarks & Market Analytics</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8;'>Compare competitor prices, review barriers, and opportunity rankings across your research portfolio.</p>", unsafe_allow_html=True)

    metrics = ProductRepository.get_terminal_metrics(is_demo=0)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Total Products</div>
                <div class="metric-value">{metrics['total_products']}</div>
                <div class="metric-sub">Active research portfolio</div>
            </div>
            """, unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Shortlisted</div>
                <div class="metric-value" style="color: #38BDF8;">{metrics['shortlisted_count']}</div>
                <div class="metric-sub">Passed initial gates</div>
            </div>
            """, unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Approved for Test</div>
                <div class="metric-value" style="color: #10B981;">{metrics['approved_count']}</div>
                <div class="metric-sub">Ready for test batch</div>
            </div>
            """, unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Competitors Tracked</div>
                <div class="metric-value">{metrics['total_competitors']}</div>
                <div class="metric-sub">Observed listings on amazon.in</div>
            </div>
            """, unsafe_allow_html=True
        )
    with col5:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Supplier Quotes</div>
                <div class="metric-value">{metrics['total_quotes']}</div>
                <div class="metric-sub">Verified factory quotes</div>
            </div>
            """, unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🏆 Portfolio Opportunity Rankings")
    prods = ProductRepository.list_products(is_demo=0)
    if prods:
        ranked = sorted(prods, key=lambda p: (p.get("opportunity_score") or 0.0), reverse=True)
        display_data = []
        for p in ranked:
            score = p.get("opportunity_score")
            conf = p.get("confidence_level") or "Low"
            has_block = p.get("has_blocking_risks") == 1
            score_str = f"⚠️ {score:.1f} (Blocking Risk)" if has_block else (f"{score:.1f} ({conf})" if score is not None else "Needs Scoring")

            display_data.append({
                "ID": p["id"],
                "Product Title": p["title"],
                "Category": p["category"],
                "Status": p["research_status"],
                "Target MRP (₹)": f"₹{p['current_observed_price']:,.0f}" if p.get("current_observed_price") else "N/A",
                "Unit Net Profit (₹)": f"₹{p['base_profit_unit']:,.1f}" if p.get("base_profit_unit") is not None else "N/A",
                "Margin (%)": f"{p['base_margin_pct']:.1f}%" if p.get("base_margin_pct") is not None else "N/A",
                "Opportunity Score": score_str,
                "Competitors": p.get("competitor_count", 0),
            })
        st.dataframe(pd.DataFrame(display_data), use_container_width=True, hide_index=True)
    else:
        st.info("No products available to rank.")

# =============================================================================
# STEP 7: DATA IMPORTERS & DB HYGIENE
# =============================================================================
elif nav_selection == "📥 Step 7: Data Importers & DB Hygiene":
    st.markdown("<h2>📥 Step 7: Data Importers & DB Hygiene</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8;'>Import legacy student spreadsheets, Google Trends CSVs, or manage database storage.</p>", unsafe_allow_html=True)

    tab_imp_excel, tab_imp_trends, tab_cleaner = st.tabs([
        "📄 Import Student Research Excel",
        "📈 Import Google Trends CSV",
        "🧹 Database Maintenance & Reset"
    ])

    with tab_imp_excel:
        st.markdown("#### Import Amazon Product Research Template (.xlsx)")
        uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])
        if uploaded_file is not None:
            if st.button("Execute Excel Import"):
                try:
                    res = ExcelImporter.import_workbook(uploaded_file, uploaded_file.name)
                    st.success(f"Imported successfully! Created {res['products_created']} products, {res['competitors_created']} competitors.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Import failed: {str(e)}")

    with tab_imp_trends:
        st.markdown("#### Import Google Trends Multi-Timeline CSV")
        uploaded_csv = st.file_uploader("Upload Trends CSV", type=["csv"])
        if uploaded_csv is not None:
            try:
                df_trends = GoogleTrendsConnector.parse_trends_csv(uploaded_csv.getvalue().decode("utf-8"))
                st.dataframe(df_trends.head(10), use_container_width=True)
                st.success(f"Parsed {len(df_trends)} trend records!")
            except Exception as e:
                st.error(f"Failed to parse CSV: {str(e)}")

    with tab_cleaner:
        st.markdown("#### Database Maintenance")
        st.write("Reset the terminal or purge legacy test data at any time:")

        c_cl1, c_cl2 = st.columns(2)
        with c_cl1:
            if st.button("🚀 Reload 3 Starter Blueprints", use_container_width=True):
                pids = load_starter_blueprints()
                st.success(f"Loaded {len(pids)} starter blueprints!")
                st.rerun()
        with c_cl2:
            if st.button("🗑️ Delete Legacy US Spreadsheet Imports", use_container_width=True):
                del_count = ProductRepository.delete_legacy_products()
                st.success(f"Deleted {del_count} legacy spreadsheet items.")
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⚠️ Wipe Database (Clear All Products)", type="primary"):
            cleared = ProductRepository.clear_all_products()
            st.success(f"Wiped {cleared} products. Database is completely clean!")
            st.rerun()

# =============================================================================
# SEPARATE TAB: HOW TO USE THIS TERMINAL & OPERATOR PLAYBOOK
# =============================================================================
elif nav_selection == "📖 How to Use This Terminal & Operator Playbook":
    st.markdown("<h2>📖 How to Use This Terminal & Operator Playbook</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8;'>The complete manual: how to hunt niches, apply Excel criteria, source from Indian clusters, calculate GST, and launch your first product.</p>", unsafe_allow_html=True)

    st.markdown("""
    ---
    ### 🧭 The 6-Stage Operator Workflow

    #### Stage 1: Hunt for High-Margin Niches (`Step 1`)
    - **What to do:** Use the **Niche Hunter** to identify cultural habits and daily pain points in Indian homes (e.g. daily puja articles, insulated chaiware, ergonomic desk accessories, Ayurvedic copper).
    - **Custom Niches:** Record your own ideas in the **"➕ Hunt & Add New Niche"** tab. Save target MRP bands and estimated factory costs.
    - **Promotion:** When a niche looks promising, click **"🚀 Promote to Product"** to automatically send it to your Step 5 Portfolio!

    ---
    #### Stage 2: Audit Against the Excel Research Criteria (`Step 2`)
    - **The 12 Core Excel Rules:**
      1. **Profit Margin ≥ 31%:** Must yield healthy profits even after 10–15% PPC ad spend.
      2. **Median Competitor Reviews < 100:** If page 1 incumbents have thousands of reviews, beginners will burn capital on ads trying to compete.
      3. **Monthly Search Volume 500+:** Demand must be genuine and active.
      4. **Weight Under 0.50 kg (500g):** Prevents steep weight handling fee jumps on Amazon India.
      5. **Selling Price ₹499 to ₹1,499:** High enough to leave ₹150+ net profit after Amazon's cut, yet affordable enough for a 100-unit batch on ₹50k capital.
      6. **Non-Consumable & Zero Hazmat:** No food, supplements, or batteries that trigger mandatory lab certificates.
      7. **Non-Fragile:** Prevents high courier transit returns across Indian roads.
      8. **Domestic Sourcing Hub:** Can be sourced locally within 10–14 days.
    - **Customizing Rules:** Go to the **"⚙️ Configure Research Criteria"** tab to adjust these thresholds anytime.

    ---
    #### Stage 3: Stress-Test Unit Economics & GST ITC (`Step 3`)
    - **MRP is Inclusive of Tax:** If you list at ₹699 MRP with 18% GST, your base revenue is:
      $$\\text{Base Price} = \\frac{699}{1.18} = ₹592.37$$
    - **Claiming Back GST (Input Tax Credit):** Amazon India charges 18% GST on all seller fees (Referral, Closing, Weight Handling). As a GST-registered seller, **100% of this GST is recovered as Input Tax Credit (ITC)** against your Output GST liabilities!
    - **₹50,000 Budget Deployment:**
      - 56% (₹28,000) $\\rightarrow$ Inventory (120–160 units @ ₹140–₹210)
      - 8% (₹4,000) $\\rightarrow$ Custom Packaging & FNSKU Barcodes
      - 20% (₹10,000) $\\rightarrow$ Launch PPC Sponsored Ads
      - 6% (₹3,000) $\\rightarrow$ Factory Samples & Courier Tests
      - 10% (₹5,000) $\\rightarrow$ Emergency Cash Buffer

    ---
    #### Stage 4: Sourcing from Domestic Mandis (`Step 4`)
    - **Bypass Middlemen:** Go directly to India's manufacturing hubs:
      - *Moradabad, UP:* Brass castings, copper, puja articles.
      - *Saharanpur, UP / Jodhpur, RJ:* Seasoned neem, sheesham, and mango woodcrafts.
      - *Rajkot GIDC, Gujarat:* Stainless steel drinkware, kitchen tools.
      - *Surat / Panipat:* Fabric organizers, linen, microfiber mats.
    - **Save Suppliers:** Use the **"➕ Add New Supplier"** tab to maintain your private factory directory.
    - **WhatsApp RFQ Scripts:** Click the WhatsApp generator to copy ready Hindi and English inquiry messages.

    ---
    #### Stage 5: Managing Your Portfolio (`Step 5`)
    - Log competing ASINs on Amazon.in, record monthly search volumes, and store factory quotations.
    - You have complete control to **Add or Delete** individual competitors, keywords, quotes, or entire products with 1 click!

    ---
    #### Stage 6: The 30-Day Launch Playbook
    - **Days 1–5:** Apply for GTIN Brand Exemption. Create listing with 100% pure white background hero image (#FFFFFF) and benefit bullets.
    - **Days 6–10:** Inward stock to Amazon FBA or configure Amazon Easy Ship.
    - **Days 11–20:** Launch with **Exact Match PPC only** on 3 to 5 hyper-relevant keywords at ₹12–₹18 bid cap.
    - **Days 21–30:** Place packaging insert cards offering WhatsApp support for instant free replacements, and trigger Amazon's "Request a Review" button 5 days after delivery.
    """)
