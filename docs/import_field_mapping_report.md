# Excel Import Field-Mapping & Data Normalization Report

**Application:** Amazon India Product Research & Opportunity Intelligence Terminal  
**Stage:** Stage 1 Discovery & Data Architecture  
**Analyzed Files:**
1. `OLD Product Research Spreadsheet (_File_ -_ _Make A Copy_).xlsx`
2. `🔎 NEW Student Amazon Product Research Template (_File_ -_ _Make A Copy_).xlsx`

---

## 1. Executive Summary of Analyzed Workbooks

Both workbooks were thoroughly inspected down to cell-level formulas, values, and formatting. They are student research templates designed for general e-commerce analysis (predominantly US Amazon with Etsy comparisons in USD).

To serve Amazon India (`amazon.in`) without corrupting INR currency or local fee realities:
1. **Currency Isolation:** All imports from these templates are strictly flagged with `marketplace = 'AMAZON_US_LEGACY'` and `currency = 'USD'`. They can be imported as reference ideas, but are prevented from being mistakenly treated as Amazon India domestic observations.
2. **Formula Decomposition:** Excel formulas (e.g. `=MEDIAN(...)`, `=0.15*B3`, `=(24000+...)/5`) are parsed to capture both the raw formula expression and its evaluated numerical result.
3. **Multi-Channel Data:** Fields related to Etsy (`#1 SELLING ETSY LINK`, `ETSY REVENUE`) are stored in `product_observations` or notes rather than primary Amazon metrics.

---

## 2. Workbook 1: `OLD Product Research Spreadsheet`

### Sheet 1: `🔎 1. Product Spreadsheet`

| Original Excel Column | Data Type in Excel | Formula / Example | Unified Terminal Target Table & Column | Mapping Transformation / Business Rule |
|---|---|---|---|---|
| `PRODUCT IDEA` | Text | `"wine stopper"`, `"boho wallet"` | `products.title` & `products.main_keyword` | Trimmed, standardized to title case. Serves as product identifier. |
| `GOOGLE SEARCH VOLUME` | Number | `3600.0` | `keyword_observations.search_volume` | Source marked as `'Google Search (US Legacy Template)'`, type `'estimated'`. |
| `#1 AMAZON SELLER` | URL | `https://www.amazon.com/dp/B005N0WCE4?psc=1` | `competitors.product_url`, `competitors.asin` | URL regex extracts ASIN (`B005N0WCE4`). Stored as top competitor for product. |
| `MEDIAN AMAZON REVIEWS` | Formula | `=MEDIAN(5771,143,3224,...)` (Val: 2700.5) | `competitors` (multiple records) + `products.median_reviews` | Raw values inside formula can be parsed as individual competitor review counts! Formula string stored in audit log. |
| `AMAZON REVENUE (MONTHLY)` | Number | `59320.0` | `product_observations.monthly_revenue_est` | Tagged as USD reference estimate; flagged with legacy note. |
| `AMAZON SEARCH VOLUME` | Number | `41101.0` | `keyword_observations.search_volume` | Source marked as `'Amazon Keyword (Legacy Tool)'`. |
| `#1 SELLING ETSY LINK` | URL | `https://www.etsy.com/...` | `research_notes` / `product_observations` | Stored as secondary external market observation. |
| `ETSY REVENUE (TOTAL)` | Number | `12130.0` | `research_notes` / `product_observations` | Multi-channel cross-reference only. |
| `TRADEMARK SEARCH` | Dropdown | `PASS` / `FAIL` | `validation_checks` (`check_key='trademark'`) | Mapped to `PASS`, `FAIL`, or `NEEDS_INVESTIGATION`. |
| `PATENT SEARCH` | Dropdown | `PASS` / `FAIL` | `validation_checks` (`check_key='patent'`) | Mapped to `PASS`, `FAIL`, or `NEEDS_INVESTIGATION`. |
| `PROFIT MARGIN (%)` | Blank/Number | Blank in row 3 | `profit_scenarios.margin_pct` | Populated if present, else calculated via Indian calculator. |
| `NOTES` | Text | User notes | `research_notes.content` | Appended with import timestamp and workbook origin. |

### Sheet 2: `💰 2.  Product Margin`

