# streaming/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import StreamingMovie
from streaming.forms import StreamingMovieForm

@login_required
def upload_streaming_movie(request):
    if request.method == 'POST':
        form = StreamingMovieForm(request.POST, request.FILES)
        if form.is_valid():
            movie = form.save(commit=False)
            movie.creator = request.user  # 현재 로그인한 사용자를 창작자로 설정
            movie.save()
            return redirect('streaming:streaming_detail', movie_id=movie.id)
    else:
        form = StreamingMovieForm()
    return render(request, 'upload_streaming.html', {'form': form})

def streaming_detail(request, movie_id):
    movie = get_object_or_404(StreamingMovie, id=movie_id)
    movie.views += 1  # 조회수 증가
    movie.save()
    return render(request, 'streaming_detail.html', {'movie': movie})
