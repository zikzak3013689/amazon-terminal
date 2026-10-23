# Known Limitations & Compliance Disclaimers

**Application:** Amazon India Product Research & Opportunity Intelligence Terminal  
**Marketplace:** Amazon India (`amazon.in`) | **Currency:** INR (₹)  
**Status:** Version 1.0 Baseline

---

## 1. Data Attribution & Transparency Constraints

### A. No Synthetic Sales Fabrication
Unlike black-box software that claims to reveal exact sales figures by running hidden linear regressions on BSR, this terminal **never fabricates unit sales**. If verified sales data is not provided by the seller or observed through authorized reporting, the terminal explicitly flags the metric as "Missing Data" and lowers the score confidence level accordingly.

### B. Google Trends vs. Amazon Search Demand
- Google Trends values represent **relative search interest (0–100 index)** on Google Search in India.
- A high Google Trends score indicates strong cultural awareness or external traffic, but does not guarantee buyer intent on Amazon.in.
- Trends comparisons are only valid when multiple keywords are exported together in the same query session.

### C. Google Keyword Planner vs. Amazon Buyer Search
- Keyword volumes from Google Ads represent searchers looking for information or shopping on Google across India.
- Amazon buyer search volumes follow different shopper search behavior. Google keyword data must always be corroborated with Amazon.in BSR and competitor review velocity.

### D. Review Count vs. Sales Volume Reality
Review counts reflect historical accumulated customer feedback. Review conversion rates in India typically range from **0.5% to 2.5%** depending on category. Review counts must never be treated as a direct multiplier for monthly sales.

---

## 2. API Integrations & Subscription Cost Boundaries

### A. Keepa API (Phase 1 Decoupled Mode)
- Access to the programmatic Keepa REST API requires a paid commercial subscription (EUR 19–49/mo).
- To preserve the **₹0 software subscription fee guarantee**, Phase 1 operates in a high-efficiency **Manual Keepa Observation Mode**:
  - Direct 1-click deep links open the Keepa India price and BSR history graph (`https://keepa.com/#!product/10-[ASIN]`).
  - Fields are provided to log 30/90/180-day Buy Box averages and BSR drops.
  - The API connector is cleanly modularized and will activate seamlessly once a user supplies an authorized API key in `.env`.

### B. Prohibited Scraping & Access Control Bypass
- The terminal strictly avoids automated headless browser scraping of `amazon.in` or rotating proxy circumvention.
- This protects users against Amazon IP blocks, legal cease-and-desist notices, and broken DOM scraping scripts.

---

## 3. Regulatory & Legal Disclaimers

1. **Intellectual Property (Trademarks & Patents):**
   - The checklist provides direct links to the official Indian Intellectual Property Office portal (`ipindiaonline.gov.in`).
   - The terminal's "Pass" status reflects the user's manual preliminary search; it does not constitute a legal non-infringement opinion or replace registered Indian Patent/Trademark Attorney clearance.

2. **GST & Taxation:**
   - Calculations use the standard Indian GST formula and Amazon India seller fee schedules.
   - Actual tax liabilities may vary based on seller state jurisdiction (CGST+SGST vs IGST), turnover thresholds, composition scheme eligibility, or TCS/TDS withholdings (Section 52 CGST Act). Consult a qualified Chartered Accountant (CA).

3. **Product Certifications:**
   - Categories requiring mandatory Bureau of Indian Standards (BIS) ISI mark, FSSAI licensing (food/dietary), CDSCO registration (cosmetics), or EPR plastic packaging registration must be verified directly with respective regulatory authorities prior to inventory import.
