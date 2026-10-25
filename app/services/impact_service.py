"""
Impact Service computing aggregate metrics across all items and transactions.
Demonstrates polymorphic iteration over diverse Item instances.
"""
from typing import List, Dict, Any
from app.models.item import Item


class ImpactService:
    """
    Computes cumulative SDG 11 & SDG 12 environmental indicators
    by iterating polymorphically over heterogeneous Item objects.
    """
    @staticmethod
    def calculate_total_platform_impact(items: List[Item]) -> Dict[str, Any]:
        total_co2 = 0.0
        total_diverted = 0.0
        by_category: Dict[str, float] = {}
        by_type: Dict[str, int] = {"DONATION": 0, "RENTAL": 0, "RECYCLABLE": 0}

        for item in items:
            # Polymorphic method call
            impact = item.calculate_environmental_impact()
            total_co2 += impact.get("co2_saved_kg", 0.0)
            total_diverted += impact.get("waste_diverted_kg", 0.0)
            
            # Category breakdown
            cat = item.category
            by_category[cat] = round(by_category.get(cat, 0.0) + impact.get("co2_saved_kg", 0.0), 2)
            
            # Type count
            l_type = item.get_listing_type()
            by_type[l_type] = by_type.get(l_type, 0) + 1

        # Real-world equivalents for presentation & viva
        equivalent_trees_planted = round(total_co2 / 21.7, 1)  # 1 mature tree absorbs ~21.7 kg CO2/yr
        car_km_avoided = round(total_co2 * 5.2, 1)            # Avg car emits ~0.192 kg CO2/km

        return {
            "total_co2_saved_kg": round(total_co2, 2),
            "total_waste_diverted_kg": round(total_diverted, 2),
            "equivalent_trees_planted": equivalent_trees_planted,
            "car_km_avoided": car_km_avoided,
            "category_breakdown": by_category,
            "type_counts": by_type,
            "total_listings": len(items)
        }
