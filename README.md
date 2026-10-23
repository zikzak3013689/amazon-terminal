# Amazon India Product Research & Opportunity Intelligence Terminal

A complete, functional, beginner-friendly marketplace intelligence terminal designed specifically for discovering, evaluating, comparing, and validating products to sell on **Amazon India (`amazon.in`)**.

Built for non-technical users and professional sellers on Windows.

---

## 🌟 Key Highlights & Philosophy

- **Market Focus:** Amazon India (`amazon.in`) exclusively, calibrated in Indian Rupees (**₹ INR**).
- **Initial Software Budget:** **₹0 Subscription Fees**. No mandatory paid SaaS APIs (e.g. Helium 10, Jungle Scout).
- **Zero Fabricated Numbers:** Strict adherence to reality. Sales, keyword volumes, competitor data, and supplier quotes are either directly observed, imported from authorized files, or calculated using deterministic formulas. Missing data is never silently invented.
- **True Indian GST Unit Economics:** Distinguishes **Output GST liability** from **Input Tax Credit (ITC)** on domestic sourcing and Amazon seller fees, eliminating false margins and double-taxation.
- **Dual-Mode Architecture:** Seamlessly toggle between **Demo Mode** (10 pre-loaded demonstration products with complete metrics) and **Real Research Mode** (clean workspace with zero synthetic mock data).
- **Legal & Compliant:** Zero headless scraping, zero proxy rotation, zero CAPTCHA walls. Built entirely on verified manual entry, spreadsheet imports, and legal public verification links.

---

## 🚀 Quick Launch (Windows)

### Method 1: One-Click Launcher (No Coding Required)
1. Double-click **`run_terminal.bat`** in the project folder.
2. The terminal will verify dependencies and launch in your default browser at `http://localhost:8501`.

### Method 2: Command Line (PowerShell / CMD)
```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
python -m streamlit run app.py
```

---

## 🧭 Terminal Modules

### 1. 📊 Executive Terminal Dashboard
- Pipeline health metrics: Active Research Ideas, Shortlisted Candidates, Awaiting Data, Tested/Approved.
- Status distribution pie chart and category breakdown.
- Ranked Top Opportunities with confidence ratings (High / Medium / Low) and blocking risk warnings.

### 2. 🔍 Product Explorer & Shortlist
- Searchable product database with category, status, and keyword filters.
- Quick product idea creator.
- One-click export of filtered research portfolios to **CSV** and **Excel**.

### 3. 🔎 Product Detail Deep-Dive
- Comprehensive product profile with dimensions, actual vs. volumetric weight, and target pricing.
- 1-Click direct research links: Amazon.in Search, Amazon Best Sellers, Movers & Shakers, Hot New Releases, Keepa Web Price Graph, IndiaMART supplier search, and the official Indian Intellectual Property Trademark portal.
- 6 Interactive Tabs:
  1. **⚔️ Competitors Matrix:** Track up to 10+ competing ASINs, median price, price range, review concentration %, and weakness mining.
  2. **📈 Keywords & Demand:** Keyword observations from Google Trends and Google Ads Keyword Planner.
  3. **💰 Profit & GST Economics:** Conservative, Base, and Optimistic scenario cards, interactive Profit Waterfall Chart, break-even selling price, and break-even ACoS.
  4. **✅ 13-Point Checklist:** Audit Demand, Competition, Profitability, Logistics, Fragility, IP, and mandatory Indian regulatory compliance (BIS/Legal Metrology/FSSAI/EPR).
  5. **🏭 Supplier Quotations:** Log factory quotations from Indian industrial clusters (Moradabad, Surat, Rajkot, etc.) and overseas suppliers.
  6. **📝 Research Notes & Audit Log:** Chronological notes with timestamps.

### 4. 🧮 Profitability & GST Calculator Sandbox
- Interactive unit economics sandbox.
- Real-time calculations for:
  - Base selling price (excl. output GST)
  - Category referral fees and price-band closing fees
  - Weight handling tiers (FBA Standard, Easy Ship, Self Ship across Local/Regional/National zones)
  - Recoverable GST Input Tax Credit (ITC)
  - Contribution profit, margin %, and inventory ROI %
  - Break-even selling price and break-even advertising cost of sale (ACoS %)

### 5. ⚔️ Competitor Benchmark Studio
- Statistical price dispersion analysis (standard deviation & bubble chart).
- Review concentration analysis showing social proof barriers.
- Competitor differentiation checklist (review mining, transit packaging, accessory bundles, bilingual user guides).

