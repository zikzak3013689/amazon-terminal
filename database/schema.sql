-- Amazon India Product Research Terminal - SQLite Database Schema
-- Version: 1.0.0

PRAGMA foreign_keys = ON;

-- Table: products
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    asin TEXT,
    product_url TEXT,
    marketplace TEXT NOT NULL DEFAULT 'amazon.in',
    category TEXT NOT NULL DEFAULT 'Home & Kitchen',
    subcategory TEXT,
    main_keyword TEXT NOT NULL,
    brand TEXT,
    current_observed_price REAL,
    review_count INTEGER,
    average_rating REAL,
    bestseller_rank INTEGER,
    weight_kg REAL DEFAULT 0.5,
    length_cm REAL DEFAULT 15.0,
    width_cm REAL DEFAULT 10.0,
    height_cm REAL DEFAULT 5.0,
    estimated_demand_notes TEXT,
    competition_notes TEXT,
    research_status TEXT NOT NULL DEFAULT 'New Idea',
    is_demo INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_products_status ON products(research_status);
CREATE INDEX IF NOT EXISTS idx_products_asin ON products(asin);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_is_demo ON products(is_demo);

-- Table: product_keywords
CREATE TABLE IF NOT EXISTS product_keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    keyword TEXT NOT NULL,
    keyword_type TEXT NOT NULL DEFAULT 'long-tail', -- 'main', 'long-tail', 'short-tail', 'generic'
    is_primary INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_keywords_product ON product_keywords(product_id);

-- Table: competitors
CREATE TABLE IF NOT EXISTS competitors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    competitor_asin TEXT NOT NULL,
    competitor_title TEXT NOT NULL,
    brand TEXT,
    product_url TEXT,
    observed_price REAL NOT NULL,
    rating REAL,
    review_count INTEGER,
    bsr INTEGER,
    monthly_sales_est INTEGER,
    monthly_revenue_est REAL,
    seller_name TEXT,
    fulfilment_type TEXT DEFAULT 'FBA', -- FBA, Easy Ship, Self Ship
    strengths TEXT,
    weaknesses TEXT,
    differentiation_angle TEXT,
    observation_date DATE DEFAULT (DATE('now')),
    evidence_source TEXT DEFAULT 'Amazon.in Listing',
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_competitors_product ON competitors(product_id);

-- Table: product_observations (Historical price & rank snapshots)
CREATE TABLE IF NOT EXISTS product_observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    observed_price REAL,
    bestseller_rank INTEGER,
    review_count INTEGER,
    rating REAL,
    source_name TEXT NOT NULL,
    source_url TEXT,
    observation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    marketplace TEXT DEFAULT 'amazon.in',
    collection_method TEXT DEFAULT 'Manual Observation',
    data_type TEXT NOT NULL DEFAULT 'observed', -- observed, estimated, calculated, assumed
    notes TEXT,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Table: keyword_observations (Google Trends & Keyword Planner data)
CREATE TABLE IF NOT EXISTS keyword_observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    keyword TEXT NOT NULL,
    source_platform TEXT NOT NULL, -- 'Google Trends', 'Google Keyword Planner', 'Amazon Search Suggestion'
    search_volume REAL,
    relative_interest_score INTEGER, -- 0-100 for Google Trends
    competition_index TEXT, -- Low, Medium, High
    cpc_bid_low REAL,
    cpc_bid_high REAL,
    geo_location TEXT DEFAULT 'IN',
    timeframe TEXT,
    observation_date DATE DEFAULT (DATE('now')),
    collection_method TEXT DEFAULT 'CSV Import',
    data_type TEXT DEFAULT 'estimated',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_kw_obs_product ON keyword_observations(product_id);

