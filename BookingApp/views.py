from django.shortcuts import render
from django.http import JsonResponse
from .utils import recommend_resorts
from datetime import datetime, timedelta
from django.utils import timezone
import json

def home(request):
    """Render the home page."""
    return render(request, 'home.html')

def recommend_view(request):
    """API endpoint to provide resort recommendations."""
    hotel_name = request.GET.get('hotel', '').strip()
    
    if not hotel_name:
        return JsonResponse({'error': 'Missing "hotel" parameter'}, status=400)
    
    recommendations = recommend_resorts(hotel_name)
    
    if isinstance(recommendations, str):  
        return JsonResponse({'error': recommendations}, status=404)
    
    return JsonResponse({'recommendations': recommendations.to_dict(orient='records')})

def recommend_page(request):
    """Render recommendations with visualization."""
    hotel_name = request.GET.get('hotel', '').strip()
    
    if not hotel_name:
        return render(request, 'recommend.html', {'error': 'Please enter a valid hotel name!'})

    recommendations = recommend_resorts(hotel_name)
    
    if isinstance(recommendations, str):
        return render(request, 'recommend.html', {'error': recommendations})
    
    return render(request, 'recommend.html', {
        'hotel_name': hotel_name,
        'recommendations': recommendations.to_dict(orient='records'),
    })

def dashboard(request):
    """Render the resort owner dashboard."""
    # Mock data for demonstration
    context = {
        'stats': {
            'total_bookings': 127,
            'revenue': 45850,
            'occupancy_rate': 85,
            'average_rating': 4.8
        },
        'recent_bookings': [
            {
                'id': 'BK001',
                'guest_name': 'John Doe',
                'package': 'Luxury Villa',
                'check_in': datetime.now() + timedelta(days=2),
                'status': 'Confirmed'
            }
        ],
        'popular_packages': [
            {
                'name': 'Royal Villa Experience',
                'bookings': 45,
                'revenue': 12500,
                'rating': 4.9
            }
        ]
    }
    return render(request, 'dashboard.html', context)

def manage_packages(request):
    """Handle package management."""
    if request.method == 'POST':
        # Handle package creation/update
        return JsonResponse({'status': 'success'})
    
    packages = [
        {
            'id': 1,
            'name': 'Royal Villa Experience',
            'price': 5999,
            'description': 'Luxury villa with private pool',
            'is_active': True
        }
    ]
    return render(request, 'dashboard/packages.html', {'packages': packages})

def manage_bookings(request):
    """Handle booking management."""
    bookings = [
        {
            'id': 'BK001',
            'guest_name': 'John Doe',
            'package': 'Luxury Villa',
            'check_in': datetime.now() + timedelta(days=2),
            'check_out': datetime.now() + timedelta(days=5),
            'status': 'Confirmed',
            'total_amount': 5999
        }
    ]
    return render(request, 'dashboard/bookings.html', {'bookings': bookings})

def analytics(request):
    """Show guest analytics and insights with date filtering."""
    # Get date range from request
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    # Default to last 30 days if no dates provided
    if not start_date or not end_date:
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Get property filter
    property_id = request.GET.get('property', 'all')

    # Generate analytics data based on date range
    context = generate_analytics_data(start_date, end_date, property_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(context)
    
    return render(request, 'dashboard/analytics.html', context)

def generate_analytics_data(start_date, end_date, property_id='all'):
    """Generate analytics data for the given date range."""
    # Calculate date difference
    date_diff = (end_date - start_date).days
    
    # Generate daily data points
    daily_data = []
    current_date = start_date
    
    while current_date <= end_date:
        daily_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'revenue': generate_revenue_data(current_date),
            'bookings': generate_booking_data(current_date),
            'occupancy': generate_occupancy_data(current_date)
        })
        current_date += timedelta(days=1)

    return {
        'date_range': {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d'),
            'days': date_diff
        },
        'summary': {
            'total_revenue': sum(day['revenue'] for day in daily_data),
            'total_bookings': sum(day['bookings'] for day in daily_data),
            'avg_occupancy': sum(day['occupancy'] for day in daily_data) / len(daily_data),
            'period_growth': calculate_growth(daily_data)
        },
        'daily_data': daily_data,
        'satisfaction_metrics': [
            {
                'name': 'Overall Experience',
                'icon': 'fa-star',
                'rating': 4.8,
                'reviews': 150,
                'trend': calculate_metric_trend(start_date, end_date, 'experience')
            },
            {
                'name': 'Room Quality',
                'icon': 'fa-bed',
                'rating': 4.6,
                'reviews': 120,
                'trend': calculate_metric_trend(start_date, end_date, 'room_quality')
            },
            {
                'name': 'Service',
                'icon': 'fa-concierge-bell',
                'rating': 4.9,
                'reviews': 140,
                'trend': calculate_metric_trend(start_date, end_date, 'service')
            },
            {
                'name': 'Cleanliness',
                'icon': 'fa-broom',
                'rating': 4.7,
                'reviews': 130,
                'trend': calculate_metric_trend(start_date, end_date, 'cleanliness')
            }
        ],
        'predictions': generate_predictions(end_date),
        'property_data': get_property_data(property_id)
    }

def calculate_growth(data):
    """Calculate period-over-period growth."""
    if len(data) < 2:
        return 0
    
    first_half = sum(day['revenue'] for day in data[:len(data)//2])
    second_half = sum(day['revenue'] for day in data[len(data)//2:])
    
    if first_half == 0:
        return 100
    return ((second_half - first_half) / first_half) * 100

# Mock data generation functions
def generate_revenue_data(date):
    """Generate realistic revenue data based on date patterns."""
    base = 5000
    # Weekend boost
    if date.weekday() >= 5:
        base *= 1.5
    # Season factors
    month = date.month
    if month in [12, 1, 7, 8]:  # Peak seasons
        base *= 1.3
    return round(base * (0.9 + (date.day % 10) / 10))

def generate_booking_data(date):
    """Generate realistic booking numbers."""
    base = 15
    if date.weekday() >= 5:
        base *= 1.4
    return round(base * (0.8 + (date.day % 8) / 10))

def generate_occupancy_data(date):
    """Generate realistic occupancy rates."""
    base = 75
    if date.weekday() >= 5:
        base += 15
    return min(100, round(base * (0.9 + (date.day % 10) / 20)))

def calculate_metric_trend(start_date, end_date, metric):
    """Calculate the trend for a given metric."""
    # Implementation of calculate_metric_trend function
    pass

def get_property_data(property_id):
    """Retrieve property-specific data."""
    # Implementation of get_property_data function
    pass

def generate_predictions(end_date):
    """Generate predictions for the given date."""
    # Implementation of generate_predictions function
    pass

def reviews(request):
    """Handle resort reviews."""
    reviews_data = [
        {
            'guest_name': 'Alice Smith',
            'rating': 5,
            'comment': 'Excellent service and beautiful location!',
            'date': datetime.now() - timedelta(days=2)
        }
    ]
    return render(request, 'dashboard/reviews.html', {'reviews': reviews_data})
