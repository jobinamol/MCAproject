from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .utils import recommend_resorts
from datetime import datetime, timedelta

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

@login_required
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
            },
            # Add more bookings...
        ],
        'popular_packages': [
            {
                'name': 'Royal Villa Experience',
                'bookings': 45,
                'revenue': 12500,
                'rating': 4.9
            },
            # Add more packages...
        ]
    }
    return render(request, 'dashboard.html', context)

@login_required
def manage_packages(request):
    """Handle package management."""
    if request.method == 'POST':
        # Handle package creation/update
        return JsonResponse({'status': 'success'})
    
    # Get all packages for display
    packages = [
        {
            'id': 1,
            'name': 'Royal Villa Experience',
            'price': 5999,
            'description': 'Luxury villa with private pool',
            'is_active': True
        },
        # Add more packages...
    ]
    return render(request, 'dashboard/packages.html', {'packages': packages})

@login_required
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
        },
        # Add more bookings...
    ]
    return render(request, 'dashboard/bookings.html', {'bookings': bookings})

@login_required
def analytics(request):
    """Show analytics and insights."""
    analytics_data = {
        'revenue_chart': {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            'data': [4500, 5200, 4800, 5900, 6100]
        },
        'occupancy_rate': {
            'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'data': [75, 82, 78, 85, 90, 95, 88]
        }
    }
    return render(request, 'dashboard/analytics.html', {'analytics': analytics_data})

@login_required
def reviews(request):
    """Handle resort reviews."""
    reviews_data = [
        {
            'guest_name': 'Alice Smith',
            'rating': 5,
            'comment': 'Excellent service and beautiful location!',
            'date': datetime.now() - timedelta(days=2)
        },
        # Add more reviews...
    ]
    return render(request, 'dashboard/reviews.html', {'reviews': reviews_data})
