"""Nexus HTTP API for Farmer CRUD + Income Ledger endpoints."""

from __future__ import annotations

import os
import structlog
from pathlib import Path
from datetime import date
import uuid

from nexus import Nexus, JSONResponse
from starlette.requests import Request

from .models import FarmerCreate, SaleCreate, ObligationCreate, ObligationType
from .repository import (
    FarmerRepository,
    PhoneFormatError,
    LandSizeError,
    DuplicatePhoneError,
    FarmerNotFoundError,
)
from .obligation_repository import (
    ObligationRepository,
    ObligationNotFoundError,
    compute_priority,
    due_in_days,
    ObligationPriority,
)
from .cashflow_service import CashFlowService, CashFlowStatus
from .sale_repository import (
    SaleRepository,
    SaleNotFoundError,
    compute_baseline_price,
    DISTRESS_THRESHOLD,
    MSP_ONION,
)

logger = structlog.get_logger(__name__)

# DB path — can be overridden via env for testing
DB_PATH = os.environ.get("KISANMITRA_DB", ":memory:")


def _phone_response(farmer) -> dict:
    """Return the phone-only response fields per spec."""
    return {
        "phone": farmer.phone,
        "name": farmer.name,
        "district": farmer.district,
        "land_size": farmer.land_size,
        "land_tenure": farmer.land_tenure.value,
        "crop_type": farmer.crop_type.value,
        "season": farmer.season.value,
        "created_at": farmer.created_at.isoformat() + "Z",
    }


class FarmerHandlers:
    """HTTP handlers for /api/farmers endpoints."""

    def __init__(self, repo: FarmerRepository):
        self._repo = repo

    async def create(self, request: Request) -> JSONResponse:
        """POST /api/farmers — create new farmer. 201 / 400 / 409."""
        logger.info("create_farmer.start")
        try:
            body = await request.json()
        except Exception:
            logger.warning("create_farmer.invalid_json")
            return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

        try:
            data = FarmerCreate(**body)
        except Exception as e:
            logger.warning("create_farmer.validation_error", error=str(e))
            return JSONResponse({"error": str(e)}, status_code=400)

        try:
            farmer = await self._repo.create(data)
            logger.info("create_farmer.ok", phone=farmer.phone)
            return JSONResponse(_phone_response(farmer), status_code=201)
        except DuplicatePhoneError:
            logger.warning("create_farmer.duplicate", phone=data.phone)
            return JSONResponse(
                {"error": f"Farmer with phone {data.phone} already exists"}, status_code=409
            )
        except PhoneFormatError as e:
            logger.warning("create_farmer.phone_format_error", error=str(e))
            return JSONResponse({"error": str(e)}, status_code=400)
        except LandSizeError as e:
            logger.warning("create_farmer.land_size_error", error=str(e))
            return JSONResponse({"error": str(e)}, status_code=400)

    async def get(self, request: Request, phone: str) -> JSONResponse:
        """GET /api/farmers/{phone} — get farmer by phone. 200 / 404."""
        logger.info("get_farmer.start", phone=phone)
        try:
            farmer = await self._repo.get_by_phone(phone)
            logger.info("get_farmer.ok", phone=phone)
            return JSONResponse(farmer.model_dump(mode="json"), status_code=200)
        except PhoneFormatError as e:
            logger.warning("get_farmer.phone_format_error", phone=phone, error=str(e))
            return JSONResponse({"error": str(e)}, status_code=400)
        except FarmerNotFoundError:
            logger.warning("get_farmer.not_found", phone=phone)
            return JSONResponse(
                {"error": f"Farmer with phone {phone} not found"}, status_code=404
            )

    async def update(self, request: Request, phone: str) -> JSONResponse:
        """PUT /api/farmers/{phone} — update farmer. 200 / 400 / 404."""
        logger.info("update_farmer.start", phone=phone)
        try:
            body = await request.json()
        except Exception:
            logger.warning("update_farmer.invalid_json", phone=phone)
            return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

        # Only accept updatable fields
        updatable = frozenset([
            "name", "land_size", "land_tenure", "crop_type", "season", "primary_language"
        ])
        fields = {k: v for k, v in body.items() if k in updatable}
        if not fields:
            return JSONResponse(
                {"error": "No updatable fields provided"}, status_code=400
            )

        try:
            farmer = await self._repo.update(phone, fields)
            logger.info("update_farmer.ok", phone=phone)
            return JSONResponse(farmer.model_dump(mode="json"), status_code=200)
        except PhoneFormatError as e:
            logger.warning("update_farmer.phone_format_error", phone=phone, error=str(e))
            return JSONResponse({"error": str(e)}, status_code=400)
        except FarmerNotFoundError:
            logger.warning("update_farmer.not_found", phone=phone)
            return JSONResponse(
                {"error": f"Farmer with phone {phone} not found"}, status_code=404
            )
        except (LandSizeError, ValueError) as e:
            logger.warning("update_farmer.validation_error", phone=phone, error=str(e))
            return JSONResponse({"error": str(e)}, status_code=400)

    async def delete(self, request: Request, phone: str) -> JSONResponse:
        """DELETE /api/farmers/{phone} — soft-delete. 204 / 404."""
        logger.info("delete_farmer.start", phone=phone)
        try:
            await self._repo.delete(phone)
            logger.info("delete_farmer.ok", phone=phone)
            return JSONResponse({}, status_code=204)
        except PhoneFormatError as e:
            logger.warning("delete_farmer.phone_format_error", phone=phone, error=str(e))
            return JSONResponse({"error": str(e)}, status_code=400)
        except FarmerNotFoundError:
            logger.warning("delete_farmer.not_found", phone=phone)
            return JSONResponse(
                {"error": f"Farmer with phone {phone} not found"}, status_code=404
            )


