# tasks.py

from celery import shared_task
from datetime import datetime, timedelta
from django.core.mail import send_mail
from .amazon_price_scrap import AmazonScraper
from .flipkart_price_scrap import FlipkartScraper
from wishlist.models import Product, PriceCheckTracker, Wishlist
from login.models import CustomUser
from django.utils import timezone

@shared_task
def scrape_amazon_task(keyword, page):
    scraper = AmazonScraper()
    return scraper.scrape_page(keyword, page)

@shared_task
def scrape_flipkart_task(keyword, page):
    scraper = FlipkartScraper()
    return scraper.scrape_page(keyword, page)

@shared_task
def scrape_amazon_detail_task(url):
    scraper = AmazonScraper()
    return scraper.extract_product_details(url)

@shared_task
def scrape_flipkart_detail_task(url):
    scraper = FlipkartScraper()
    return scraper.extract_product_details(url)

@shared_task
def update_product_prices():
    print("Task starting")
    tracker, created = PriceCheckTracker.objects.get_or_create(task_name='update_product_prices')

    # Check if the last run was within the last 24 hours
    if tracker.last_run and (timezone.now() - tracker.last_run).days < 1:
        print("Skipping price-check task since it ran within the last 24 hours.")
        return

    # Perform the price-check logic for each product in the database
    products = Product.objects.all()
    for product in products:
        try:
            amazon_scraper = AmazonScraper()
            flipkart_scraper = FlipkartScraper()

            # Update Amazon price
            new_amazon_price = amazon_scraper.extract_product_details(product.amazon_url)['price']
            amazon_price_changed = product.amazon_price != new_amazon_price
            product.amazon_price = new_amazon_price

            # Update Flipkart price
            data = flipkart_scraper.extract_product_details(product.flipkart_url)
            new_flipkart_price = data["price"]
            flipkart_price_changed = product.flipkart_price != new_flipkart_price
            product.flipkart_price = new_flipkart_price

            product.save()

            # Send an email notification to users if the price has changed
            if amazon_price_changed or flipkart_price_changed:
                notify_users_about_price_change(product, new_amazon_price, new_flipkart_price)
            
            print(product +"price checked")

        except Exception as e:
            # Log the error but continue with the next product
            print(f"Error processing product {product.id}: {e}")

    # Update the last run time after successfully updating all prices
    tracker.last_run = timezone.now()
    tracker.save()
    print("Product prices updated successfully.")


def notify_users_about_price_change(product, new_amazon_price, new_flipkart_price):
    """
    Sends an email notification to users if the price of a product has changed.
    """
    # Get all users who have this product in their wishlist
    wishlists = Wishlist.objects.filter(products=product)
    recipients = set()

    for wishlist in wishlists:
        recipients.add(wishlist.user.email)

    if recipients:
        send_mail(
            subject='Price Change Notification',
            message=f'The price of {product.amazon_name} has changed.\n\n'
                    f'Amazon Price: {new_amazon_price}\n'
                    f'Flipkart Price: {new_flipkart_price}\n\n'
                    f'Check the updated prices on our website!',
            from_email='kavijeevanraj@gmail.com',
            recipient_list=list(recipients),
            fail_silently=False,
        )
        print(f"Email sent to users: {', '.join(recipients)}")
