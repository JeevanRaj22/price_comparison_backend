from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.sessions.models import Session
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import CustomUser
from .decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json

# User Registration View
@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        print(json.loads(request.body))

        if CustomUser.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)

        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already exists'}, status=400)

        # Create new user and hash the password
        new_user = CustomUser(username=username, email=email, password=make_password(password))
        new_user.save()

        return JsonResponse({'message': 'User registered successfully'})

    return HttpResponse(status=405)  # Method Not Allowed for non-POST requests


# User Login View
@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'Invalid username or password'}, status=400)

        # Verify password
        if check_password(password, user.password):

            # Set user session
            request.session.create()
            request.session['user_id'] = user.user_id
            request.session['username'] = user.username
            print(f"User logged in with session: {request.session.items()}")
            return JsonResponse({'message': 'Login successful', 'username': user.username,'user_id':user.user_id})

        return JsonResponse({'error': 'Invalid username or password'}, status=400)

    return HttpResponse(status=405)  # Method Not Allowed for non-POST requests


# User Logout View
@csrf_exempt
def logout(request):
    print(f"Session Key: {request.session.items()}")
    if 'user_id' in request.session:
        # Clear the session
        request.session.flush()
        return JsonResponse({'message': 'Logged out successfully'})

    return JsonResponse({'error': 'No user is logged in'}, status=400)


# A protected view example (requires login)
@login_required
def some_protected_view(request):
    return JsonResponse({'message': 'This is a protected view, only accessible to logged-in users!'})


# Example home page
def home(request):
    return JsonResponse({'message': 'Welcome to the home page!'})

# Set a test session view
@csrf_exempt
def set_session(request):
    request.session['test_key'] = 'test_value'
    return JsonResponse({'message': 'Session set'})

# Check session view
@csrf_exempt
def check_session(request):
    return JsonResponse({'session_data': list(request.session.items())})



@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'csrfToken': request.META.get('CSRF_COOKIE')})


