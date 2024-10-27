# urls.py
from django.urls import path
from .views import start_scraping_view, check_status_view, load_more_view, start_scraping_detail_view, check_status_detail_view

urlpatterns = [
    path('start-scrape/', start_scraping_view, name='start_scraping'),
    path('load-more/', load_more_view, name='load_more'),
    path('check-status/', check_status_view, name='check_status'),
    path('start-scrape-detail/', start_scraping_detail_view, name='start_scraping_detail'),
    path('check-status-detail/', check_status_detail_view, name='check_status_detail'),
]
