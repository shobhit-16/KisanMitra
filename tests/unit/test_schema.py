"""Tests for Kisanmitra database schema."""

import sqlite3
import os
import pytest
from pathlib import Path

# Path to the schema file
SCHEMA_PATH = Path(__file__).parent.parent.parent / "src" / "kisanmitra" / "db" / "schema.sql"


class TestSchemaSQL:
    """Tests for schema SQL parsing and structure."""

    def test_schema_file_exists(self):
        """Test that schema.sql file exists."""
        assert SCHEMA_PATH.exists(), f"Schema file not found at {SCHEMA_PATH}"

    def test_schema_sql_parses_without_error(self):
        """Test that schema SQL parses without error in SQLite."""
        schema_content = SCHEMA_PATH.read_text()

        # Create in-memory database and parse the schema
        conn = sqlite3.connect(":memory:")

        # Use executescript to properly handle the full schema
        conn.executescript(schema_content)

        conn.close()

    def test_farmers_table_creation(self):
        """Test farmers table can be created."""
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()

        cursor.execute("""
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
            )
        """)

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='farmers'")
        result = cursor.fetchone()
        assert result is not None, "farmers table was not created"

        conn.close()

    def test_obligations_table_creation(self):
        """Test obligations table can be created."""
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS farmers (
                phone TEXT PRIMARY KEY CHECK (length(phone) = 10)
            )
        """)

        cursor.execute("""
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
            )
        """)

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='obligations'")
        result = cursor.fetchone()
        assert result is not None, "obligations table was not created"

        conn.close()

    def test_sales_table_creation(self):
        """Test sales table can be created."""
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS farmers (
                phone TEXT PRIMARY KEY CHECK (length(phone) = 10)
            )
        """)

        cursor.execute("""
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
            )
        """)

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sales'")
        result = cursor.fetchone()
        assert result is not None, "sales table was not created"

        conn.close()

    def test_schema_migrations_can_be_applied(self):
        """Test that full schema can be applied to a fresh database."""
        schema_content = SCHEMA_PATH.read_text()

        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()

        # Execute the full schema
        cursor.executescript(schema_content)

        # Verify all expected tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        expected_tables = ["farmers", "obligations", "sales", "price_alerts", "scheme_eligibility"]
        for table in expected_tables:
            assert table in tables, f"Table {table} not found in schema"

        # Verify indexes exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]

        expected_indexes = [
            "idx_farmers_district",
            "idx_farmers_block",
            "idx_obligations_phone",
            "idx_obligations_due_date",
            "idx_obligations_is_paid",
            "idx_sales_phone",
            "idx_sales_sale_date",
            "idx_price_alerts_phone",
        ]
        for index in expected_indexes:
            assert index in indexes, f"Index {index} not found in schema"

        conn.close()


class TestFarmerConstraints:
    """Tests for farmer table constraints."""

    def test_phone_must_be_10_digits(self):
        """Test that phone constraint enforces 10 digit requirement."""
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS farmers (
                phone TEXT PRIMARY KEY CHECK (length(phone) = 10)
            )
        """)

        # Valid 10-digit phone
        cursor.execute("INSERT INTO farmers (phone) VALUES ('9876543210')")
        conn.commit()

        # Invalid phone (too short)
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("INSERT INTO farmers (phone) VALUES ('12345')")

        conn.close()

    def test_land_size_bounds(self):
        """Test land_size must be between 0 and 100."""
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS farmers (
                phone TEXT PRIMARY KEY,
                land_size REAL NOT NULL CHECK (land_size > 0 AND land_size <= 100)
            )
        """)

        # Valid land size
        cursor.execute("INSERT INTO farmers (phone, land_size) VALUES ('9876543210', 2.5)")
        conn.commit()

        # Invalid (too large)
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("INSERT INTO farmers (phone, land_size) VALUES ('9876543211', 150)")

        conn.close()

    def test_land_tenure_enum(self):
        """Test land_tenure must be valid enum value."""
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS farmers (
                phone TEXT PRIMARY KEY,
                land_tenure TEXT NOT NULL CHECK (land_tenure IN ('OWNER', 'TENANT', 'SHARECROPPER'))
            )
        """)

        # Valid values
        for tenure in ["OWNER", "TENANT", "SHARECROPPER"]:
            cursor.execute(f"INSERT INTO farmers (phone, land_tenure) VALUES ('9876543210', '{tenure}')")
            conn.commit()
            cursor.execute("DELETE FROM farmers")

        # Invalid value
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("INSERT INTO farmers (phone, land_tenure) VALUES ('9876543210', 'INVALID')")

        conn.close()
