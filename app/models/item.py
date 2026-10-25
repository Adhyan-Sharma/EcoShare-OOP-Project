"""
Item domain hierarchy demonstrating Abstraction, Inheritance, and Polymorphism.
- Item (Abstract Base Class using abc.ABC)
  ├── DonationItem (free giveaway, calculates avoided manufacturing footprint)
  ├── RentalItem (shared durable tool/equipment, calculates lifecycle extension offset)
  └── RecyclableWaste (scrap material, calculates diverted landfill offset based on material type and weight)
"""
from abc import ABC, abstractmethod
from typing import Optional
from app.models.user import User


class Item(ABC):
    """
    Abstract Base Class representing any resource listed on EcoShare.
    Enforces common interface and polymorphic impact calculation.
    """
    def __init__(
        self,
        item_id: int,
        title: str,
        description: str,
        category: str,
        owner: User,
        status: str = "AVAILABLE"
    ):
        self._item_id: int = item_id
        self._title: str = title.strip()
        self._description: str = description.strip()
        self._category: str = category.strip()
        self._owner: User = owner
        self._status: str = status  # AVAILABLE, RESERVED, COMPLETED, CANCELLED

    @property
    def item_id(self) -> int:
        return self._item_id

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str:
        return self._description

    @property
    def category(self) -> str:
        return self._category

    @property
    def owner(self) -> User:
        return self._owner

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, new_status: str) -> None:
        valid_statuses = {"AVAILABLE", "RESERVED", "COMPLETED", "CANCELLED"}
        upper_status = new_status.upper()
        if upper_status not in valid_statuses:
            raise ValueError(f"Invalid status '{new_status}'. Allowed: {valid_statuses}")
        self._status = upper_status

    @abstractmethod
    def calculate_environmental_impact(self) -> dict:
        """
        Polymorphic method: Every concrete subclass MUST implement this method
        to compute its specific environmental benefits (kg CO2e saved, landfill diverted).
        Returns a dict:
        {
            "co2_saved_kg": float,
            "waste_diverted_kg": float,
            "sdg_target": str,
            "impact_summary": str
        }
        """
        pass

    @abstractmethod
    def get_listing_type(self) -> str:
        """Returns the type descriptor ('DONATION', 'RENTAL', 'RECYCLABLE')."""
        pass

    def to_dict(self) -> dict:
        """Serializes base attributes along with polymorphic impact stats."""
        impact = self.calculate_environmental_impact()
        return {
            "item_id": self._item_id,
            "title": self._title,
            "description": self._description,
            "category": self._category,
            "listing_type": self.get_listing_type(),
            "owner": self._owner.to_dict(),
            "status": self._status,
            "impact": impact
        }


class DonationItem(Item):
    """
    Donation subclass:
    Free handover of usable goods (books, furniture, clothes, appliances).
    Demonstrates Inheritance and polymorphic calculation of avoided production emissions.
    """
    def __init__(
        self,
        item_id: int,
        title: str,
        description: str,
        category: str,
        owner: User,
        condition: str = "Good",
        estimated_market_value: float = 0.0,
        status: str = "AVAILABLE"
    ):
        super().__init__(item_id, title, description, category, owner, status)
        self._condition = condition  # Like New, Good, Fair
        self._estimated_market_value = max(0.0, float(estimated_market_value))

    @property
    def condition(self) -> str:
        return self._condition

    @property
    def estimated_market_value(self) -> float:
        return self._estimated_market_value

    def get_listing_type(self) -> str:
        return "DONATION"

    def calculate_environmental_impact(self) -> dict:
        """
        PolyMorphism: Computes avoided manufacturing CO2 emissions
        based on category standard averages and condition factor.
        """
        category_multipliers = {
            "Electronics": 18.5,
            "Furniture": 14.0,
            "Clothing": 6.5,
            "Books": 2.2,
            "Household": 4.0,
        }
        base_kg = category_multipliers.get(self._category, 3.5)
        condition_factors = {"Like New": 1.2, "Good": 1.0, "Fair": 0.8}
        factor = condition_factors.get(self._condition, 1.0)
        
        co2_saved = round(base_kg * factor, 2)
        waste_diverted = round(base_kg * 0.4, 2)

        return {
            "co2_saved_kg": co2_saved,
            "waste_diverted_kg": waste_diverted,
            "sdg_target": "SDG 12.5 (Substantially reduce waste generation through reuse)",
            "impact_summary": f"Avoided new purchase manufacturing footprint ({co2_saved} kg CO2e saved)"
        }

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "condition": self._condition,
            "estimated_market_value": self._estimated_market_value
        })
        return data


