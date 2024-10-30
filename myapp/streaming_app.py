from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
import os
import uuid
from datetime import datetime

# 블루프린트 생성
streaming_blueprint = Blueprint('streaming', __name__)

# MongoDB 설정
client = MongoClient('mongodb://localhost:27017/')
db = client['movie_project_db']
streaming_projects = db['streaming_projects']

# 업로드된 영화 저장 경로
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'movies')

# 스트리밍 영화 업로드 페이지
@streaming_blueprint.route('/upload', methods=['GET', 'POST'])
def upload_streaming_movie():
    if request.method == 'POST':
        # 폼 데이터 가져오기
        title = request.form['title']
        genre = request.form.getlist('genre')
        time = int(request.form['time'])
        summary = request.form['summary']
        actors = request.form['actors']
        release_date = request.form['release_date']

        # 로그인된 사용자의 ID 가져오기 (세션에서 가정)
        creator_id = session.get('user_id')  # 로그인한 사용자의 ID

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
                "summary": summary,
                "actors": actors,
                "creator_id": creator_id,
                "release_date": release_date,
                "streaming_url": filename,
                "views": 0,
                "payment_history": [],
                "viewer": []
            }

            streaming_projects.insert_one(project)
            return redirect(url_for('streaming.show_streaming_movie', project_id=project['_id']))

    return render_template('upload_streaming.html')

# 스트리밍 영화 상세 페이지
@streaming_blueprint.route('/<project_id>')
def show_streaming_movie(project_id):
    project = streaming_projects.find_one({"_id": project_id})
    if project:
        streaming_projects.update_one(
            {"_id": project_id},
            {"$inc": {"views": 1}}  # 조회수 증가
        )
        return render_template('streaming_detail.html', project=project)
    return jsonify({"error": "Project not found"}), 404
