"""
Plotly Chart Generators for the Amazon India Research Terminal.
Delivers clear visual distinction between Real Observations, User Assumptions, and Calculated Estimates.
"""

from typing import Dict, Any, List
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def apply_dark_theme(fig: go.Figure, **kwargs) -> go.Figure:
    """Safely applies dark terminal styling without argument collisions."""
    base_layout = dict(
        paper_bgcolor="rgba(15, 23, 42, 0.0)",
        plot_bgcolor="rgba(30, 41, 59, 0.5)",
        font=dict(color="#94A3B8", family="Inter, sans-serif"),
        margin=dict(l=40, r=40, t=40, b=40),
    )
    base_layout.update(kwargs)
    fig.update_layout(**base_layout)
    fig.update_xaxes(gridcolor="#334155", zerolinecolor="#475569")
    fig.update_yaxes(gridcolor="#334155", zerolinecolor="#475569")
    return fig

def render_profit_waterfall(profit_data: Dict[str, Any]) -> go.Figure:
    """
    Renders an Indian Unit Economics Waterfall Chart from MRP down to Net Contribution Profit.
    """
    selling_price = profit_data.get("selling_price_gross", 0)
    output_gst = profit_data.get("output_gst_liability", 0)
    sourcing_cost = profit_data.get("sourcing_cost_unit", 0)
    referral_fee = profit_data.get("referral_fee", 0)
    closing_fee = profit_data.get("closing_fee", 0)
    shipping_fee = profit_data.get("weight_handling_fee", 0) + profit_data.get("pick_pack_fee", 0) + profit_data.get("storage_fee", 0)
    ad_spend = profit_data.get("ad_spend_unit", 0)
    returns = profit_data.get("return_cost_unit", 0)
    net_profit = profit_data.get("net_profit_unit", 0)

    x_labels = [
        "Retail Price (MRP)",
        "Output GST",
        "Landed Sourcing",
        "Referral Fee",
        "Closing Fee",
        "FBA / Shipping",
        "PPC Ad Spend",
        "Returns Loss",
        "Net Profit"
    ]

    measures = ["absolute", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "total"]
    y_values = [
        selling_price,
        -output_gst,
        -sourcing_cost,
        -referral_fee,
        -closing_fee,
        -shipping_fee,
        -ad_spend,
        -returns,
        net_profit
    ]

    text_values = [f"₹{abs(v):.1f}" for v in y_values]

    fig = go.Figure(go.Waterfall(
        name="Unit Economics",
        orientation="v",
        measure=measures,
        x=x_labels,
        textposition="outside",
        text=text_values,
        y=y_values,
        connector={"line": {"color": "#64748B"}},
        decreasing={"marker": {"color": "#EF4444"}},
        increasing={"marker": {"color": "#10B981"}},
        totals={"marker": {"color": "#38BDF8" if net_profit >= 0 else "#EF4444"}}
    ))

    apply_dark_theme(
        fig,
        title=f"Unit Economics Breakdown (Selling Price: ₹{selling_price:.0f} | Net Profit: ₹{net_profit:.1f})",
        waterfallgap=0.25
    )
    return fig

def render_competitor_price_distribution(competitors: List[Dict[str, Any]], target_price: float = None) -> go.Figure:
    """Renders competitor price scatter chart with target product benchmark line."""
    fig = go.Figure()
    if not competitors:
        apply_dark_theme(fig, title="No competitor data available")
        return fig

    titles = [c.get("competitor_title", c.get("competitor_asin", "Comp"))[:25] for c in competitors]
    prices = [c.get("observed_price", 0) for c in competitors]
    ratings = [c.get("rating", 4.0) or 4.0 for c in competitors]
    reviews = [c.get("review_count", 10) or 10 for c in competitors]

    fig.add_trace(go.Scatter(
        x=titles,
        y=prices,
        mode="markers+text",
        marker=dict(
            size=[min(max(r / 20.0, 14), 45) for r in reviews],
            color=ratings,
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(title="Rating ⭐", thickness=15)
        ),
        text=[f"₹{p:.0f}" for p in prices],
        textposition="top center",
        hovertext=[f"{t}<br>Price: ₹{p:.0f}<br>Reviews: {r}<br>Rating: {rat}⭐" for t, p, r, rat in zip(titles, prices, reviews, ratings)],
        hoverinfo="text",
        name="Competitors"
    ))

    if target_price:
        fig.add_hline(
            y=target_price,
            line_dash="dash",
            line_color="#F59E0B",
            annotation_text=f"Your Target Price (₹{target_price:.0f})",
            annotation_position="bottom right"
        )

    apply_dark_theme(
        fig,
        title="Competitor Observed Prices (Bubble size = Review volume)",
        yaxis_title="Observed Price (INR ₹)"
    )
    return fig