class SaleHandlers:
    """HTTP handlers for /api/farmers/{phone}/sales endpoints."""

    def __init__(self, sale_repo: SaleRepository, farmer_repo: FarmerRepository):
        self._sale_repo = sale_repo
        self._farmer_repo = farmer_repo

    async def create_sale(self, request: Request, phone: str) -> JSONResponse:
        """POST /api/farmers/{phone}/sales — record a sale. 201 / 400 / 404."""
        logger.info("create_sale.start", phone=phone)
        # Validate farmer exists
        try:
            await self._farmer_repo.get_by_phone(phone)
        except FarmerNotFoundError:
            logger.warning("create_sale.farmer_not_found", phone=phone)
            return JSONResponse(
                {"error": f"Farmer with phone {phone} not found"}, status_code=404
            )
        except PhoneFormatError as e:
            logger.warning("create_sale.phone_format_error", phone=phone, error=str(e))
            return JSONResponse({"error": str(e)}, status_code=400)

        try:
            body = await request.json()
        except Exception:
            logger.warning("create_sale.invalid_json", phone=phone)
            return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

        # Inject phone and generate ID
        body["phone"] = phone
        body["id"] = str(uuid.uuid4())

        try:
            data = SaleCreate(**body)
        except Exception as e:
            logger.warning("create_sale.validation_error", phone=phone, error=str(e))
            return JSONResponse({"error": str(e)}, status_code=400)

        try:
            sale = await self._sale_repo.create(data)
            logger.info("create_sale.ok", phone=phone, sale_id=sale.id)
            return JSONResponse(
                {
                    "id": sale.id,
                    "sale_date": sale.sale_date.isoformat(),
                    "quantity_quintal": sale.quantity_quintal,
                    "price_per_quintal": sale.price_per_quintal,
                    "mandi": sale.mandi,
                    "total_revenue": sale.total_revenue,
                    "is_distress": sale.is_distress,
                    "distress_reason": sale.distress_reason,
                    "notes": sale.notes,
                    "created_at": sale.created_at.isoformat() + "Z",
                },
                status_code=201,
            )
        except Exception as e:
            logger.exception("create_sale.error", phone=phone, error=str(e))
            return JSONResponse({"error": str(e)}, status_code=400)

    async def get_ledger(self, request: Request, phone: str) -> JSONResponse:
        """GET /api/farmers/{phone}/ledger — returns sales list + baseline + distress count."""
        logger.info("get_ledger.start", phone=phone)
        try:
            await self._farmer_repo.get_by_phone(phone)
        except FarmerNotFoundError:
            logger.warning("get_ledger.farmer_not_found", phone=phone)
            return JSONResponse(
                {"error": f"Farmer with phone {phone} not found"}, status_code=404
            )
        except PhoneFormatError as e:
            logger.warning("get_ledger.phone_format_error", phone=phone, error=str(e))
            return JSONResponse({"error": str(e)}, status_code=400)

        sales = await self._sale_repo.list_by_phone(phone)
        baseline = compute_baseline_price(sales)
        distress_count = sum(1 for s in sales if s.is_distress)
        total_revenue = sum(s.total_revenue for s in sales)

        sale_items = []
        for s in sales:
            if s.is_distress:
                reason_display = {
                    "FORCED_SELL": "Sold immediately due to cash emergency",
                    "NO_STORAGE": "No storage capacity — had to sell at any price",
                    "WEAK_BARGAINING": "Sold at low price due to weak bargaining position",
                    "MIDDLEMAN_EXPLOITATION": "Sold to village trader below mandi price",
                }.get(s.distress_reason, s.distress_reason or "")
                status_display = "तनाव (Distress)"
            else:
                reason_display = None
                status_display = "सामान्य (Normal)"

            sale_items.append(
                {
                    "id": s.id,
                    "sale_date": s.sale_date.isoformat(),
                    "quantity_quintal": s.quantity_quintal,
                    "price_per_quintal": s.price_per_quintal,
                    "mandi": s.mandi,
                    "total_revenue": s.total_revenue,
                    "is_distress": s.is_distress,
                    "distress_reason": reason_display,
                    "status_display": status_display,
                }
            )

        response = {
            "phone": phone,
            "season": "RABI",
            "year": date.today().year,
            "baseline_price": int(baseline) if baseline is not None else None,
            "baseline_unit": "quintal",
            "total_sales": len(sales),
            "total_revenue": total_revenue,
            "distress_count": distress_count,
            "sales": sale_items,
        }
        logger.info("get_ledger.ok", phone=phone, total_sales=len(sales))
        return JSONResponse(response, status_code=200)

    async def get_baseline(self, request: Request, phone: str) -> JSONResponse:
        """GET /api/farmers/{phone}/baseline — returns current baseline price + calculation."""
        logger.info("get_baseline.start", phone=phone)
        try:
            await self._farmer_repo.get_by_phone(phone)
        except FarmerNotFoundError:
            logger.warning("get_baseline.farmer_not_found", phone=phone)
            return JSONResponse(
                {"error": f"Farmer with phone {phone} not found"}, status_code=404
            )
        except PhoneFormatError as e:
            logger.warning("get_baseline.phone_format_error", phone=phone, error=str(e))
            return JSONResponse({"error": str(e)}, status_code=400)

        sales = await self._sale_repo.list_by_phone(phone)
        non_distress = [s for s in sales if not s.is_distress]
        baseline = compute_baseline_price(sales)

        # Build display message
        if baseline is None:
            message = "No baseline available — all recorded sales were distress sales."
        elif baseline >= 3500:
            message = "Your baseline is excellent — strong bargaining position"
        elif baseline >= 2700:
            message = f"Your baseline: ₹{baseline:.0f}/quintal — above market average"
        elif baseline >= 2000:
            message = f"Your baseline: ₹{baseline:.0f}/quintal — monitor prices carefully"
        else:
            message = "Your baseline is low — consider FPO aggregation"

        response = {
            "phone": phone,
            "baseline_price": int(baseline) if baseline is not None else None,
            "baseline_unit": "quintal",
            "msp_onion": MSP_ONION,
            "distress_threshold": DISTRESS_THRESHOLD,
            "non_distress_sales_count": len(non_distress),
            "distress_sales_count": sum(1 for s in sales if s.is_distress),
            "message": message,
        }
        if non_distress:
            response["calculation"] = {
                "total_revenue": int(sum(s.quantity_quintal * s.price_per_quintal for s in non_distress)),
                "total_quantity": sum(s.quantity_quintal for s in non_distress),
                "formula": "total_revenue / total_quantity",
            }
        logger.info("get_baseline.ok", phone=phone, baseline_price=baseline)
        return JSONResponse(response, status_code=200)


