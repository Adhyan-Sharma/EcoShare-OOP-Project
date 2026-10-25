import pytest
from app.models.user import User
from app.models.item import DonationItem, RentalItem, RecyclableWaste, Item
from app.models.transaction import DonationTransaction, RentalTransaction, RecyclingTransaction
from app.services.item_factory import ItemFactory
from app.services.impact_service import ImpactService
from app.services.notification import InMemoryNotificationService


def test_encapsulation_user():
    """Test User property encapsulation and validation."""
    u = User(1, "rahul", "rahul@campus.edu", "+919876543210")
    assert u.username == "rahul"
    assert u.email == "rahul@campus.edu"
    assert u.eco_score == 0.0

    # Test mutation via encapsulated method
    u.add_eco_score(15.5)
    assert u.eco_score == 15.5

    # Test masking sensitive info
    assert u.get_masked_contact() == "r***l@campus.edu"

    # Test invalid email validation raises error
    with pytest.raises(ValueError):
        u.email = "invalid-email"

    # Test invalid phone validation raises error
    with pytest.raises(ValueError):
        u.phone = "123"


def test_polymorphic_environmental_impact():
    """Test polymorphic calculate_environmental_impact across subclasses."""
    owner = User(1, "donor", "donor@campus.edu", "+919876543210")

    donation = DonationItem(
        item_id=101,
        title="Physics Textbook",
        description="University Physics textbook",
        category="Books",
        owner=owner,
        condition="Good"
    )

    rental = RentalItem(
        item_id=102,
        title="Lawn Mower",
        description="Electric lawn mower for community grass trimming",
        category="Tools",
        owner=owner,
        rental_fee_per_day=50.0
    )

    waste = RecyclableWaste(
        item_id=103,
        title="Aluminum Soft Drink Cans",
        description="Clean crushed beverage cans",
        category="Recyclables",
        owner=owner,
        material_type="Aluminium",
        weight_kg=10.0
    )

    items = [donation, rental, waste]

    # Verify all items share the base Item interface
    for item in items:
        assert isinstance(item, Item)
        impact = item.calculate_environmental_impact()
        assert "co2_saved_kg" in impact
        assert "waste_diverted_kg" in impact
        assert impact["co2_saved_kg"] > 0

    # Check distinct polymorphic formulas
    assert donation.calculate_environmental_impact()["co2_saved_kg"] == 2.2
    assert rental.calculate_environmental_impact()["co2_saved_kg"] == 12.5
    # Recyclable: 10 kg * 9.1 factor = 91.0 kg CO2 saved
    assert waste.calculate_environmental_impact()["co2_saved_kg"] == 91.0


def test_factory_pattern():
    """Test ItemFactory creates proper subclass instances."""
    owner = User(2, "priya", "priya@campus.edu", "+919988776655")

    item1 = ItemFactory.create_item(
        item_id=201,
        item_type="DONATION",
        owner=owner,
        data={"title": "Jacket", "description": "Warm winter jacket", "category": "Clothing"}
    )
    assert isinstance(item1, DonationItem)
    assert item1.get_listing_type() == "DONATION"

    item2 = ItemFactory.create_item(
        item_id=202,
        item_type="RENTAL",
        owner=owner,
        data={"title": "Oscilloscope", "category": "Electronics", "rental_fee_per_day": 75}
    )
    assert isinstance(item2, RentalItem)
    assert item2.rental_fee_per_day == 75.0

    item3 = ItemFactory.create_item(
        item_id=203,
        item_type="RECYCLABLE",
        owner=owner,
        data={"title": "Plastic Bottles", "material_type": "Plastic", "weight_kg": 5.0}
    )
    assert isinstance(item3, RecyclableWaste)
    assert item3.weight_kg == 5.0


def test_transaction_completion_and_state_transition():
    """Test abstraction and state changes during transaction lifecycle."""
    giver = User(1, "giver", "giver@campus.edu", "+919876543210")
    receiver = User(2, "receiver", "receiver@campus.edu", "+919123456789")

    item = DonationItem(301, "Study Desk", "Wooden desk", "Furniture", giver)
    assert item.status == "AVAILABLE"

    tx = DonationTransaction(1, item, receiver)
    assert tx.status == "PENDING"
    assert tx.provider.username == "giver"

    res = tx.process_completion()
    assert tx.status == "COMPLETED"
    assert item.status == "COMPLETED"
    assert giver.eco_score > 0
    assert receiver.eco_score > 0
    assert res["status"] == "COMPLETED"


def test_notification_service_abstraction():
    """Test notification abstraction interface and in-memory log."""
    notif = InMemoryNotificationService()
    assert notif.send("Alice", "alice@example.com", "Your item has been requested!")
    logs = notif.get_recent_notifications()
    assert len(logs) == 1
    assert logs[0]["recipient_name"] == "Alice"
