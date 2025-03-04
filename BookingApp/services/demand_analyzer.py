from datetime import datetime, timedelta
import pandas as pd
from ..models import SeasonalDemand, Room, Package, Venue
from django.db.models import Avg, Count
from django.utils import timezone

class DemandAnalyzer:
    def __init__(self):
        self.categories = ['room', 'package', 'venue']

    def analyze_historical_demand(self, category, start_date=None, end_date=None):
        """Analyze historical demand patterns."""
        if not start_date:
            start_date = timezone.now() - timedelta(days=365)
        if not end_date:
            end_date = timezone.now()

        data = SeasonalDemand.objects.filter(
            category=category,
            date__range=[start_date, end_date]
        )

        analysis = {
            'total_bookings': data.aggregate(Count('bookings_count'))['bookings_count__count'],
            'avg_occupancy': data.aggregate(Avg('occupancy_rate'))['occupancy_rate__avg'],
            'peak_months': self._get_peak_months(data),
            'weekday_distribution': self._get_weekday_distribution(data),
            'revenue_trends': self._get_revenue_trends(data)
        }

        return analysis

    def predict_future_demand(self, category, prediction_days=30):
        """Predict demand for the next specified days."""
        predictions = []
        start_date = timezone.now().date()

        for i in range(prediction_days):
            future_date = start_date + timedelta(days=i)
            
            # Get current occupancy rate
            occupancy_rate = self._get_current_occupancy(category)
            
            # Predict demand
            predicted_demand = SeasonalDemand.predict_demand(
                category, 
                future_date, 
                occupancy_rate
            )
            
            predictions.append({
                'date': future_date,
                'predicted_demand': predicted_demand,
                'confidence_score': self._calculate_confidence_score(category, future_date)
            })

        return predictions

    def get_recommendations(self, category):
        """Generate pricing and capacity recommendations."""
        current_demand = self.analyze_historical_demand(category)
        future_demand = self.predict_future_demand(category)
        
        recommendations = {
            'pricing': self._generate_pricing_recommendations(category, current_demand, future_demand),
            'capacity': self._generate_capacity_recommendations(category, current_demand, future_demand),
            'marketing': self._generate_marketing_recommendations(category, current_demand, future_demand)
        }
        
        return recommendations

    def _get_peak_months(self, data):
        """Identify peak demand months."""
        monthly_data = data.values('date__month').annotate(
            avg_bookings=Avg('bookings_count')
        ).order_by('-avg_bookings')
        return list(monthly_data)

    def _get_weekday_distribution(self, data):
        """Analyze demand distribution across weekdays."""
        return data.values('date__week_day').annotate(
            avg_bookings=Avg('bookings_count')
        ).order_by('date__week_day')

    def _get_revenue_trends(self, data):
        """Analyze revenue trends."""
        return data.values('date__month').annotate(
            avg_revenue=Avg('revenue')
        ).order_by('date__month')

    def _get_current_occupancy(self, category):
        """Get current occupancy rate for the category."""
        if category == 'room':
            return Room.objects.filter(status='occupied').count() / Room.objects.count()
        elif category == 'venue':
            return Venue.objects.filter(status='reserved').count() / Venue.objects.count()
        return 0.0

    def _calculate_confidence_score(self, category, date):
        """Calculate prediction confidence score."""
        # Implement confidence calculation logic
        return 0.85  # Placeholder

    def _generate_pricing_recommendations(self, category, current_demand, future_demand):
        """Generate pricing recommendations based on demand analysis."""
        recommendations = []
        
        # Analyze demand patterns
        high_demand_dates = [p for p in future_demand if p['predicted_demand'] > current_demand['total_bookings']]
        
        if high_demand_dates:
            recommendations.append({
                'type': 'price_increase',
                'message': 'Consider increasing prices for the following dates due to high predicted demand:',
                'dates': [d['date'] for d in high_demand_dates],
                'suggested_increase': '10-15%'
            })
            
        return recommendations

    def _generate_capacity_recommendations(self, category, current_demand, future_demand):
        """Generate capacity management recommendations."""
        recommendations = []
        
        # Analyze capacity utilization
        if current_demand['avg_occupancy'] > 0.8:
            recommendations.append({
                'type': 'capacity_warning',
                'message': 'High occupancy rates detected. Consider capacity expansion or optimization.'
            })
            
        return recommendations

    def _generate_marketing_recommendations(self, category, current_demand, future_demand):
        """Generate marketing recommendations."""
        recommendations = []
        
        # Analyze low demand periods
        low_demand_months = [m for m in current_demand['peak_months'] if m['avg_bookings'] < 50]
        
        if low_demand_months:
            recommendations.append({
                'type': 'marketing_campaign',
                'message': 'Consider running promotional campaigns during low-demand months:',
                'months': low_demand_months
            })
            
        return recommendations

    def get_dynamic_pricing(self, category, item_id, date_range=30):
        """Get dynamic pricing recommendations for a date range."""
        from .pricing_service import DynamicPricingService
        
        pricing_service = DynamicPricingService()
        start_date = timezone.now().date()
        pricing_data = []
        
        for i in range(date_range):
            future_date = start_date + timedelta(days=i)
            multiplier = pricing_service.calculate_price_multiplier(
                category, item_id, future_date
            )
            
            pricing_data.append({
                'date': future_date,
                'multiplier': multiplier,
                'factors': {
                    'demand': pricing_service._get_demand_factor(category, item_id, future_date),
                    'seasonal': pricing_service._get_seasonal_factor(future_date),
                    'day_of_week': pricing_service._get_day_of_week_factor(future_date),
                    'occupancy': pricing_service._get_occupancy_factor(category, future_date)
                }
            })
        
        return pricing_data 