class ObligationHandlers:
    """HTTP handlers for /api/farmers/{phone}/obligations endpoints."""

    def __init__(self, obligation_repo: ObligationRepository, farmer_repo: FarmerRepository):
        self._obligation_repo = obligation_repo
        self._farmer_repo = farmer_repo

    def _obligation_response(self, ob, today) -> dict:
        """Return obligation response fields per spec."""
        return {
            "id": ob.id,
            "type": ob.type.value,
            "amount": ob.amount,
            "due_date": ob.due_date.isoformat(),
            "priority": compute_priority(ob.due_date, today).value,
            "due_in_days": due_in_days(ob.due_date, today),
            "reminder_flag": ob.reminder_flag,
            "is_paid": ob.is_paid,
            "description": ob.description,
            "reminder_date": ob.reminder_date.isoformat() if ob.reminder_date else None,
            "paid_date": ob.paid_date.isoformat() if ob.paid_date else None,
            "paid_amount": ob.paid_amount,
            "created_at": ob.created_at.isoformat() + "Z",
        }

    async def create(self, request: Request, phone: str) -> JSONResponse:
        """POST /api/farmers/{phone}/obligations — create obligation. 201 / 400 / 404."""
        logger.info("create_obligation.start", phone=phone)
        # Validate farmer exists
        try:
            await self._farmer_repo.get_by_phone(phone)
        except FarmerNotFoundError:
            logger.warning("create_obligation.farmer_not_found", phone=phone)
            return JSONResponse(
                {"error": f"Farmer with phone {phone} not found"}, status_code=404
            )
        except PhoneFormatError as e:
            logger.warning("create_obligation.phone_format_error", phone=phone, error=str(e))
            return JSONResponse({"error": str(e)}, status_code=400)

        try:
            body = await request.json()
        except Exception:
            logger.warning("create_obligation.invalid_json", phone=phone)
            return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

        # Inject phone and generate ID
        body["phone"] = phone
        body["id"] = str(uuid.uuid4())

        try:
            data = ObligationCreate(**body)
        except Exception as e:
            logger.warning("create_obligation.validation_error", phone=phone, error=str(e))
            return JSONResponse({"error": str(e)}, status_code=400)

        try:
            obligation = await self._obligation_repo.create(data)
            logger.info("create_obligation.ok", phone=phone, obligation_id=obligation.id)
            today = date.today()
            return JSONResponse(self._obligation_response(obligation, today), status_code=201)
        except ValueError as e:
            logger.warning("create_obligation.constraint_error", phone=phone, error=str(e))
            return JSONResponse({"error": str(e)}, status_code=400)

    async def list(self, request: Request, phone: str) -> JSONResponse:
        """GET /api/farmers/{phone}/obligations — list obligations. 200 / 400 / 404."""
        logger.info("list_obligations.start", phone=phone)
        try:
            await self._farmer_repo.get_by_phone(phone)
        except FarmerNotFoundError:
            logger.warning("list_obligations.farmer_not_found", phone=phone)
            return JSONResponse(
                {"error": f"Farmer with phone {phone} not found"}, status_code=404
            )
        except PhoneFormatError as e:
            logger.warning("list_obligations.phone_format_error", phone=phone, error=str(e))
            return JSONResponse({"error": str(e)}, status_code=400)

        # Parse query params
        query_params = dict(request.query_params)
        status = query_params.get("status", "pending")
        if status not in ("pending", "paid", "all"):
            status = "pending"

        obligations = await self._obligation_repo.list_by_phone(phone, status=status)
        today = date.today()
        total_pending = sum(ob.amount for ob in obligations if not ob.is_paid)

        response = {
            "phone": phone,
            "obligations": [self._obligation_response(ob, today) for ob in obligations],
            "total_pending": total_pending,
        }
        logger.info("list_obligations.ok", phone=phone, count=len(obligations))
        return JSONResponse(response, status_code=200)

    async def list_urgent(self, request: Request, phone: str) -> JSONResponse:
        """GET /api/farmers/{phone}/obligations/urgent — list urgent obligations. 200 / 400 / 404."""
        logger.info("list_urgent_obligations.start", phone=phone)
        try:
            await self._farmer_repo.get_by_phone(phone)
        except FarmerNotFoundError:
            logger.warning("list_urgent_obligations.farmer_not_found", phone=phone)
            return JSONResponse(
                {"error": f"Farmer with phone {phone} not found"}, status_code=404
            )
        except PhoneFormatError as e:
            logger.warning("list_urgent_obligations.phone_format_error", phone=phone, error=str(e))
            return JSONResponse({"error": str(e)}, status_code=400)

        obligations = await self._obligation_repo.list_urgent(phone)
        today = date.today()

        response = {
            "phone": phone,
            "obligations": [self._obligation_response(ob, today) for ob in obligations],
        }
        logger.info("list_urgent_obligations.ok", phone=phone, count=len(obligations))
        return JSONResponse(response, status_code=200)

    async def update_reminder(self, request: Request, phone: str, id: str) -> JSONResponse:
        """PUT /api/farmers/{phone}/obligations/{id}/reminder — update reminder. 200 / 400 / 404."""
        logger.info("update_reminder.start", phone=phone, obligation_id=id)
        try:
            await self._farmer_repo.get_by_phone(phone)
        except FarmerNotFoundError:
            logger.warning("update_reminder.farmer_not_found", phone=phone)
            return JSONResponse(
                {"error": f"Farmer with phone {phone} not found"}, status_code=404
            )
        except PhoneFormatError as e:
            logger.warning("update_reminder.phone_format_error", phone=phone, error=str(e))
            return JSONResponse({"error": str(e)}, status_code=400)

        try:
            body = await request.json()
        except Exception:
            logger.warning("update_reminder.invalid_json", phone=phone, obligation_id=id)
            return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

        reminder_flag = body.get("reminder_flag", False)
        reminder_date_str = body.get("reminder_date")
        reminder_date = date.fromisoformat(reminder_date_str) if reminder_date_str else None

        try:
            obligation = await self._obligation_repo.update_reminder(
                id, phone, reminder_flag=reminder_flag, reminder_date=reminder_date
            )
            logger.info("update_reminder.ok", phone=phone, obligation_id=id)
            today = date.today()
            return JSONResponse(self._obligation_response(obligation, today), status_code=200)
        except ObligationNotFoundError:
            logger.warning("update_reminder.not_found", phone=phone, obligation_id=id)
            return JSONResponse(
                {"error": f"Obligation with id {id} not found for phone {phone}"}, status_code=404
            )
        except ValueError as e:
            logger.warning("update_reminder.constraint_error", phone=phone, obligation_id=id, error=str(e))
            return JSONResponse({"error": str(e)}, status_code=400)

    async def mark_paid(self, request: Request, phone: str, id: str) -> JSONResponse:
        """DELETE /api/farmers/{phone}/obligations/{id} — mark as paid. 204 / 404."""
        logger.info("mark_obligation_paid.start", phone=phone, obligation_id=id)
        try:
            await self._farmer_repo.get_by_phone(phone)
        except FarmerNotFoundError:
            logger.warning("mark_obligation_paid.farmer_not_found", phone=phone)
            return JSONResponse(
                {"error": f"Farmer with phone {phone} not found"}, status_code=404
            )
        except PhoneFormatError as e:
            logger.warning("mark_obligation_paid.phone_format_error", phone=phone, error=str(e))
            return JSONResponse({"error": str(e)}, status_code=400)

        try:
            body = await request.json() if request.method == "DELETE" else {}
            # For DELETE, check if paid_amount was provided
            paid_amount = body.get("paid_amount") if body else None
        except Exception:
            paid_amount = None

        try:
            await self._obligation_repo.mark_paid(id, phone, paid_amount=paid_amount)
            logger.info("mark_obligation_paid.ok", phone=phone, obligation_id=id)
            return JSONResponse({}, status_code=204)
        except ObligationNotFoundError:
            logger.warning("mark_obligation_paid.not_found", phone=phone, obligation_id=id)
            return JSONResponse(
                {"error": f"Obligation with id {id} not found for phone {phone}"}, status_code=404
            )


