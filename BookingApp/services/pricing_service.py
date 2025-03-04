from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models import Avg
from ..models import SeasonalDemand

class DynamicPricingService:
    def __init__(self):
        self.base_multiplier = Decimal('1.00')
        self.max_multiplier = Decimal('2.00')
        self.min_multiplier = Decimal('0.80')

    def calculate_price_multiplier(self, category, item_id, date):
        """Calculate dynamic price multiplier based on demand and seasonality."""
        factors = {
            'demand_factor': self._get_demand_factor(category, item_id, date),
            'seasonal_factor': self._get_seasonal_factor(date),
            'day_of_week_factor': self._get_day_of_week_factor(date),
            'occupancy_factor': self._get_occupancy_factor(category, date)
        }
        
        # Calculate weighted average of all factors
        multiplier = sum(factors.values()) / len(factors)
        
        # Ensure multiplier is within bounds
        multiplier = max(self.min_multiplier, min(self.max_multiplier, multiplier))
        
        return multiplier

    def _get_demand_factor(self, category, item_id, date):
        """Calculate factor based on historical demand."""
        historical_demand = SeasonalDemand.objects.filter(
            category=category,
            item_id=item_id,
            date__month=date.month
        ).aggregate(Avg('bookings_count'))['bookings_count__avg'] or 0

        if historical_demand > 80:
            return Decimal('1.50')
        elif historical_demand > 60:
            return Decimal('1.25')
        elif historical_demand > 40:
            return Decimal('1.10')
        elif historical_demand < 20:
            return Decimal('0.90')
        return Decimal('1.00')

    def _get_seasonal_factor(self, date):
        """Calculate factor based on season."""
        peak_months = [12, 1, 7, 8]  # December, January, July, August
        shoulder_months = [3, 4, 9, 10]  # March, April, September, October
        
        if date.month in peak_months:
            return Decimal('1.30')
        elif date.month in shoulder_months:
            return Decimal('1.15')
        return Decimal('1.00')

    def _get_day_of_week_factor(self, date):
        """Calculate factor based on day of week."""
        if date.weekday() >= 5:  # Weekend
            return Decimal('1.20')
        return Decimal('1.00')

    def _get_occupancy_factor(self, category, date):
        """Calculate factor based on current occupancy."""
        current_occupancy = SeasonalDemand.objects.filter(
            category=category,
            date=date
        ).aggregate(Avg('occupancy_rate'))['occupancy_rate__avg'] or 0

        if current_occupancy > 0.9:
            return Decimal('1.40')
        elif current_occupancy > 0.7:
            return Decimal('1.20')
        elif current_occupancy < 0.3:
            return Decimal('0.85')
        return Decimal('1.00') 