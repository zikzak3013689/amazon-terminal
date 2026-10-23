# Amazon India Financial Calculation Methodology & Unit Economics

**Application:** Amazon India Product Research & Opportunity Intelligence Terminal  
**Market:** Amazon India (`amazon.in`) | **Currency:** Indian Rupee (₹, INR)  
**Document Status:** Production Financial Specification

---

## 1. Indian E-Commerce Tax Architecture (GST)

On Amazon India, consumer retail prices are legally presented as **MRP (Maximum Retail Price - inclusive of all taxes)**. When evaluating unit economics, treating GST incorrectly leads to either double-taxing or underestimating margins.

### The Two GST Realities

The terminal provides an explicit toggle for the seller's GST regime:

#### Model A: Regular GST Registered Seller (Standard & Recommended)
- **Output GST Liability:** Collected from the customer as part of the listing price and owed to the Indian Government.
  $$\text{Selling Price (Excl. GST)} = \frac{\text{Selling Price (Incl. GST)}}{1 + \text{GST Rate}}$$
  $$\text{Output GST} = \text{Selling Price (Incl. GST)} - \text{Selling Price (Excl. GST)}$$
- **Input Tax Credit (ITC):**
  - **Sourcing ITC:** GST paid on domestic raw materials / finished goods invoice is recoverable against Output GST liability.
  - **Amazon Fee ITC:** Amazon India levies 18% GST on all seller service fees (Referral, Closing, Shipping, Pick & Pack, Storage, Advertising). A registered seller claims 100% of this 18% GST as ITC.
- **Net GST Payable to Govt:**
  $$\text{Net GST Payable} = \max(0, \text{Output GST} - (\text{Sourcing GST ITC} + \text{Amazon Fees GST ITC}))$$
- **Net Contribution Profit:**
  $$\text{Contribution Profit} = \text{Selling Price (Excl. GST)} - \text{Landed Cost (Excl. GST)} - \text{Total Amazon Fees (Excl. GST)} - \text{Ad Spend (Excl. GST)} - \text{Return Allowance}$$

#### Model B: Unregistered / Non-ITC Small Seller
- GST paid on inventory and Amazon fees cannot be reclaimed and acts as a direct sunk cost.

---

## 2. Landed Cost Calculation

### Domestic Sourcing (e.g., IndiaMART / Direct Factory)
$$\text{Landed Cost per Unit} = \text{Base Purchase Cost} + \text{Domestic Inward Freight} + \text{Packaging} + \text{Quality Inspection} + \text{Defect Allowance} + \text{Unrecoverable GST (if non-ITC)}$$

### Overseas Import Sourcing (e.g., China / Vietnam)
1. **Assessable Value (CIF):** Unit Purchase (FOB) + International Freight + Insurance.
2. **Basic Customs Duty (BCD):** Typically 10%–20% on Assessable Value depending on HSN code.
3. **Social Welfare Surcharge (SWS):** 10% on BCD.
4. **Integrated GST (IGST):** Typically 18% on $(\text{Assessable Value} + \text{BCD} + \text{SWS})$. *Eligible as ITC for registered importers with IEC & GSTIN.*
5. **Clearing, Forwarding & Port Logistics:** Allocated per unit.

---

## 3. Amazon India Marketplace Fee Schedules

Amazon India charges distinct fee components:

### A. Referral Fee (% of Selling Price)
Varies by category (e.g., 5% for Computers, 9% for Home & Kitchen, 13% for Apparel, 15% for Jewelry/Bags). Subject to category-specific minimum fees (typically ₹3–₹5).

### B. Closing Fee (Tiered by Price Band)
Amazon India applies closing fees based on fulfilment method and price slabs. For standard FBA:
- ₹0 to ₹250: ₹5
- ₹251 to ₹500: ₹9
- ₹501 to ₹1,000: ₹30
- Above ₹1,000: ₹61  
*(Adjustable in config for Easy Ship and Self Ship).*

### C. Fulfilment & Weight Handling Fee
Based on actual weight vs. volumetric weight $(\frac{L \times W \times H}{5000} \text{ in cm})$, whichever is greater:
- **Easy Ship / FBA Standard (per 500g slab):**
  - Local: ₹35–₹45 for first 500g + ₹15/additional 500g
  - Regional: ₹45–₹55 for first 500g + ₹25/additional 500g
  - National: ₹65–₹80 for first 500g + ₹35/additional 500g

### D. Pick & Pack Fee (FBA only)
Flat ₹14 to ₹20 per standard unit.

### E. Monthly Storage Fee (FBA only)
Calculated based on cubic feet $(\text{length} \times \text{width} \times \text{height} / 28316.8 \text{ cm}^3)$:
Typically ₹45 per cubic foot per month, allocated per unit based on estimated inventory turnover (e.g., 30–45 days storage).

### F. Returns & Unsellable Defect Allowance
Customer returns on Amazon India average 5%–15% in general categories (higher in apparel/footwear).
$$\text{Return Cost per Unit} = \text{Selling Price} \times \text{Return Rate \%} \times (\text{Loss on Resale \%} + \text{Reverse Shipping Cost Allocation})$$

---

## 4. Key Financial Performance Indicators (KPIs)

1. **Contribution Profit per Unit (₹):**
   $$\text{Profit} = \text{Net Revenue} - \text{Landed Cost} - \text{Total Marketplace Fees} - \text{Marketing Spend} - \text{Return Loss}$$

2. **Contribution Margin (%):**
   $$\text{Margin \%} = \frac{\text{Contribution Profit}}{\text{Selling Price (Excl. GST)}} \times 100$$
   *Threshold:* $\ge 30\%$ represents a healthy private label product.

3. **Return on Investment on Inventory (ROI %):**
   $$\text{ROI \%} = \frac{\text{Contribution Profit per Unit}}{\text{Landed Cost per Unit}} \times 100$$
   *Threshold:* $\ge 100\%$ indicates that capital doubles upon selling inventory.

4. **Break-Even Selling Price (₹):**
   Minimum price where Contribution Profit equals zero, accounting for variable referral and closing fees.

5. **Break-Even Advertising Cost of Sale (Break-Even ACoS %):**
   $$\text{Break-Even ACoS} = \frac{\text{Pre-Ad Profit per Unit}}{\text{Selling Price}} \times 100$$
   Represents maximum allowable ad spend % before the product incurs a loss.

---

## 5. Three Scenario Projections

The terminal generates three distinct financial scenarios:

| Scenario | Pricing Assumption | PPC / Ad Spend % | Return Rate | Sourcing Cost Variance |
|---|---|---|---|---|
| **Conservative** | 10% lower price (price pressure) | 20% of revenue (high PPC competition) | 12% returns | +10% higher freight/sourcing |
| **Base** | Observed median market price | 12% of revenue (standard launch PPC) | 7% returns | Quoted supplier cost |
| **Optimistic** | 10% premium (differentiated bundle) | 6% of revenue (organic ranking traction)| 4% returns | -5% bulk order discount |

Every calculation step, fee rate, and formula is transparently logged in the UI.