class CashFlowHandlers:
    """HTTP handlers for /api/farmers/{phone}/cashflow endpoint."""

    def __init__(self, cashflow_service: CashFlowService, farmer_repo: FarmerRepository):
        self._cashflow_service = cashflow_service
        self._farmer_repo = farmer_repo

    async def get_cashflow(self, request: Request, phone: str) -> JSONResponse:
        """GET /api/farmers/{phone}/cashflow?days=30 — compute cash flow. 200 / 400 / 404."""
        logger.info("get_cashflow.start", phone=phone)
        try:
            await self._farmer_repo.get_by_phone(phone)
        except FarmerNotFoundError:
            logger.warning("get_cashflow.farmer_not_found", phone=phone)
            return JSONResponse(
                {"error": f"Farmer with phone {phone} not found"}, status_code=404
            )
        except PhoneFormatError as e:
            logger.warning("get_cashflow.phone_format_error", phone=phone, error=str(e))
            return JSONResponse({"error": str(e)}, status_code=400)

        # Parse query params
        query_params = dict(request.query_params)
        try:
            days = int(query_params.get("days", 30))
            days = max(1, min(days, 90))
        except ValueError:
            days = 30

        expected_sale_revenue = query_params.get("expected_sale_revenue")
        if expected_sale_revenue is not None:
            try:
                expected_sale_revenue = int(expected_sale_revenue)
            except ValueError:
                expected_sale_revenue = None

        other_income = query_params.get("other_income")
        if other_income is not None:
            try:
                other_income = int(other_income)
            except ValueError:
                other_income = None

        result = await self._cashflow_service.compute(
            phone,
            window_days=days,
            expected_sale_revenue=expected_sale_revenue,
            other_income=other_income,
        )
        logger.info("get_cashflow.ok", phone=phone, status=result["cash_flow"]["status"])
        return JSONResponse(result, status_code=200)


