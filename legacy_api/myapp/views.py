from django.shortcuts import render
from .models import Movie

def home(request):
	items = Movie.objects.all()
	return render(request, 'myapp/home.html', {'items': items})
# Create your views here.

# Create your views here.