def render_competitor_review_concentration(competitors: List[Dict[str, Any]]) -> go.Figure:
    """Renders review count comparison across top competing listings."""
    fig = go.Figure()
    if not competitors:
        apply_dark_theme(fig, title="No competitor data")
        return fig

    sorted_comps = sorted(competitors, key=lambda c: (c.get("review_count") or 0), reverse=True)
    labels = [c.get("competitor_title", c.get("competitor_asin", "ASIN"))[:22] for c in sorted_comps]
    reviews = [(c.get("review_count") or 0) for c in sorted_comps]

    fig.add_trace(go.Bar(
        x=labels,
        y=reviews,
        marker_color="#38BDF8",
        text=[f"{r:,}" for r in reviews],
        textposition="auto"
    ))

    apply_dark_theme(
        fig,
        title="Social Proof Distribution (Competitor Review Counts)",
        yaxis_title="Total Review Count"
    )
    return fig

def render_google_trends_chart(trends_result: Dict[str, Any]) -> go.Figure:
    """Renders Google Trends Interest-Over-Time line chart."""
    fig = go.Figure()
    df = trends_result.get("dataframe")
    if df is None or df.empty:
        apply_dark_theme(fig, title="No Trends data")
        return fig

    keywords = trends_result.get("keywords", [])
    for kw in keywords:
        fig.add_trace(go.Scatter(
            x=df["date"],
            y=df[kw],
            mode="lines",
            name=kw,
            line=dict(width=2.5)
        ))

    apply_dark_theme(
        fig,
        title=f"Google Trends Search Interest in India ({trends_result.get('timeframe', 'Past Year')})",
        yaxis_title="Relative Search Interest (0 - 100 Index)",
        xaxis_title="Date",
        hovermode="x unified"
    )
    return fig

def render_opportunity_score_bar(breakdown: Dict[str, Any], total_score: float) -> go.Figure:
    """Renders a horizontal breakdown bar chart for the 6 opportunity scoring factors."""
    factor_labels = [
        "Demand Evidence",
        "Competition Opp.",
        "Profitability",
        "Market Stability",
        "Differentiation",
        "Sourcing Feasibility"
    ]
    factor_keys = [
        "demand_evidence",
        "competition_opportunity",
        "profitability",
        "market_stability",
        "differentiation",
        "sourcing_feasibility"
    ]

    scores = [breakdown.get(k, {}).get("score", 0) for k in factor_keys]
    weights = [breakdown.get(k, {}).get("weight", 0) for k in factor_keys]

    fig = go.Figure(go.Bar(
        y=factor_labels,
        x=scores,
        orientation="h",
        marker=dict(
            color=scores,
            colorscale=[[0, "#EF4444"], [0.5, "#F59E0B"], [1.0, "#10B981"]],
            showscale=False
        ),
        text=[f"{s:.0f}/100 (Weight: {w:.0f}%)" for s, w in zip(scores, weights)],
        textposition="inside",
        insidetextanchor="middle"
    ))

    apply_dark_theme(
        fig,
        title=f"Opportunity Score Breakdown (Overall: {total_score:.1f} / 100)",
        xaxis=dict(range=[0, 100], title="Factor Score (0-100)")
    )
    return fig
