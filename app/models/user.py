"""
User domain model demonstrating Encapsulation.
Hides internal fields (e.g. contact email, phone) behind property getters/setters,
validates inputs, and tracks personal eco-impact metrics.
"""
import re
from typing import Optional


class User:
    """
    Demonstrates OOP Encapsulation:
    - Protected attributes prefixed with '_'
    - Strict validation on property setters (e.g., email format, phone digits)
    - Controlled mutation of eco_score and impact stats
    """
    def __init__(
        self,
        user_id: int,
        username: str,
        email: str,
        phone: str,
        role: str = "Resident",
        eco_score: float = 0.0
    ):
        self._user_id: int = user_id
        self._username: str = username
        self.email = email        # Uses property setter for validation
        self.phone = phone        # Uses property setter for validation
        self._role: str = role
        self._eco_score: float = max(0.0, float(eco_score))

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        if not value or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value):
            raise ValueError(f"Invalid email address: '{value}'")
        self._email = value.strip().lower()

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, value: str) -> None:
        cleaned = re.sub(r"[^\d+]", "", value or "")
        if len(cleaned) < 7:
            raise ValueError("Phone number must have at least 7 digits")
        self._phone = cleaned

    @property
    def role(self) -> str:
        return self._role

    @property
    def eco_score(self) -> float:
        return round(self._eco_score, 2)

    def add_eco_score(self, points: float) -> None:
        """Encapsulated method to safely update user's cumulative eco points."""
        if points > 0:
            self._eco_score += points

    def get_masked_contact(self) -> str:
        """Helper showing information hiding - masks sensitive user details for public views."""
        parts = self._email.split("@")
        masked_local = parts[0][0] + "***" + parts[0][-1] if len(parts[0]) > 2 else "***"
        return f"{masked_local}@{parts[1]}"

    def to_dict(self) -> dict:
        return {
            "user_id": self._user_id,
            "username": self._username,
            "email": self._email,
            "phone": self._phone,
            "role": self._role,
            "eco_score": self.eco_score,
            "masked_contact": self.get_masked_contact()
        }

    def __repr__(self) -> str:
        return f"<User id={self._user_id} username='{self._username}' eco_score={self.eco_score}>"