-- Table: supplier_quotes
CREATE TABLE IF NOT EXISTS supplier_quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    supplier_name TEXT NOT NULL,
    supplier_country TEXT NOT NULL DEFAULT 'India',
    supplier_contact TEXT,
    supplier_city_hub TEXT, -- e.g. Moradabad, Surat, Shenzhen
    product_reference TEXT,
    unit_purchase_cost REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'INR',
    exchange_rate_to_inr REAL DEFAULT 1.0,
    moq INTEGER NOT NULL DEFAULT 100,
    packaging_cost REAL DEFAULT 0.0,
    sample_cost REAL DEFAULT 0.0,
    production_lead_time_days INTEGER DEFAULT 15,
    defect_allowance_pct REAL DEFAULT 2.0,
    tax_rate_pct REAL DEFAULT 18.0, -- GST or IGST
    is_tax_recoverable_itc INTEGER DEFAULT 1,
    freight_cost_per_unit REAL DEFAULT 0.0,
    quotation_date DATE DEFAULT (DATE('now')),
    valid_until_date DATE,
    notes TEXT,
    is_primary_supplier INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_quotes_product ON supplier_quotes(product_id);

-- Table: sourcing_costs (Detailed landed cost modeling)
CREATE TABLE IF NOT EXISTS sourcing_costs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    quote_id INTEGER,
    sourcing_type TEXT NOT NULL DEFAULT 'Domestic (India)', -- 'Domestic (India)', 'Overseas Import'
    unit_purchase_cost REAL NOT NULL,
    packaging_cost REAL DEFAULT 0.0,
    inward_shipping_cost REAL DEFAULT 0.0,
    customs_duty_bcd_pct REAL DEFAULT 0.0,
    social_welfare_surcharge_pct REAL DEFAULT 10.0, -- 10% on BCD
    import_igst_pct REAL DEFAULT 18.0,
    inspection_cost_per_unit REAL DEFAULT 0.0,
    port_clearing_cost_per_unit REAL DEFAULT 0.0,
    total_landed_cost_excl_tax REAL NOT NULL,
    total_landed_cost_incl_tax REAL NOT NULL,
    input_tax_credit_amount REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (quote_id) REFERENCES supplier_quotes(id) ON DELETE SET NULL
);

-- Table: profit_scenarios (Conservative, Base, Optimistic)
CREATE TABLE IF NOT EXISTS profit_scenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    scenario_name TEXT NOT NULL, -- 'Conservative', 'Base', 'Optimistic'
    selling_price_gross REAL NOT NULL, -- Inclusive of GST (MRP)
    gst_rate REAL NOT NULL DEFAULT 0.18,
    is_gst_registered INTEGER NOT NULL DEFAULT 1,
    fulfilment_model TEXT NOT NULL DEFAULT 'FBA', -- 'FBA', 'Easy Ship', 'Self Ship'
    referral_fee REAL NOT NULL,
    closing_fee REAL NOT NULL,
    weight_handling_fee REAL NOT NULL,
    pick_pack_fee REAL DEFAULT 0.0,
    storage_fee REAL DEFAULT 0.0,
    amazon_fee_gst REAL NOT NULL,
    landed_cost_unit REAL NOT NULL,
    advertising_spend_unit REAL NOT NULL,
    advertising_spend_pct REAL NOT NULL,
    returns_allowance_pct REAL NOT NULL,
    returns_cost_unit REAL NOT NULL,
    net_revenue_excl_tax REAL NOT NULL,
    net_profit_unit REAL NOT NULL,
    margin_pct REAL NOT NULL,
    roi_pct REAL NOT NULL,
    breakeven_selling_price REAL NOT NULL,
    breakeven_acos_pct REAL NOT NULL,
    monthly_units_est INTEGER DEFAULT 100,
    monthly_net_profit REAL,
    assumptions_json TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_profit_product ON profit_scenarios(product_id);

-- Table: validation_checks
CREATE TABLE IF NOT EXISTS validation_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    check_key TEXT NOT NULL,
    check_category TEXT NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Needs Investigation', -- 'Pass', 'Needs Investigation', 'Fail'
    notes TEXT,
    evidence_source TEXT,
    is_blocking INTEGER NOT NULL DEFAULT 0,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE(product_id, check_key)
);