def create_app() -> Nexus:
    """Build and configure the Nexus app with farmer + obligation routes."""
    app = Nexus(enable_http_transport=True, enable_durability=False)

    # DB path — re-read each call so env override takes effect
    db_path = os.environ.get("KISANMITRA_DB", ":memory:")

    # Repositories are app-level singletons
    farmer_repo = FarmerRepository(db_path)
    sale_repo = SaleRepository(db_path)
    obligation_repo = ObligationRepository(db_path)

    farmer_handlers = FarmerHandlers(farmer_repo)
    sale_handlers = SaleHandlers(sale_repo, farmer_repo)
    obligation_handlers = ObligationHandlers(obligation_repo, farmer_repo)
    cashflow_handlers = CashFlowHandlers(CashFlowService(obligation_repo), farmer_repo)

    # Farmer routes
    app.endpoint("/api/farmers", methods=["POST"])(farmer_handlers.create)
    app.endpoint("/api/farmers/{phone}", methods=["GET"])(farmer_handlers.get)
    app.endpoint("/api/farmers/{phone}", methods=["PUT"])(farmer_handlers.update)
    app.endpoint("/api/farmers/{phone}", methods=["DELETE"])(farmer_handlers.delete)

    # Sale routes
    app.endpoint("/api/farmers/{phone}/sales", methods=["POST"])(sale_handlers.create_sale)
    app.endpoint("/api/farmers/{phone}/ledger", methods=["GET"])(sale_handlers.get_ledger)
    app.endpoint("/api/farmers/{phone}/baseline", methods=["GET"])(sale_handlers.get_baseline)

    # Obligation routes
    app.endpoint("/api/farmers/{phone}/obligations", methods=["POST"])(obligation_handlers.create)
    app.endpoint("/api/farmers/{phone}/obligations", methods=["GET"])(obligation_handlers.list)
    app.endpoint("/api/farmers/{phone}/obligations/urgent", methods=["GET"])(obligation_handlers.list_urgent)
    app.endpoint("/api/farmers/{phone}/obligations/{id}/reminder", methods=["PUT"])(obligation_handlers.update_reminder)
    app.endpoint("/api/farmers/{phone}/obligations/{id}", methods=["DELETE"])(obligation_handlers.mark_paid)

    # Cash flow route
    app.endpoint("/api/farmers/{phone}/cashflow", methods=["GET"])(cashflow_handlers.get_cashflow)

    return app
