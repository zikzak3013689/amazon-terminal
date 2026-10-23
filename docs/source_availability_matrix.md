# Data Source Availability & Integration Matrix
**Application:** Amazon India Product Research & Opportunity Intelligence Terminal  
**Market:** Amazon India (`amazon.in`) | **Currency:** INR (₹)  
**Document Status:** Production Baseline (Stage 1 Discovery)

---

## 1. Overview of Data Sources

To maintain a zero-cost initial budget, adhere strictly to Amazon India's Terms of Service, and avoid fabricated numbers, the terminal utilizes a **dual-mode architecture** (Demo Mode vs. Real Research Mode) with transparent classification of every data point as:
- **Observed:** Directly seen on a live listing, BSR page, or supplier quote.
- **Estimated:** Third-party estimation from authorized tools or public models.
- **Calculated:** Derived strictly using deterministic mathematical/tax formulas.
- **Assumed:** User-specified assumptions (e.g., target ad spend, return rate).

---

## 2. Source Availability Matrix

| Source | Target Marketplace | Access Method | Cost | Current Availability | Integration Status | Data Reliability / Notes |
|---|---|---|---|---|---|---|
| **Amazon India Live Pages** (`amazon.in`) | Amazon.in | Manual Entry + Clean URL Parser + Public Deep Links | ₹0 | **Available** | **Active (Module B - Connector 1)** | 100% legal & compliant. Zero scraping, zero CAPTCHA risks. Deep links provided for Best Sellers, Movers & Shakers, New Releases. |
| **Google Trends** | India (`geo=IN`) | CSV Import (Exported from Google Trends web) | ₹0 | **Available** | **Active (Module B - Connector 2)** | Relative search interest (0–100), not absolute sales volume. Preserves keyword, date range, seasonality index. |
| **Google Keyword Planner** | India (`country=IN`) | CSV Import (Exported from Google Ads) | ₹0 | **Available** | **Active (Module B - Connector 3)** | Google search volume & bid ranges. Explicitly tagged as *Google Search Demand*, never confused with Amazon buyer search. |
| **Keepa Price & BSR History** | Amazon.in | Manual Observation / Modular API Adapter | ₹0 (Manual) / Paid API | **Manual Available; API Disabled** | **Modular Adapter Ready (Connector 4)** | Manual fields for Buy Box, Amazon price, BSR drops. API adapter is securely decoupled and remains off until valid key supplied. |
| **Domestic Suppliers (India)** | India (Moradabad, Surat, Khurja, Tirupur, etc.) | Structured Quote Input (IndiaMART/Direct) | ₹0 | **Available** | **Active (Module B - Connector 5)** | Domestic landed cost, GST Input Tax Credit (ITC), MOQ, packaging, freight. |
| **Overseas Suppliers** | China, Vietnam, etc. (Alibaba, Global Sources) | Structured Quote Input | ₹0 | **Available** | **Active (Module B - Connector 5)** | FOB price, ocean/air freight, BCD, SWS, IGST, clearing & forwarding charges. |
| **Historical Student Spreadsheet (OLD)** | US/Global reference | openpyxl / pandas Workbook Importer | ₹0 | **Available in Workspace** | **Active (Importer Engine)** | Extracted from `OLD Product Research Spreadsheet...xlsx`. Formulas converted; currency tagged as USD reference. |
| **New Student Template (NEW)** | US/Global reference | openpyxl / pandas Workbook Importer | ₹0 | **Available in Workspace** | **Active (Importer Engine)** | Extracted from `🔎 NEW Student Amazon Product Research Template...xlsx`. Long-tail vs short-tail keyword mapping. |

---

## 3. Compliance and Ethical Constraints

1. **No Bot Scraping:** The terminal does not run headless browsers to scrape Amazon behind Cloudflare/WAF, nor use rotating proxies. This prevents IP blocks, legal issues, and broken DOM failures.
2. **No Fabricated Demand:** The terminal does not generate synthetic sales estimates. If a product lacks verified sales data, the system warns the user of missing evidence.
3. **Transparent Assumptions:** Every profit calculation displays exact fee schedules, tax credits, and user inputs with step-by-step audit trails.