### 6. 🏭 Sourcing & Supplier Studio
- Directory of major Indian industrial manufacturing clusters and specializations (Moradabad for Brass, Surat for Microfiber/Textiles, Rajkot for Metal/Kitchenware, Channapatna for Wooden Toys, etc.).
- Overseas Import Customs Duty Simulator: Calculates CIF Assessable Value, Basic Customs Duty (BCD), Social Welfare Surcharge (SWS), and Integrated GST (IGST).

### 7. 📥 Data Importers & Connectors
- Automated importer for the provided student research spreadsheets:
  - `OLD Product Research Spreadsheet (_File_ -_ _Make A Copy_).xlsx`
  - `🔎 NEW Student Amazon Product Research Template (_File_ -_ _Make A Copy_).xlsx`
- Generic Excel workbook importer.
- CSV importers for Google Trends (India geocode) and Google Ads Keyword Planner.
- Modular Keepa API adapter interface (disabled by default in Phase 1 for ₹0 cost, ready for API keys).

### 8. ⚖️ Opportunity Scoring Settings
- 100-point transparent scoring engine based on 6 core factors:
  - Demand Evidence (25%)
  - Competition Opportunity (20%)
  - Profitability (25%)
  - Market Stability (10%)
  - Differentiation Feasibility (10%)
  - Sourcing Feasibility (10%)
- Interactive weight sliders to tailor scoring to your business strategy.

---

## 🏗️ Technical Architecture & Project Structure

```
d:\Python\Amazon\
│
├── app.py                      # Main Streamlit application entrypoint
├── requirements.txt            # Python dependencies
├── run_terminal.bat            # One-click Windows launcher
├── .env.example                # Environment variables template
├── conftest.py                 # Pytest configuration
│
├── config/
│   └── settings.py             # App constants, fee schedules, tax rates, scoring weights
│
├── database/
│   ├── schema.sql              # Normalized SQLite schema (13 tables, indexes, constraints)
│   ├── connection.py           # Thread-safe database connection & migration runner
│   └── repository.py           # Clean data access layer (CRUD, queries, metrics)
│
├── calculators/
│   └── profit_calculator.py    # Indian unit economics, GST ITC recovery, fee tiers, scenarios
│
├── modules/
│   ├── validation_checklist.py # 13-point validation checklist and blocker gate detector
│   └── competitor_analyzer.py  # Competitor price dispersion and review concentration
│
├── scoring/
│   └── opportunity_scorer.py   # 100-point transparent scoring engine with confidence grading
│
├── connectors/
│   ├── amazon_manual.py        # Clean URL parser, ASIN extractor, legal deep links
│   ├── google_trends.py        # Google Trends India CSV parser & seasonality engine
│   ├── google_keyword_planner.py# Google Ads Keyword Planner CSV parser & bid metrics
│   ├── keepa_adapter.py        # Keepa manual price tracker & decoupled API adapter
│   ├── supplier_connector.py   # Domestic Indian clusters & import duty calculator
│   └── excel_importer.py       # Importer for student spreadsheets & generic workbooks
│
├── ui/
│   ├── theme.py                # Financial terminal CSS styling & status badges
│   └── charts.py               # Plotly interactive charts (waterfall, scatter, bar, trends)
│
├── sample_data/
│   ├── demo_products.py        # 10 pre-loaded Amazon India private label demo products
│   ├── sample_google_trends_india.csv          # Sample Google Trends India export
│   └── sample_google_keyword_planner_india.csv # Sample Google Keyword Planner India export
│
├── tests/
│   ├── test_database.py        # Database CRUD, filters, and duplicate tests
│   ├── test_profit_calculator.py# Unit economics, GST treatment, fee schedules, scenarios
│   ├── test_validation_and_scoring.py # Checklist blocker gates, scoring engine
│   └── test_importers.py       # Excel and CSV importer tests
│
└── docs/
    ├── source_availability_matrix.md     # Detailed data source integration matrix
    ├── import_field_mapping_report.md    # Spreadsheet cell-level mapping document
    ├── financial_calculation_methodology.md # Mathematical unit economics formulas
    ├── windows_installation_guide.md     # Windows setup & 10-product beginner test guide
    ├── known_limitations.md              # Boundary conditions & legal compliance notices
    └── feature_checklist.md              # 100% master specification verification matrix
```

---

## 🧪 Automated Testing

Run the test suite with:
```powershell
python -m pytest -v
```
All **16 automated test suites** pass with 100% code correctness and deterministic mathematical formulas.

---

## 📄 License & Compliance

Built for educational, research, and independent private label business planning on Amazon India. Does not use unauthorized scrapers, reverse-engineered APIs, or intellectual property infringements.
