from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .forms import UserRegisterForm, UserUpdateForm
from django.shortcuts import render,redirect
from django.contrib.auth import login,authenticate
from django.contrib.auth.decorators import login_required
from movies.models import Movie , Booking

def home(request):
    movies = Movie.objects.all()
    latest_movies = Movie.objects.filter(release_year__gte=2024).order_by('-release_year', '-rating')[:8]
    telugu_movies = Movie.objects.filter(language='Telugu', release_year__gte=2024).order_by('-rating', '-release_year')[:8]
    hindi_movies = Movie.objects.filter(language='Hindi', release_year__gte=2024).order_by('-rating', '-release_year')[:8]
    english_movies = Movie.objects.filter(language='English', release_year__gte=2024).order_by('-rating', '-release_year')[:8]
    animation_movies = Movie.objects.filter(genre='Animation', release_year__gte=2024).order_by('-rating', '-release_year')[:8]
    kids_movies = Movie.objects.filter(genre__in=['Animation', 'Family'], release_year__gte=2024).order_by('-rating', '-release_year')[:8]
    return render(
        request,
        'home.html',
        {
            'movies': movies,
            'latest_movies': latest_movies,
            'telugu_movies': telugu_movies,
            'hindi_movies': hindi_movies,
            'english_movies': english_movies,
            'animation_movies': animation_movies,
            'kids_movies': kids_movies,
        }
    )
def register(request):
    if request.method == 'POST':
        form=UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data.get('username')
            password=form.cleaned_data.get('password1')
            user=authenticate(username=username,password=password)
            login(request,user)
            return redirect('profile')
    else:
        form=UserRegisterForm()
    return render(request,'users/register.html',{'form':form})

def login_view(request):
    if request.method == 'POST':
        form=AuthenticationForm(request,data=request.POST)
        if form.is_valid():
            user=form.get_user()
            login(request,user)
            return redirect('/')
    else:
        form=AuthenticationForm()
    return render(request,'users/login.html',{'form':form})

@login_required
def profile(request):
    bookings= Booking.objects.filter(user=request.user)
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)

    return render(request, 'users/profile.html', {'u_form': u_form,'bookings':bookings})

@login_required
def reset_password(request):
    if request.method == 'POST':
        form=PasswordChangeForm(user=request.user,data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form=PasswordChangeForm(user=request.user)
    return render(request,'users/reset_password.html',{'form':form})