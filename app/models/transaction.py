"""
Transaction and Exchange hierarchy demonstrating Abstraction and Composition.
Links Users (Requester/Receiver and Owner/Provider) with an Item.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from app.models.user import User
from app.models.item import Item, DonationItem, RentalItem, RecyclableWaste


class Transaction(ABC):
    """
    Abstract Base Class for an exchange transaction.
    Demonstrates OOP Abstraction and Composition (User + Item).
    """
    def __init__(
        self,
        transaction_id: int,
        item: Item,
        receiver: User,
        created_at: Optional[str] = None,
        status: str = "PENDING"
    ):
        self._transaction_id = transaction_id
        self._item = item
        self._receiver = receiver
        self._created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._status = status  # PENDING, APPROVED, COMPLETED, CANCELLED

    @property
    def transaction_id(self) -> int:
        return self._transaction_id

    @property
    def item(self) -> Item:
        return self._item

    @property
    def provider(self) -> User:
        return self._item.owner

    @property
    def receiver(self) -> User:
        return self._receiver

    @property
    def created_at(self) -> str:
        return self._created_at

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, new_status: str) -> None:
        valid = {"PENDING", "APPROVED", "COMPLETED", "CANCELLED"}
        if new_status.upper() not in valid:
            raise ValueError(f"Invalid transaction status: {new_status}")
        self._status = new_status.upper()

    @abstractmethod
    def process_completion(self) -> dict:
        """
        Finalizes the transaction, transitions item state,
        and awards eco-points to participating users.
        """
        pass

    @abstractmethod
    def get_transaction_type(self) -> str:
        pass

    def to_dict(self) -> dict:
        return {
            "transaction_id": self._transaction_id,
            "type": self.get_transaction_type(),
            "status": self._status,
            "created_at": self._created_at,
            "item": self._item.to_dict(),
            "provider": self.provider.to_dict(),
            "receiver": self.receiver.to_dict()
        }


class DonationTransaction(Transaction):
    """Concrete transaction for donating an item permanently."""
    def get_transaction_type(self) -> str:
        return "DONATION_HANDOVER"

    def process_completion(self) -> dict:
        self.status = "COMPLETED"
        self._item.status = "COMPLETED"
        
        # Award eco-points: Provider gets points for donating; Receiver gets reuse badge
        impact = self._item.calculate_environmental_impact()
        points = max(5.0, impact["co2_saved_kg"] * 1.5)
        self.provider.add_eco_score(points)
        self.receiver.add_eco_score(points * 0.5)

        return {
            "status": "COMPLETED",
            "points_awarded_provider": round(points, 2),
            "points_awarded_receiver": round(points * 0.5, 2),
            "environmental_impact": impact
        }


class RentalTransaction(Transaction):
    """Concrete transaction for renting out tools/equipment for N days."""
    def __init__(
        self,
        transaction_id: int,
        item: RentalItem,
        receiver: User,
        rental_days: int = 1,
        created_at: Optional[str] = None,
        status: str = "PENDING"
    ):
        super().__init__(transaction_id, item, receiver, created_at, status)
        self._rental_days = max(1, int(rental_days))

    @property
    def rental_days(self) -> int:
        return self._rental_days

    def get_transaction_type(self) -> str:
        return "EQUIPMENT_RENTAL"

    def calculate_total_fee(self) -> float:
        if isinstance(self._item, RentalItem):
            return round(self._item.rental_fee_per_day * self._rental_days, 2)
        return 0.0

    def process_completion(self) -> dict:
        self.status = "COMPLETED"
        # Tool is returned to available pool for the next community member!
        self._item.status = "AVAILABLE"

        impact = self._item.calculate_environmental_impact()
        points = 10.0
        self.provider.add_eco_score(points)
        self.receiver.add_eco_score(points)

        return {
            "status": "COMPLETED",
            "fee_paid": self.calculate_total_fee(),
            "item_restored_to_pool": True,
            "points_awarded": points,
            "environmental_impact": impact
        }

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "rental_days": self._rental_days,
            "total_fee": self.calculate_total_fee()
        })
        return data


class RecyclingTransaction(Transaction):
    """Concrete transaction for dispatching scrap/recyclables to a collection agent/center."""
    def __init__(
        self,
        transaction_id: int,
        item: RecyclableWaste,
        receiver: User,
        pickup_notes: str = "",
        created_at: Optional[str] = None,
        status: str = "PENDING"
    ):
        super().__init__(transaction_id, item, receiver, created_at, status)
        self._pickup_notes = pickup_notes

    @property
    def pickup_notes(self) -> str:
        return self._pickup_notes

    def get_transaction_type(self) -> str:
        return "RECYCLING_DISPATCH"

    def process_completion(self) -> dict:
        self.status = "COMPLETED"
        self._item.status = "COMPLETED"

        impact = self._item.calculate_environmental_impact()
        points = max(2.0, impact["waste_diverted_kg"] * 3.0)
        self.provider.add_eco_score(points)
        self.receiver.add_eco_score(points)

        return {
            "status": "COMPLETED",
            "points_awarded": round(points, 2),
            "environmental_impact": impact
        }

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({"pickup_notes": self._pickup_notes})
        return data