CREATE INDEX IF NOT EXISTS idx_validation_product ON validation_checks(product_id);

-- Table: opportunity_scores
CREATE TABLE IF NOT EXISTS opportunity_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    total_score REAL NOT NULL, -- 0 to 100
    demand_score REAL NOT NULL,
    competition_score REAL NOT NULL,
    profit_score REAL NOT NULL,
    stability_score REAL NOT NULL,
    differentiation_score REAL NOT NULL,
    sourcing_score REAL NOT NULL,
    confidence_level TEXT NOT NULL, -- 'High', 'Medium', 'Low'
    missing_data_warnings TEXT,
    has_blocking_risks INTEGER DEFAULT 0,
    blocking_reasons TEXT,
    score_breakdown_json TEXT,
    scored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_scores_product ON opportunity_scores(product_id);

-- Table: research_notes
CREATE TABLE IF NOT EXISTS research_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    author TEXT DEFAULT 'User',
    title TEXT,
    content TEXT NOT NULL,
    source_reference TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Table: import_history
CREATE TABLE IF NOT EXISTS import_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    import_type TEXT NOT NULL, -- 'OLD_STUDENT_EXCEL', 'NEW_STUDENT_EXCEL', 'GOOGLE_TRENDS_CSV', 'KEYWORD_PLANNER_CSV', 'GENERIC_EXCEL'
    total_records INTEGER DEFAULT 0,
    imported_count INTEGER DEFAULT 0,
    skipped_count INTEGER DEFAULT 0,
    error_log TEXT,
    raw_payload_json TEXT,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: data_sources
CREATE TABLE IF NOT EXISTS data_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_key TEXT UNIQUE NOT NULL,
    source_name TEXT NOT NULL,
    source_type TEXT NOT NULL,
    status TEXT NOT NULL, -- 'Active', 'Disabled', 'Pending Credentials'
    is_free INTEGER DEFAULT 1,
    configuration_json TEXT,
    last_accessed TIMESTAMP
);

-- Table: hunted_niches
CREATE TABLE IF NOT EXISTS hunted_niches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    niche_name TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'Home & Kitchen',
    target_cluster TEXT,
    problem_solved TEXT,
    target_mrp_low REAL DEFAULT 499.0,
    target_mrp_high REAL DEFAULT 999.0,
    estimated_factory_cost REAL DEFAULT 150.0,
    search_volume_est INTEGER DEFAULT 2500,
    competition_level TEXT DEFAULT 'Low',
    differentiation_hook TEXT,
    notes TEXT,
    status TEXT DEFAULT 'Active Hunting',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_hunted_niches_status ON hunted_niches(status);

-- Table: custom_suppliers
CREATE TABLE IF NOT EXISTS custom_suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_name TEXT NOT NULL,
    hub_city TEXT NOT NULL,
    state TEXT,
    materials_offered TEXT,
    contact_person TEXT,
    phone_whatsapp TEXT,
    indiamart_profile_url TEXT,
    moq INTEGER DEFAULT 100,
    typical_unit_cost REAL,
    sample_cost REAL DEFAULT 0.0,
    lead_time_days INTEGER DEFAULT 14,
    gst_invoice_available INTEGER DEFAULT 1,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_custom_suppliers_hub ON custom_suppliers(hub_city);

-- Table: user_research_criteria (Configurable research thresholds based on Excel methodology)
CREATE TABLE IF NOT EXISTS user_research_criteria (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    min_profit_margin_pct REAL DEFAULT 31.0,
    max_competitor_reviews INTEGER DEFAULT 100,
    min_search_volume INTEGER DEFAULT 500,
    max_weight_kg REAL DEFAULT 0.50,
    min_mrp_inr REAL DEFAULT 499.0,
    max_mrp_inr REAL DEFAULT 1499.0,
    require_domestic_sourcing INTEGER DEFAULT 1,
    require_non_consumable INTEGER DEFAULT 1,
    require_non_fragile INTEGER DEFAULT 1,
    require_zero_hazmat INTEGER DEFAULT 1,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

