from flask import Flask, render_template, request, send_from_directory, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

# Flask 앱과 MongoDB 클라이언트 설정
app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['movie_project_db']
streaming_projects = db['streaming_projects']

# 영화 파일을 제공할 폴더 경로 설정
MOVIE_FOLDER = os.path.join(os.getcwd(), 'movies')

# 스트리밍 프로젝트 조회 및 HTML 렌더링
@app.route('/stream/<project_id>', methods=['GET'])
def stream_project(project_id):
    project = streaming_projects.find_one({"_id": ObjectId(project_id)})
    if project:
        return render_template('player.html', project=project)
    return jsonify({"error": "Project not found"}), 404

# 영화 파일 스트리밍
@app.route('/movies/<filename>')
def stream_movie(filename):
    return send_from_directory(MOVIE_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