| Original Cell / Label | Formula / Value | Unified Calculator Mapping | Note for Amazon India |
|---|---|---|---|
| `B3` (Price) | `34.95` | `profit_scenarios.selling_price` | In legacy template this is USD. In India terminal, selling price is in INR (₹) inclusive of GST. |
| `B5` (Production Costs) | `4.5` | `sourcing_costs.unit_purchase_cost` | Sourcing cost. |
| `B6` (Packaging Costs) | `1.0` | `sourcing_costs.packaging_cost` | Packaging per unit. |
| `B7` (Shipping Fees) | `2.0` | `sourcing_costs.shipping_cost` | Inward transport / freight. |
| `B8` (Amazon Referral Fee) | `=0.15*B3` (15%) | `calculators.referral_fee` | Amazon India referral fee varies from 3% to 18% depending on category + 18% GST. |
| `B9` (Amazon Fulfilment Fee)| `6.0` | `calculators.weight_handling_fee` | Amazon India uses standard weight handling tiers (Local/Regional/National) + Pick & Pack. |
| `B10` (Amazon Storage Fees)| `0.05` | `calculators.storage_fee` | Monthly storage allocation per unit. |
| `B11` (Marketing & Ads) | `5.25` | `calculators.advertising_spend` | Budgeted customer acquisition / PPC cost per unit. |
| `B12` (Additional Fees) | `0.0` | `calculators.other_expenses` | Miscellaneous expenses (e.g., closing fee). |
| `B14` (Profit) | `=B3-SUM(B5:B12)` | `profit_scenarios.net_profit` | Terminal calculates exact net profit with GST input tax recovery. |
| `B15` (Margin) | `=B14/B3` | `profit_scenarios.margin_pct` | Profit margin %. |
| `B16` (ROI) | `=B14/(B5+B6+B7)` | `profit_scenarios.roi_pct` | Return on inventory investment. |

### Sheet 3: `✅ 3. Product Checklist`

Contains 12 criteria (default `False`). The terminal integrates every single one into its **13-Point Indian Validation Checklist**, adding mandatory Indian product compliance (BIS/FSSAI/EPR):
1. Does NOT infringe on any copyright.
2. Does NOT infringe on any patents.
3. Does NOT infringe on any trademarks.
4. Does NOT require a special restricted license to sell.
5. Monthly search volume threshold met (500+).
6. Is NOT consumable (shelf life / perishability risk).
7. Is NOT a temporary fad/trend.
8. Is NOT dangerous / HAZMAT.
9. Median reviews of top 10 sellers < 100 (low barrier to entry).
10. NOT easily breakable (low transit breakage).
11. Profit margin at least 31% (after advertising).
12. Year-round non-seasonal demand.
13. *Indian Regulatory Compliance (Added)*: Legal Metrology (MRP, Packer, Origin) + BIS/FSSAI/EPR.

---

## 3. Workbook 2: `🔎 NEW Student Amazon Product Research Template`

### Sheet 1: `🔎 Product Research Template`

This sheet splits research into **Specific Product (Long-Tail)** and **Product Type (Short-Tail)**:

| Original Excel Column | Sample Data | Unified Terminal Target | Transformation & Logic |
|---|---|---|---|
| `Long-Tail Keyword` | `twin milestone blanket` | `product_keywords.keyword` (`is_primary=1`) | Main targeted high-intent long-tail search phrase. |
| `Amazon Keyword Volume` | `485.0` | `keyword_observations.search_volume` | Long-tail search volume (source tagged). |
| `Google Keyword Volume` | `390.0` | `keyword_observations.search_volume` | Google Ads search volume for long tail. |
| `#1 AMZ Monthly Revenue` | `13000.0` | `competitors.monthly_revenue_est` | Revenue of top competitor. |
| `Etsy Revenue` | `400.0` | `research_notes` | Cross-platform demand indicator. |
| `Amazon Page 1 Products` | `16.0` | `products.page1_product_count` | Measure of keyword search results saturation. |
| `Short-Tail Keyword` | `milestone blanket` | `product_keywords.keyword` (`is_primary=0`) | Parent product category keyword. |
| `Amazon Keyword Volume` (Short) | `3634.0` | `keyword_observations.search_volume` | High-level volume for category. |
| `Google Keyword Volume` (Short) | `5400.0` | `keyword_observations.search_volume` | High-level Google volume. |
| `Avg Top 5 Monthly Amazon Rev`| `=(24000+21000+19000+16000+15000)/5` | `product_observations.top5_avg_revenue` | Parsed formula values: provides 5 competitor revenue points! |
| `Top Etsy Revenue` | `3000.0` | `research_notes` | Secondary reference. |

---

## 4. Duplicate Detection & Data Integrity Rules

1. **Title / ASIN Uniqueness:** If an imported row matches an existing product by ASIN (or by exact title within the same marketplace), it is treated as an update to observation history rather than creating a duplicate product record.
2. **Preservation of Raw Inputs:** All original raw spreadsheet values and formulas are preserved verbatim in an `import_history` and `raw_payload` JSON field for complete reproducibility.
3. **Status Assignment:** Newly imported rows receive `research_status = 'Researching'` or `'New Idea'`.
4. **Zero vs Null Distinction:** Empty cells are stored as `NULL`, never silently coerced to `0`, preventing skewing of mathematical medians and opportunity scores.
