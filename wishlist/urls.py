from django.urls import path
from .views import add_to_wishlist, retrieve_wishlist, remove_from_wishlist

urlpatterns = [
    path('add/', add_to_wishlist, name='add_to_wishlist'),
    path('<int:user_id>/', retrieve_wishlist, name='retrieve_wishlist'),
    path('remove/', remove_from_wishlist, name='remove_from_wishlist'),
]
