"""Integration tests for src/kisanmitra/api.py — Nexus HTTP endpoints."""
from starlette.testclient import TestClient

from kisanmitra.api import create_app


def _make_client(tmp_path=None):
    """Return a TestClient wired to the underlying FastAPI app.

    Uses a file-based temp DB so all requests share the same SQLite schema.
    """
    import os
    import asyncio
    from pathlib import Path

    if tmp_path is None:
        import tempfile
        tmp_path = Path(tempfile.mkdtemp())

    db_path = tmp_path / "test.db"
    os.environ["KISANMITRA_DB"] = str(db_path)

    # Initialize schema before creating app
    schema_path = Path(__file__).parent.parent.parent / "src" / "kisanmitra" / "db" / "schema.sql"
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.executescript(schema_path.read_text())
    conn.close()

    app = create_app()
    return TestClient(app.fastapi_app), db_path


def test_create_farmer_ok():
    """POST /api/farmers — 201 on valid farmer creation."""
    client, _ = _make_client()
    body = {
        "phone": "9999999999",
        "name": "Test Farmer",
        "village": "TestVillage",
        "block": "TestBlock",
        "district": "NASHIK",
        "state": "MAHARASHTRA",
        "land_size": 2.5,
        "land_tenure": "SHARECROPPER",
        "crop_type": "RABI_ONION",
        "season": "RABI",
        "primary_language": "MARATHI",
    }
    response = client.post("/api/farmers", json=body)
    assert response.status_code == 201
    data = response.json()
    assert data["phone"] == "9999999999"
    assert data["name"] == "Test Farmer"
    assert data["land_tenure"] == "SHARECROPPER"


def test_create_farmer_duplicate():
    """POST /api/farmers — 409 on duplicate phone."""
    client, _ = _make_client()
    body = {
        "phone": "9999999998",
        "name": "First Farmer",
        "village": "Village",
        "block": "Block",
        "land_size": 1.0,
        "land_tenure": "OWNER",
        "crop_type": "RABI_ONION",
        "season": "RABI",
    }
    r1 = client.post("/api/farmers", json=body)
    assert r1.status_code == 201
    r2 = client.post("/api/farmers", json=body)
    assert r2.status_code == 409
    assert "already exists" in r2.json()["error"]


def test_create_farmer_invalid_json():
    """POST /api/farmers — 400 on malformed JSON."""
    client, _ = _make_client()
    response = client.post("/api/farmers", content=b"not json")
    assert response.status_code == 400


def test_create_farmer_validation_error():
    """POST /api/farmers — 400 on invalid field values."""
    client, _ = _make_client()
    body = {
        "phone": "123",  # too short
        "name": "Test",
        "village": "Village",
        "block": "Block",
        "land_size": -1.0,  # negative
        "land_tenure": "OWNER",
        "crop_type": "RABI_ONION",
        "season": "RABI",
    }
    response = client.post("/api/farmers", json=body)
    assert response.status_code == 400


def test_get_farmer_ok():
    """GET /api/farmers/{phone} — 200 with farmer data."""
    client, _ = _make_client()
    create_body = {
        "phone": "9999999997",
        "name": "Get Test",
        "village": "Village",
        "block": "Block",
        "land_size": 3.0,
        "land_tenure": "TENANT",
        "crop_type": "KHARIF_PADDY",
        "season": "KHARIF",
    }
    client.post("/api/farmers", json=create_body)
    response = client.get("/api/farmers/9999999997")
    assert response.status_code == 200
    data = response.json()
    assert data["phone"] == "9999999997"
    assert data["name"] == "Get Test"


def test_get_farmer_not_found():
    """GET /api/farmers/{phone} — 404 for unknown phone."""
    client, _ = _make_client()
    response = client.get("/api/farmers/0000000000")
    assert response.status_code == 404


