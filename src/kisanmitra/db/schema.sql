-- Kisanmitra Database Schema
-- Nashik Pilot Configuration

-- farmers table
CREATE TABLE IF NOT EXISTS farmers (
    phone TEXT PRIMARY KEY CHECK (length(phone) = 10),
    name TEXT NOT NULL,
    village TEXT NOT NULL,
    block TEXT NOT NULL,
    district TEXT NOT NULL DEFAULT 'NASHIK',
    state TEXT NOT NULL DEFAULT 'MAHARASHTRA',
    land_size REAL NOT NULL CHECK (land_size > 0 AND land_size <= 100),
    land_tenure TEXT NOT NULL CHECK (land_tenure IN ('OWNER', 'TENANT', 'SHARECROPPER')),
    crop_type TEXT NOT NULL CHECK (crop_type IN ('RABI_ONION', 'KHARIF_PADDY', 'RABI_WHEAT', 'SUMMER_MAIZE')),
    season TEXT NOT NULL CHECK (season IN ('RABI', 'KHARIF', 'SUMMER')),
    primary_language TEXT NOT NULL DEFAULT 'MARATHI',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1
);

-- obligations table
CREATE TABLE IF NOT EXISTS obligations (
    id TEXT PRIMARY KEY,
    phone TEXT NOT NULL REFERENCES farmers(phone),
    type TEXT NOT NULL CHECK (type IN ('KCC_EMI', 'SCHOOL_FEE', 'LAND_RENT', 'COOPERATIVE_DUE', 'INSURANCE_PREMIUM', 'WATER_ELECTRICITY', 'OTHER')),
    amount INTEGER NOT NULL CHECK (amount > 0),
    due_date DATE NOT NULL,
    description TEXT,
    reminder_date DATE,
    reminder_flag INTEGER DEFAULT 0,
    is_paid INTEGER DEFAULT 0,
    paid_date DATE,
    paid_amount INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- sales table
CREATE TABLE IF NOT EXISTS sales (
    id TEXT PRIMARY KEY,
    phone TEXT NOT NULL REFERENCES farmers(phone),
    sale_date DATE NOT NULL,
    quantity_quintal REAL NOT NULL CHECK (quantity_quintal > 0),
    price_per_quintal INTEGER NOT NULL CHECK (price_per_quintal >= 0),
    mandi TEXT NOT NULL,
    total_revenue INTEGER GENERATED ALWAYS AS (CAST(quantity_quintal * price_per_quintal AS INTEGER)) STORED,
    is_distress INTEGER,
    distress_reason TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- price_alerts table
CREATE TABLE IF NOT EXISTS price_alerts (
    id TEXT PRIMARY KEY,
    phone TEXT NOT NULL REFERENCES farmers(phone),
    enabled INTEGER DEFAULT 1,
    drop_threshold INTEGER DEFAULT 2,
    rise_threshold_percent INTEGER DEFAULT 8,
    preferred_mandis TEXT DEFAULT '["Lasalgaon", "Niphad"]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Scheme eligibility cache
CREATE TABLE IF NOT EXISTS scheme_eligibility (
    phone TEXT NOT NULL REFERENCES farmers(phone),
    scheme_id TEXT NOT NULL,
    eligible INTEGER,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (phone, scheme_id)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_farmers_district ON farmers(district);
CREATE INDEX IF NOT EXISTS idx_farmers_block ON farmers(block);
CREATE INDEX IF NOT EXISTS idx_obligations_phone ON obligations(phone);
CREATE INDEX IF NOT EXISTS idx_obligations_due_date ON obligations(due_date);
CREATE INDEX IF NOT EXISTS idx_obligations_is_paid ON obligations(is_paid);
CREATE INDEX IF NOT EXISTS idx_sales_phone ON sales(phone);
CREATE INDEX IF NOT EXISTS idx_sales_sale_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_price_alerts_phone ON price_alerts(phone);
