from django.shortcuts import render
from backend.settings import BASE_DIR


# Create your views here.
def index(request):
    return render(request, BASE_DIR / "backend" / "templates" / "base.html")