def test_update_farmer_ok():
    """PUT /api/farmers/{phone} — 200 on successful update."""
    client, _ = _make_client()
    client.post("/api/farmers", json={
        "phone": "9999999996",
        "name": "Original Name",
        "village": "Village",
        "block": "Block",
        "land_size": 1.5,
        "land_tenure": "OWNER",
        "crop_type": "RABI_ONION",
        "season": "RABI",
    })
    response = client.put("/api/farmers/9999999996", json={"name": "Updated Name"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


def test_delete_farmer_ok():
    """DELETE /api/farmers/{phone} — 204 on successful delete."""
    client, _ = _make_client()
    client.post("/api/farmers", json={
        "phone": "9999999995",
        "name": "To Delete",
        "village": "V",
        "block": "B",
        "land_size": 1.0,
        "land_tenure": "OWNER",
        "crop_type": "RABI_ONION",
        "season": "RABI",
    })
    response = client.delete("/api/farmers/9999999995")
    assert response.status_code == 204


def test_create_obligation_ok():
    """POST /api/farmers/{phone}/obligations — 201 on valid obligation."""
    client, _ = _make_client()
    client.post("/api/farmers", json={
        "phone": "9999999994",
        "name": "Obligation Farmer",
        "village": "V",
        "block": "B",
        "land_size": 1.0,
        "land_tenure": "OWNER",
        "crop_type": "RABI_ONION",
        "season": "RABI",
    })
    ob_body = {
        "type": "KCC_EMI",
        "amount": 3200,
        "due_date": "2026-06-15",
        "description": "KCC EMI June",
    }
    response = client.post("/api/farmers/9999999994/obligations", json=ob_body)
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "KCC_EMI"
    assert data["amount"] == 3200
    assert "priority" in data
    assert "due_in_days" in data


def test_create_obligation_farmer_not_found():
    """POST /api/farmers/{phone}/obligations — 404 if farmer missing."""
    client, _ = _make_client()
    response = client.post("/api/farmers/0000000000/obligations", json={
        "type": "KCC_EMI",
        "amount": 1000,
        "due_date": "2026-06-15",
    })
    assert response.status_code == 404


def test_list_obligations():
    """GET /api/farmers/{phone}/obligations — 200 with obligation list."""
    client, _ = _make_client()
    client.post("/api/farmers", json={
        "phone": "9999999993",
        "name": "List Test",
        "village": "V",
        "block": "B",
        "land_size": 1.0,
        "land_tenure": "OWNER",
        "crop_type": "RABI_ONION",
        "season": "RABI",
    })
    client.post("/api/farmers/9999999993/obligations", json={
        "type": "SCHOOL_FEE",
        "amount": 5000,
        "due_date": "2026-05-30",
    })
    response = client.get("/api/farmers/9999999993/obligations")
    assert response.status_code == 200
    data = response.json()
    assert "obligations" in data
    assert len(data["obligations"]) >= 1


def test_get_ledger():
    """GET /api/farmers/{phone}/ledger — 200 with sales ledger."""
    client, _ = _make_client()
    client.post("/api/farmers", json={
        "phone": "9999999992",
        "name": "Ledger Test",
        "village": "V",
        "block": "B",
        "land_size": 1.0,
        "land_tenure": "OWNER",
        "crop_type": "RABI_ONION",
        "season": "RABI",
    })
    response = client.get("/api/farmers/9999999992/ledger")
    assert response.status_code == 200
    data = response.json()
    assert data["phone"] == "9999999992"
    assert "baseline_price" in data
    assert "total_sales" in data


def test_get_baseline():
    """GET /api/farmers/{phone}/baseline — 200 with baseline price."""
    client, _ = _make_client()
    client.post("/api/farmers", json={
        "phone": "9999999991",
        "name": "Baseline Test",
        "village": "V",
        "block": "B",
        "land_size": 1.0,
        "land_tenure": "OWNER",
        "crop_type": "RABI_ONION",
        "season": "RABI",
    })
    response = client.get("/api/farmers/9999999991/baseline")
    assert response.status_code == 200
    data = response.json()
    assert "baseline_price" in data
    assert "msp_onion" in data
    assert "distress_threshold" in data


def test_get_cashflow():
    """GET /api/farmers/{phone}/cashflow — 200 with cash flow computation."""
    client, _ = _make_client()
    client.post("/api/farmers", json={
        "phone": "9999999990",
        "name": "Cashflow Test",
        "village": "V",
        "block": "B",
        "land_size": 1.0,
        "land_tenure": "OWNER",
        "crop_type": "RABI_ONION",
        "season": "RABI",
    })
    client.post("/api/farmers/9999999990/obligations", json={
        "type": "KCC_EMI",
        "amount": 3200,
        "due_date": "2026-05-25",
    })
    response = client.get("/api/farmers/9999999990/cashflow?days=30")
    assert response.status_code == 200
    data = response.json()
    assert "cash_flow" in data
    assert "income" in data
    assert "obligations" in data


def test_quantity_quintal_upper_bound():
    """SaleCreate enforces le=1000 on quantity_quintal."""
    client, _ = _make_client()
    client.post("/api/farmers", json={
        "phone": "9999999989",
        "name": "Qty Bound",
        "village": "V",
        "block": "B",
        "land_size": 1.0,
        "land_tenure": "OWNER",
        "crop_type": "RABI_ONION",
        "season": "RABI",
    })
    sale_body = {
        "sale_date": "2026-05-01",
        "quantity_quintal": 1500,  # exceeds 1000 limit
        "price_per_quintal": 2800,
        "mandi": "Lasalgaon",
    }
    response = client.post("/api/farmers/9999999989/sales", json=sale_body)
    assert response.status_code == 400
