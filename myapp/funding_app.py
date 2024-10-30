from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
import os
import uuid
from datetime import datetime

funding_blueprint = Blueprint('funding', __name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['movie_project_db']
funding_projects = db['funding_projects']

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'movies')

@funding_blueprint.route('/upload', methods=['GET', 'POST'])
def upload_funding_movie():
    if request.method == 'POST':
        # 폼 데이터 가져오기
        title = request.form['title']
        genre = request.form.getlist('genre')
        time = int(request.form['time'])
        intention = request.form['intention']
        summary = request.form['summary']
        making_description = request.form['making_description']
        target_funding = int(request.form['target_funding'])
        funding_description = request.form['funding_description']
        funding_deadline = request.form['funding_deadline']
        create_date = datetime.now().strftime('%Y-%m-%d')

        # 펀딩 옵션 가져오기
        funding_options = []
        for i in range(len(request.form.getlist('funding_amount'))):
            amount = int(request.form.getlist('funding_amount')[i])
            benefit = request.form.getlist('funding_benefit')[i]
            funding_options.append({"amount": amount, "benefit": benefit})

        # 영화 파일 저장
        file = request.files['movie_file']
        if file:
            filename = f"{uuid.uuid4()}.mp4"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # MongoDB에 영화 정보 저장
            project = {
                "_id": str(uuid.uuid4()),
                "title": title,
                "genre": genre,
                "time": time,
                "intention": intention,
                "summary": summary,
                "making_description": making_description,
                "target_funding": target_funding,
                "funding_description": funding_description,
                "funding_deadline": funding_deadline,
                "create_date": create_date,
                "status": "funding",
                "funding_options": funding_options,
                "total_funding_amount": 0,
                "streaming_url": filename
            }

            # MongoDB에 저장
            funding_projects.insert_one(project)

            # 업로드 완료 후 소개 페이지로 리디렉션
            return redirect(url_for('funding.show_funding_movie', project_id=project['_id']))

    return render_template('upload_funding.html')

@funding_blueprint.route('/<project_id>')
def show_funding_movie(project_id):
    project = funding_projects.find_one({"_id": project_id})
    if project:
        return render_template('funding_detail.html', project=project)
    return jsonify({"error": "Project not found"}), 404