class RentalItem(Item):
    """
    Rental subclass:
    Shared durable goods (power tools, ladders, camping equipment, project sensors).
    Focuses on collaborative consumption (Product-as-a-Service).
    """
    def __init__(
        self,
        item_id: int,
        title: str,
        description: str,
        category: str,
        owner: User,
        rental_fee_per_day: float,
        security_deposit: float = 0.0,
        max_duration_days: int = 7,
        status: str = "AVAILABLE"
    ):
        super().__init__(item_id, title, description, category, owner, status)
        self._rental_fee_per_day = max(0.0, float(rental_fee_per_day))
        self._security_deposit = max(0.0, float(security_deposit))
        self._max_duration_days = max(1, int(max_duration_days))

    @property
    def rental_fee_per_day(self) -> float:
        return self._rental_fee_per_day

    @property
    def security_deposit(self) -> float:
        return self._security_deposit

    @property
    def max_duration_days(self) -> int:
        return self._max_duration_days

    def get_listing_type(self) -> str:
        return "RENTAL"

    def calculate_environmental_impact(self) -> dict:
        """
        PolyMorphism: Computes lifecycle extension through community tool sharing.
        Each shared rental prevents individual purchases of low-usage equipment.
        """
        # Average power tool/equipment production CO2 is ~25-45 kg.
        # Shared utilization offsets ~12.5 kg CO2 per rental cycle.
        co2_saved = 12.5
        waste_diverted = 2.0

        return {
            "co2_saved_kg": co2_saved,
            "waste_diverted_kg": waste_diverted,
            "sdg_target": "SDG 12.2 & 12.5 (Efficient natural resource management & collaborative use)",
            "impact_summary": f"Lifecycle extension via shared equipment ({co2_saved} kg CO2e offset)"
        }

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "rental_fee_per_day": self._rental_fee_per_day,
            "security_deposit": self._security_deposit,
            "max_duration_days": self._max_duration_days
        })
        return data


class RecyclableWaste(Item):
    """
    RecyclableWaste subclass:
    Campus or community scrap (paper/cardboard, plastic bottles, e-waste, aluminum cans).
    Quantified by weight and material grade.
    """
    def __init__(
        self,
        item_id: int,
        title: str,
        description: str,
        category: str,
        owner: User,
        material_type: str,
        weight_kg: float,
        material_grade: str = "Standard",
        status: str = "AVAILABLE"
    ):
        super().__init__(item_id, title, description, category, owner, status)
        self._material_type = material_type.strip()
        self._weight_kg = max(0.01, float(weight_kg))
        self._material_grade = material_grade.strip()

    @property
    def material_type(self) -> str:
        return self._material_type

    @property
    def weight_kg(self) -> float:
        return self._weight_kg

    @property
    def material_grade(self) -> str:
        return self._material_grade

    def get_listing_type(self) -> str:
        return "RECYCLABLE"

    def calculate_environmental_impact(self) -> dict:
        """
        PolyMorphism: Computes direct landfill diversion and emissions reduction
        based on exact mass (kg) and material circularity factor.
        """
        emission_factors = {
            "Aluminium": 9.1,     # kg CO2 saved per kg recycled aluminium
            "Plastic": 2.1,       # kg CO2 saved per kg recycled plastic
            "Paper/Cardboard": 1.3,
            "Glass": 0.45,
            "E-Waste": 4.5
        }
        factor = emission_factors.get(self._material_type, 1.2)
        grade_multiplier = 1.15 if self._material_grade.lower() in ["clean", "grade-a", "high"] else 1.0

        co2_saved = round(self._weight_kg * factor * grade_multiplier, 2)
        waste_diverted = round(self._weight_kg, 2)

        return {
            "co2_saved_kg": co2_saved,
            "waste_diverted_kg": waste_diverted,
            "sdg_target": "SDG 11.6 & 12.5 (Urban municipal waste reduction & circular economy)",
            "impact_summary": f"Diverted {waste_diverted} kg of {self._material_type} from landfill ({co2_saved} kg CO2e saved)"
        }

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "material_type": self._material_type,
            "weight_kg": self._weight_kg,
            "material_grade": self._material_grade
        })
        return data
