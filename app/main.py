"""
FastAPI application router and web endpoints for EcoShare.
Binds together the OOP Domain Models, DatabaseManager, Services, and HTML views.
"""
from fastapi import FastAPI, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os

from app.database.db_manager import DatabaseManager
from app.services.impact_service import ImpactService
from app.services.notification import InMemoryNotificationService

app = FastAPI(
    title="EcoShare: Community Resource & Waste Exchange",
    description="OOP Lab Project demonstrating Encapsulation, Inheritance, Polymorphism, Abstraction, and Factory Pattern."
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)
db = DatabaseManager()
notification_service = InMemoryNotificationService()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, type: str = None):
    all_items = db.get_all_items()
    filtered_items = [i for i in all_items if i.get_listing_type() == type] if type else all_items
    stats = ImpactService.calculate_total_platform_impact(all_items)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "items": filtered_items,
            "selected_type": type,
            "stats": stats
        }
    )


@app.get("/list-item", response_class=HTMLResponse)
async def list_item_page(request: Request):
    users = db.get_all_users()
    return templates.TemplateResponse(
        request=request,
        name="list_item.html",
        context={"users": users}
    )


@app.post("/list-item")
async def create_item_endpoint(
    request: Request,
    item_type: str = Form(...),
    owner_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    condition: str = Form(None),
    estimated_market_value: float = Form(0.0),
    rental_fee_per_day: float = Form(0.0),
    security_deposit: float = Form(0.0),
    max_duration_days: int = Form(7),
    material_type: str = Form(None),
    weight_kg: float = Form(0.0),
    material_grade: str = Form(None),
):
    owner = db.get_user_by_id(owner_id)
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")

    form_data = {
        "title": title,
        "description": description,
        "category": category,
        "condition": condition,
        "estimated_market_value": estimated_market_value,
        "rental_fee_per_day": rental_fee_per_day,
        "security_deposit": security_deposit,
        "max_duration_days": max_duration_days,
        "material_type": material_type,
        "weight_kg": weight_kg,
        "material_grade": material_grade
    }

    item = db.create_item(item_type, owner_id, form_data)
    notification_service.send(
        recipient_name=owner.username,
        recipient_email=owner.email,
        message=f"Your resource '{item.title}' has been listed successfully as a {item_type}."
    )
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/request-item/{item_id}", response_class=HTMLResponse)
async def request_item_page(request: Request, item_id: int):
    item = db.get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    users = db.get_all_users()
    return templates.TemplateResponse(
        request=request,
        name="request_item.html",
        context={
            "item": item,
            "users": users
        }
    )


@app.post("/request-item/{item_id}")
async def submit_request_endpoint(
    item_id: int,
    receiver_id: int = Form(...),
    rental_days: int = Form(1),
    pickup_notes: str = Form("")
):
    item = db.get_item_by_id(item_id)
    receiver = db.get_user_by_id(receiver_id)
    if not item or not receiver:
        raise HTTPException(status_code=404, detail="Item or user not found")

    tx = db.create_transaction(
        item_id=item_id,
        receiver_id=receiver_id,
        trans_type=item.get_listing_type(),
        rental_days=rental_days,
        pickup_notes=pickup_notes
    )

    # Notify provider
    notification_service.send(
        recipient_name=item.owner.username,
        recipient_email=item.owner.email,
        message=f"{receiver.username} requested your item '{item.title}' (Tx #{tx.transaction_id})."
    )

    return RedirectResponse(url="/exchanges", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/exchanges", response_class=HTMLResponse)
async def exchanges_page(request: Request):
    transactions = db.get_all_transactions()
    notifications = notification_service.get_recent_notifications(10)
    return templates.TemplateResponse(
        request=request,
        name="transactions.html",
        context={
            "transactions": transactions,
            "notifications": notifications
        }
    )


@app.post("/complete-transaction/{trans_id}")
async def complete_tx_endpoint(trans_id: int):
    res = db.complete_transaction(trans_id)
    tx = db.get_transaction_by_id(trans_id)

    # Dispatch completion notification
    notification_service.send(
        recipient_name=tx.provider.username,
        recipient_email=tx.provider.email,
        message=f"Transaction #{trans_id} completed! Eco-score awarded. Thank you for supporting SDG 11 & 12."
    )

    return RedirectResponse(url="/exchanges", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/impact", response_class=HTMLResponse)
async def impact_page(request: Request):
    items = db.get_all_items()
    users = db.get_all_users()
    stats = ImpactService.calculate_total_platform_impact(items)
    return templates.TemplateResponse(
        request=request,
        name="impact.html",
        context={
            "stats": stats,
            "users": users
        }
    )


@app.get("/viva-doc", response_class=HTMLResponse)
async def viva_doc_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="viva.html"
    )


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
