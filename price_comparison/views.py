# views.py

from django.http import JsonResponse
from .tasks import scrape_amazon_task, scrape_flipkart_task,scrape_amazon_detail_task, scrape_flipkart_detail_task
from celery.result import AsyncResult
from .match_products import find_matching_products_first_five_words
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def start_scraping_view(request):
    """
    Starts scraping for the first page.
    """
    keyword = request.GET.get('q')
    if not keyword:
        return JsonResponse({'error': 'Keyword parameter is missing'}, status=400)

    # Start scraping page 1 for both Amazon and Flipkart
    amazon_task = scrape_amazon_task.apply_async(args=[keyword, 1], queue='amazon_queue')
    flipkart_task = scrape_flipkart_task.apply_async(args=[keyword, 1], queue='flipkart_queue')
    
    return JsonResponse({
        'amazon_task_id': amazon_task.id,
        'flipkart_task_id': flipkart_task.id,
        'current_page': 1,
        'status': "Scraping started for page 1"
    })


@csrf_exempt
def load_more_view(request):
    """
    Loads the next page based on the current_page provided.
    """
    keyword = request.GET.get('q')
    current_page = request.GET.get('current_page')

    if not keyword or not current_page:
        return JsonResponse({'error': 'Keyword and current_page parameters are required'}, status=400)

    try:
        current_page = int(current_page)
    except ValueError:
        return JsonResponse({'error': 'current_page must be an integer'}, status=400)

    next_page = current_page + 1

    # Start scraping the next page for both Amazon and Flipkart
    amazon_task = scrape_amazon_task.apply_async(args=[keyword, next_page], queue='amazon_queue')
    flipkart_task = scrape_flipkart_task.apply_async(args=[keyword, next_page], queue='flipkart_queue')
    
    return JsonResponse({
        'amazon_task_id': amazon_task.id,
        'flipkart_task_id': flipkart_task.id,
        'current_page': next_page,
        'status': f"Scraping started for page {next_page}"
    })


def check_status_view(request):
    """
    Checks the status of the scraping tasks and returns the results if completed.
    """
    amazon_task_id = request.GET.get('amazon_task_id', '')
    flipkart_task_id = request.GET.get('flipkart_task_id', '')

    if not amazon_task_id or not flipkart_task_id:
        return JsonResponse({'error': 'Task IDs are required'}, status=400)

    amazon_result = AsyncResult(amazon_task_id)
    flipkart_result = AsyncResult(flipkart_task_id)

    if amazon_result.ready() and flipkart_result.ready():
        if amazon_result.successful() and flipkart_result.successful():
            amazon_products = amazon_result.result
            flipkart_products = flipkart_result.result

            matched_products,amazon_data,flipkart_data = find_matching_products_first_five_words(
                amazon_products, flipkart_products, threshold=0.8
            )
            return JsonResponse({
                "status": "completed",
                "matched_products": matched_products,
                "amazon_data": amazon_data,
                "flipkart_data": flipkart_data
            })
        else:
            # Identify which task failed
            failed_tasks = {}
            if not amazon_result.successful():
                failed_tasks['amazon_status'] = amazon_result.status
            if not flipkart_result.successful():
                failed_tasks['flipkart_status'] = flipkart_result.status

            return JsonResponse({
                "status": "failed",
                **failed_tasks
            }, status=500)

    return JsonResponse({
        "status": "pending",
        'amazon_status': amazon_result.status,
        'flipkart_status': flipkart_result.status
    })

@csrf_exempt
def start_scraping_detail_view(request):
    if request.method == 'POST':
        try:
            # Parse the request body to get the JSON data
            data = json.loads(request.body)
            amazon_url = data.get('amazon_url')
            flipkart_url = data.get('flipkart_url')

            if not amazon_url or not flipkart_url:
                return JsonResponse({'error': 'URL parameter is missing'}, status=400)

            amazon_task = scrape_amazon_detail_task.apply_async(args=[amazon_url], queue='amazon_queue')
            flipkart_task = scrape_flipkart_detail_task.apply_async(args=[flipkart_url], queue='flipkart_queue')

            return JsonResponse({
                'amazon_task_id': amazon_task.id,
                'flipkart_task_id': flipkart_task.id,
                'status': "Scraping started"
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def check_status_detail_view(request):
    """
    Checks the status of the scraping tasks and returns the results if completed.
    """
    amazon_task_id = request.GET.get('amazon_task_id', '')
    flipkart_task_id = request.GET.get('flipkart_task_id', '')

    if not amazon_task_id or not flipkart_task_id:
        return JsonResponse({'error': 'Task IDs are required'}, status=400)

    amazon_result = AsyncResult(amazon_task_id)
    flipkart_result = AsyncResult(flipkart_task_id)

    if amazon_result.ready() and flipkart_result.ready():
        if amazon_result.successful() and flipkart_result.successful():
            amazon_products = amazon_result.result
            flipkart_products = flipkart_result.result
            return JsonResponse({
                "status": "completed",
                "amazon_data": amazon_products,
                "flipkart_data": flipkart_products
            })
        else:
            # Identify which task failed
            failed_tasks = {}
            if not amazon_result.successful():
                failed_tasks['amazon_status'] = amazon_result.status
            if not flipkart_result.successful():
                failed_tasks['flipkart_status'] = flipkart_result.status

            return JsonResponse({
                "status": "failed",
                **failed_tasks
            }, status=500)

    return JsonResponse({
        "status": "pending",
        'amazon_status': amazon_result.status,
        'flipkart_status': flipkart_result.status
    })

