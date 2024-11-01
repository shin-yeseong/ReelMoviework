# funding/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import FundingMovie
from .forms import FundingMovieForm
import uuid
from datetime import datetime
from mongodbconnect import settings

# @login_required
def upload_funding_movie(request):
    if request.method == 'POST':
        form = FundingMovieForm(request.POST)
        if form.is_valid():
            funding_data = {
                "_id": str(uuid.uuid4()),  # 고유 ID 생성
                "title": form.cleaned_data['title'],
                "genre": form.cleaned_data['genre'],
                "time": form.cleaned_data['time'],
                "intention": form.cleaned_data['intention'],
                "summary": form.cleaned_data['summary'],
                "making_description": form.cleaned_data['making_description'],
                "creator_id": str(request.user.id),  # 로그인한 사용자의 ID 저장
                "target_funding": form.cleaned_data['target_funding'],
                "funding_description": form.cleaned_data['funding_description'],
                "funding_deadline": form.cleaned_data['funding_deadline'],
                "create_date": datetime.now(),
                "status": "funding",
                "backers": [],
                "backers_funding": [],
                "total_funding_amount": 0,
                "payment_history": []
            }

            # MongoDB에 저장
            settings.mongo_db.funding_movies.insert_one(funding_data)
            return redirect('funding:funding_movie_page')
    else:
        form = FundingMovieForm()
    return render(request, 'upload_funding.html', {'form': form})

def funding_detail(request, movie_id):
    movie = get_object_or_404(FundingMovie, id=movie_id)
    return render(request, 'funding_detail.html', {'movie': movie})

