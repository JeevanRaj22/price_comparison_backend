from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Wishlist, Product
from login.models import CustomUser
import json

# Create your views here.
@csrf_exempt
def add_to_wishlist(request):
    if request.method == 'POST':
        try:
            # Parse JSON data
            data = json.loads(request.body)
            user_id = data.get('user_id')
            amazon_name = data.get('amazon_name')
            flipkart_name = data.get('flipkart_name')
            image = data.get('image')
            amazon_url = data.get('amazon_url')
            flipkart_url = data.get('flipkart_url')
            amazon_price = data.get('amazon_price')
            flipkart_price = data.get('flipkart_price')
            ram = data.get('ram')  # New RAM field
            rom = data.get('rom')  # New ROM field
            color = data.get('color')  # New Color field

            # Check if product already exists
            product, created = Product.objects.get_or_create(
                amazon_name=amazon_name,
                flipkart_name=flipkart_name,
                ram=ram,
                rom= rom,
                color=color,  
                defaults={
                    'image': image,
                    'amazon_url': amazon_url,
                    'flipkart_url': flipkart_url,
                    'amazon_price': amazon_price,
                    'flipkart_price': flipkart_price,
                }
            )

            if not created:
                # If product existed, update its price and specs
                product.amazon_price = amazon_price
                product.flipkart_price = flipkart_price
                product.ram = ram  # Update RAM
                product.rom = rom  # Update ROM
                product.color = color  # Update Color
                product.save()

            # Get user instance
            user = get_object_or_404(CustomUser, pk=user_id)

            # Get or create a wishlist for the user
            wishlist, created = Wishlist.objects.get_or_create(user=user)

            # Add product to the wishlist
            wishlist.products.add(product)

            return JsonResponse({'message': 'Product added to wishlist successfully!'}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


def retrieve_wishlist(request, user_id):
    try:
        # Get or create the wishlist for the user
        wishlist, created = Wishlist.objects.get_or_create(user_id=user_id)
        
        # If the wishlist is newly created, return an empty response
        if created:
            return JsonResponse({'wishlist': []}, status=200)

        # Get the products in the wishlist
        products = wishlist.products.all()

        # Serialize the product details
        product_list = [{
            'product_id': product.id,
            'amazon_name': product.amazon_name,
            'flipkart_name': product.flipkart_name,
            'image': product.image,
            'amazon_url': product.amazon_url,
            'flipkart_url': product.flipkart_url,
            'amazon_price': product.amazon_price,
            'flipkart_price': product.flipkart_price,
            'ram': product.ram,
            'rom': product.rom,
            'color': product.color
        } for product in products]

        return JsonResponse({'wishlist': product_list}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)



@csrf_exempt
def remove_from_wishlist(request):
    if request.method == 'DELETE':
        try:
            # Parse JSON data
            data = json.loads(request.body)
            user_id = data.get('user_id')
            product_id = data.get('product_id')

            # Get the wishlist for the user
            wishlist = get_object_or_404(Wishlist, user_id=user_id)

            # Get the product and remove it from the wishlist
            product = get_object_or_404(Product, pk=product_id)
            wishlist.products.remove(product)

            return JsonResponse({'message': 'Product removed from wishlist successfully!'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


