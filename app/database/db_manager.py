"""
Database Manager implementing Singleton Pattern for SQLite persistence.
Handles schema initialization, CRUD operations, and maps rows to domain OOP models.
"""
import sqlite3
import os
from typing import List, Optional, Dict, Any
from app.models.user import User
from app.models.item import Item, DonationItem, RentalItem, RecyclableWaste
from app.models.transaction import Transaction, DonationTransaction, RentalTransaction, RecyclingTransaction
from app.services.item_factory import ItemFactory


class DatabaseManager:
    """
    Singleton Database Manager providing unified, encapsulated SQLite persistence.
    """
    _instance = None

    def __new__(cls, db_path: str = None):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: str = None):
        if self._initialized:
            return
        self.db_path = db_path or os.path.join(os.path.dirname(__file__), "ecoshare.db")
        self._init_db()
        self._seed_default_data()
        self._initialized = True

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Users Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    role TEXT NOT NULL,
                    eco_score REAL DEFAULT 0.0
                )
            """)

            # Items Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    category TEXT NOT NULL,
                    owner_id INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'AVAILABLE',
                    condition TEXT,
                    estimated_market_value REAL DEFAULT 0.0,
                    rental_fee_per_day REAL DEFAULT 0.0,
                    security_deposit REAL DEFAULT 0.0,
                    max_duration_days INTEGER DEFAULT 7,
                    material_type TEXT,
                    weight_kg REAL DEFAULT 0.0,
                    material_grade TEXT,
                    FOREIGN KEY(owner_id) REFERENCES users(user_id)
                )
            """)

            # Transactions Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id INTEGER NOT NULL,
                    receiver_id INTEGER NOT NULL,
                    trans_type TEXT NOT NULL,
                    rental_days INTEGER DEFAULT 1,
                    pickup_notes TEXT,
                    status TEXT NOT NULL DEFAULT 'PENDING',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(item_id) REFERENCES items(item_id),
                    FOREIGN KEY(receiver_id) REFERENCES users(user_id)
                )
            """)
            conn.commit()

    def _seed_default_data(self) -> None:
        """Seeds initial campus members and community listings if empty."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM users")
            if cursor.fetchone()["count"] == 0:
                # Add sample users
                users = [
                    ("Aarav Sharma", "aarav@campus.edu", "+919876543210", "Resident Student", 45.0),
                    ("Dr. Ananya Roy", "ananya.roy@campus.edu", "+919812345678", "Faculty Coordinator", 120.0),
                    ("Rohan Mehta", "rohan@campus.edu", "+919922334455", "Eco Club Lead", 85.0),
                    ("Campus Recyclers Hub", "hub@cityrecycle.org", "+919000112233", "Certified Recycler", 250.0),
                ]
                cursor.executemany(
                    "INSERT INTO users (username, email, phone, role, eco_score) VALUES (?, ?, ?, ?, ?)",
                    users
                )

                # Add sample items
                items = [
                    (
                        "DONATION", "Advanced Engineering Mathematics (10th Ed)",
                        "Hardcover textbook in great condition, free for 2nd year juniors.",
                        "Books", 1, "AVAILABLE", "Good", 650.0,
                        0.0, 0.0, 7, None, 0.0, None
                    ),
                    (
                        "RENTAL", "Bosch 650W Impact Drill Kit",
                        "High power drill with full drill bit set for dorm maintenance and robotics builds.",
                        "Tools", 2, "AVAILABLE", None, 0.0,
                        40.0, 200.0, 5, None, 0.0, None
                    ),
                    (
                        "RECYCLABLE", "Clean Cardboard Boxes & Packing Corrugation",
                        "Clean flattened moving cartons suitable for paper recycling mill.",
                        "Recyclables", 3, "AVAILABLE", None, 0.0,
                        0.0, 0.0, 7, "Paper/Cardboard", 14.5, "Grade-A Clean"
                    ),
                    (
                        "RECYCLABLE", "Assorted E-Waste & Motherboards",
                        "Burnt microcontrollers, scrap PCB boards, and old copper coils from final year projects.",
                        "Electronics", 1, "AVAILABLE", None, 0.0,
                        0.0, 0.0, 7, "E-Waste", 6.8, "Scrap Grade"
                    )
                ]
                cursor.executemany("""
                    INSERT INTO items (
                        item_type, title, description, category, owner_id, status,
                        condition, estimated_market_value,
                        rental_fee_per_day, security_deposit, max_duration_days,
                        material_type, weight_kg, material_grade
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, items)
                conn.commit()

    # --- User Data Access Methods ---
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return User(
                user_id=row["user_id"],
                username=row["username"],
                email=row["email"],
                phone=row["phone"],
                role=row["role"],
                eco_score=row["eco_score"]
            )

    def get_all_users(self) -> List[User]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users ORDER BY eco_score DESC")
            return [
                User(
                    user_id=row["user_id"],
                    username=row["username"],
                    email=row["email"],
                    phone=row["phone"],
                    role=row["role"],
                    eco_score=row["eco_score"]
                )
                for row in cursor.fetchall()
            ]

    def create_user(self, username: str, email: str, phone: str, role: str) -> User:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, phone, role, eco_score) VALUES (?, ?, ?, ?, 0.0)",
                (username.strip(), email.strip(), phone.strip(), role.strip())
            )
            conn.commit()
            new_id = cursor.lastrowid
            return self.get_user_by_id(new_id)

    def update_user_eco_score(self, user_id: int, new_score: float) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET eco_score = ? WHERE user_id = ?", (new_score, user_id))
            conn.commit()

    # --- Item Data Access Methods ---
    def _row_to_item(self, row: sqlite3.Row) -> Optional[Item]:
        owner = self.get_user_by_id(row["owner_id"])
        if not owner:
            return None
        return ItemFactory.create_item(
            item_id=row["item_id"],
            item_type=row["item_type"],
            owner=owner,
            data={
                "title": row["title"],
                "description": row["description"],
                "category": row["category"],
                "status": row["status"],
                "condition": row["condition"],
                "estimated_market_value": row["estimated_market_value"],
                "rental_fee_per_day": row["rental_fee_per_day"],
                "security_deposit": row["security_deposit"],
                "max_duration_days": row["max_duration_days"],
                "material_type": row["material_type"],
                "weight_kg": row["weight_kg"],
                "material_grade": row["material_grade"]
            }
        )

    def get_item_by_id(self, item_id: int) -> Optional[Item]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM items WHERE item_id = ?", (item_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_item(row)

    def get_all_items(self, status: Optional[str] = None) -> List[Item]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute("SELECT * FROM items WHERE status = ? ORDER BY item_id DESC", (status,))
            else:
                cursor.execute("SELECT * FROM items ORDER BY item_id DESC")
            items = []
            for row in cursor.fetchall():
                obj = self._row_to_item(row)
                if obj:
                    items.append(obj)
            return items

    def create_item(self, item_type: str, owner_id: int, form_data: Dict[str, Any]) -> Item:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO items (
                    item_type, title, description, category, owner_id, status,
                    condition, estimated_market_value,
                    rental_fee_per_day, security_deposit, max_duration_days,
                    material_type, weight_kg, material_grade
                ) VALUES (?, ?, ?, ?, ?, 'AVAILABLE', ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item_type.upper(),
                form_data.get("title", ""),
                form_data.get("description", ""),
                form_data.get("category", "General"),
                owner_id,
                form_data.get("condition"),
                float(form_data.get("estimated_market_value", 0.0) or 0.0),
                float(form_data.get("rental_fee_per_day", 0.0) or 0.0),
                float(form_data.get("security_deposit", 0.0) or 0.0),
                int(form_data.get("max_duration_days", 7) or 7),
                form_data.get("material_type"),
                float(form_data.get("weight_kg", 0.0) or 0.0),
                form_data.get("material_grade")
            ))
            conn.commit()
            new_id = cursor.lastrowid
            return self.get_item_by_id(new_id)

    def update_item_status(self, item_id: int, new_status: str) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE items SET status = ? WHERE item_id = ?", (new_status.upper(), item_id))
            conn.commit()

    # --- Transaction Data Access Methods ---
    def create_transaction(
        self,
        item_id: int,
        receiver_id: int,
        trans_type: str,
        rental_days: int = 1,
        pickup_notes: str = ""
    ) -> Transaction:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            from datetime import datetime
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO transactions (item_id, receiver_id, trans_type, rental_days, pickup_notes, status, created_at)
                VALUES (?, ?, ?, ?, ?, 'PENDING', ?)
            """, (item_id, receiver_id, trans_type.upper(), rental_days, pickup_notes, created_at))
            conn.commit()
            trans_id = cursor.lastrowid
            # Also set the item status to RESERVED
            self.update_item_status(item_id, "RESERVED")
            return self.get_transaction_by_id(trans_id)

    def get_transaction_by_id(self, trans_id: int) -> Optional[Transaction]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transactions WHERE transaction_id = ?", (trans_id,))
            row = cursor.fetchone()
            if not row:
                return None
            item = self.get_item_by_id(row["item_id"])
            receiver = self.get_user_by_id(row["receiver_id"])
            if not item or not receiver:
                return None

            t_type = row["trans_type"]
            if "RENTAL" in t_type:
                return RentalTransaction(
                    transaction_id=row["transaction_id"],
                    item=item,
                    receiver=receiver,
                    rental_days=row["rental_days"],
                    created_at=row["created_at"],
                    status=row["status"]
                )
            elif "RECYCL" in t_type:
                return RecyclingTransaction(
                    transaction_id=row["transaction_id"],
                    item=item,
                    receiver=receiver,
                    pickup_notes=row["pickup_notes"],
                    created_at=row["created_at"],
                    status=row["status"]
                )
            else:
                return DonationTransaction(
                    transaction_id=row["transaction_id"],
                    item=item,
                    receiver=receiver,
                    created_at=row["created_at"],
                    status=row["status"]
                )

    def get_all_transactions(self) -> List[Transaction]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT transaction_id FROM transactions ORDER BY transaction_id DESC")
            results = []
            for row in cursor.fetchall():
                tx = self.get_transaction_by_id(row["transaction_id"])
                if tx:
                    results.append(tx)
            return results

    def complete_transaction(self, trans_id: int) -> dict:
        """Invokes polymorphic process_completion() on the Transaction model."""
        tx = self.get_transaction_by_id(trans_id)
        if not tx:
            raise ValueError(f"Transaction #{trans_id} not found")
        
        # Execute polymorphic completion business logic
        completion_result = tx.process_completion()

        # Update persistent store
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE transactions SET status = 'COMPLETED' WHERE transaction_id = ?", (trans_id,))
            cursor.execute("UPDATE items SET status = ? WHERE item_id = ?", (tx.item.status, tx.item.item_id))
            cursor.execute("UPDATE users SET eco_score = ? WHERE user_id = ?", (tx.provider.eco_score, tx.provider.user_id))
            cursor.execute("UPDATE users SET eco_score = ? WHERE user_id = ?", (tx.receiver.eco_score, tx.receiver.user_id))
            conn.commit()

        return completion_result
