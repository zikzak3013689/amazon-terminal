# Windows Installation & Beginner Testing Guide

**Application:** Amazon India Product Research & Opportunity Intelligence Terminal  
**OS Target:** Windows 10 / Windows 11 (64-bit)  
**Primary Market:** Amazon India (`amazon.in`) | **Currency:** INR (₹)

---

## 1. Prerequisites (Free & Pre-installed on Windows)

1. **Python 3.12 or Higher:**
   - Download from [python.org](https://www.python.org/downloads/).
   - ⚠️ **Critical Step:** During installation, check the box: **"Add python.exe to PATH"**.
2. **Terminal / Shell:** Windows PowerShell or Command Prompt (CMD).

---

## 2. Quick One-Click Launch (Recommended)

1. Open File Explorer and navigate to `d:\Python\Amazon` (or your workspace directory).
2. Double-click **`run_terminal.bat`**.
3. The script will automatically verify dependencies and open the terminal in your default browser at `http://localhost:8501`.

---

## 3. Manual Terminal Launch (PowerShell / Command Prompt)

If you prefer launching from PowerShell:

```powershell
# 1. Navigate to the project root
cd d:\Python\Amazon

# 2. (Optional) Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install required packages
pip install -r requirements.txt

# 4. Launch the application
python -m streamlit run app.py
```

---

## 4. Beginner Step-by-Step Testing Guide (Testing Amazon India Products)

This guide takes a non-technical beginner through discovering, analyzing, and validating real products on Amazon India:

### Step 1: Launch the Terminal
1. Double-click `run_terminal.bat`.
2. The terminal opens directly in **Real Research Mode**, calibrated in Indian Rupees (₹) with zero synthetic or fabricated data.
3. Every section now features an interactive **"📖 How to Use"** expandable guide explaining the math, Amazon fee structures, and pro-tips.

### Step 2: Import Legacy Student Spreadsheets
1. Navigate to **Data Importers & Connectors**.
2. Click **Import Legacy Student Template** (imports `OLD Product Research Spreadsheet...xlsx`).
3. Click **Import New Student Template** (imports `🔎 NEW Student Amazon Product Research Template...xlsx`).
4. Notice how original formulas (e.g. `=MEDIAN(...)`, `=0.15*B3`, `=(24000+...)/5`) are parsed into competitor observations and legacy reference notes without corrupting Indian Rupee figures.

### Step 3: Add Your First Genuine Amazon India Listing
1. Go to **Product Explorer & Shortlist** and click **➕ New Product**.
2. Enter a product title (e.g., `Organic Neem Wood Comb Set`).
3. Enter the primary keyword (`neem wood comb`).
4. Select Category `Beauty & Personal Care` and Target Price `₹349`.
5. Click **Save Product**.

### Step 4: Research Competitors Legally & Safely
1. In **Product Detail Deep-Dive**, click the generated **Amazon.in Search** link.
2. Find 3 competing sellers. Copy their ASINs (e.g., `B08...`) and prices from Amazon.in.
3. Click **➕ Add Competing ASIN** to record their prices, review counts, and customer complaints from 1-star reviews.
4. Review the computed **Median Price**, **Review Concentration**, and **Price Dispersion**.

### Step 5: Test Unit Economics in the Profit Sandbox
1. Switch to **Profitability & GST Sandbox**.
2. Input Selling Price: `₹349`, Sourcing Cost: `₹80` (quoted from Jaipur/Saharanpur wood cluster).
3. Toggle `GST Registered: Yes` to verify how 18% GST on Amazon fees is claimed back as an Input Tax Credit (ITC).
4. Review your **Net Contribution Profit** (e.g., ₹95/unit) and **Break-Even ACoS** (maximum allowable advertising spend).

### Step 6: Verify Indian Compliance on the 13-Point Checklist
1. Open the **13-Point Checklist** tab.
2. Verify:
   - Legal Metrology (MRP, Manufacturer & Net Quantity sticker on box)
   - Trademark Clearance via the provided direct link to `ipindiaonline.gov.in`
   - Transit Fragility & Return Risk
3. Watch the system automatically alert you if any blocking gate fails!

---

## 5. Troubleshooting Common Windows Questions

| Issue | Cause | One-Minute Fix |
|---|---|---|
| `'python' is not recognized` | Python was installed without checking "Add to PATH" | Re-run Python installer, choose "Modify", and check "Add Python to environment variables". |
| `Execution of scripts is disabled` (PowerShell) | Windows default security policy blocks `.ps1` | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` or use `run_terminal.bat`. |
| Port 8501 is already in use | Previous Streamlit instance still running | Run `python -m streamlit run app.py --server.port 8502`. |
| Spreadsheet import says file missing | Workbooks are in a different folder | Move the `.xlsx` files into the `d:\Python\Amazon\` directory. |
