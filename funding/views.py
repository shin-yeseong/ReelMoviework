# funding/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import FundingMovie
from .forms import FundingMovieForm

# @login_required
def upload_funding_movie(request):
    if request.method == 'POST':
        form = FundingMovieForm(request.POST)
        if form.is_valid():
            movie = form.save(commit=False)
            movie.creator = request.user  # 로그인한 사용자를 창작자로 설정
            movie.save()
            return redirect('funding:funding_detail', movie_id=movie.id)
    else:
        form = FundingMovieForm()
    return render(request, 'upload_funding.html', {'form': form})

def funding_detail(request, movie_id):
    movie = get_object_or_404(FundingMovie, id=movie_id)
    return render(request, 'funding_detail.html', {'movie': movie})

