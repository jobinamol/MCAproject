from django.urls import path
from .views import home, recommend_view, recommend_page

urlpatterns = [
    path('', home, name='home'),
    path('recommend/', recommend_view, name='recommend_api'),
    path('recommend/results/', recommend_page, name='recommend_page'),
]
