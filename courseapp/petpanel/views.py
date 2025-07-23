from django.shortcuts import render

# Create your views here.
# petpanel/views.py

from django.shortcuts import render

def dashboard(request):
    return render(request, 'petpanel/dashboard.html')  # Şimdilik basit bir şablon
