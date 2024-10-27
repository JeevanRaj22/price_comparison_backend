# myapp/decorators.py
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect

def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            # If not authenticated, return error or redirect to login
            return JsonResponse({'error': 'Authentication required'}, status=401)
            # or use this to redirect:
            # return redirect('/login/')
        return view_func(request, *args, **kwargs)
    return wrapper
