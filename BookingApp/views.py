from django.shortcuts import render
from django.http import JsonResponse
from .utils import recommend_resorts

def home(request):
    """Render the home page."""
    return render(request, 'home.html')

def recommend_view(request):
    """API endpoint to provide resort recommendations."""
    hotel_name = request.GET.get('hotel', '').strip()
    
    if not hotel_name:
        return JsonResponse({'error': 'Missing "hotel" parameter. Example: /recommend/?hotel=Crowne Plaza Kochi'}, status=400)
    
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
