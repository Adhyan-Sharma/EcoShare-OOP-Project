"""
Factory Method Pattern implementation for Item creation.
Encapsulates instantiation logic based on listing type.
"""
from typing import Dict, Any
from app.models.user import User
from app.models.item import Item, DonationItem, RentalItem, RecyclableWaste


class ItemFactory:
    """
    Factory pattern class that abstracts away the conditional logic
    of creating DonationItem, RentalItem, or RecyclableWaste.
    """
    @staticmethod
    def create_item(item_id: int, item_type: str, owner: User, data: Dict[str, Any]) -> Item:
        norm_type = item_type.upper().strip()
        title = data.get("title", "")
        description = data.get("description", "")
        category = data.get("category", "General")
        status = data.get("status", "AVAILABLE")

        if norm_type in ["DONATION", "DONATIONITEM"]:
            return DonationItem(
                item_id=item_id,
                title=title,
                description=description,
                category=category,
                owner=owner,
                condition=data.get("condition", "Good"),
                estimated_market_value=float(data.get("estimated_market_value", 0.0) or 0.0),
                status=status
            )
        elif norm_type in ["RENTAL", "RENTALITEM"]:
            return RentalItem(
                item_id=item_id,
                title=title,
                description=description,
                category=category,
                owner=owner,
                rental_fee_per_day=float(data.get("rental_fee_per_day", 0.0) or 0.0),
                security_deposit=float(data.get("security_deposit", 0.0) or 0.0),
                max_duration_days=int(data.get("max_duration_days", 7) or 7),
                status=status
            )
        elif norm_type in ["RECYCLABLE", "RECYCLABLEWASTE", "WASTE"]:
            return RecyclableWaste(
                item_id=item_id,
                title=title,
                description=description,
                category=category,
                owner=owner,
                material_type=data.get("material_type", "Plastic"),
                weight_kg=float(data.get("weight_kg", 1.0) or 1.0),
                material_grade=data.get("material_grade", "Standard"),
                status=status
            )
        else:
            raise ValueError(f"Unknown item type: '{item_type}'. Must be DONATION, RENTAL, or RECYCLABLE.")
