from flask import Flask
from funding_app import funding_blueprint
from streaming_app import streaming_blueprint

app = Flask(__name__)

# 각각의 블루프린트 등록
app.register_blueprint(funding_blueprint, url_prefix='/funding')
app.register_blueprint(streaming_blueprint, url_prefix='/streaming')

if __name__ == '__main__':
    app.run(debug=True)
