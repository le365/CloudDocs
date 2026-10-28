from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from azure.storage.blob import BlobServiceClient
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Cấu hình kết nối PostgreSQL (thay đổi thông tin username, password, localhost, port, tên db của nhóm)

import os

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/clouddocs_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Cấu hình kết nối Azure Blob Storage (thay chuỗi kết nối thực tế từ Azure Portal của nhóm)
AZURE_CONNECTION_STRING = "your_azure_blob_connection_string"
CONTAINER_NAME = "clouddocs-container"
blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)

# Model lưu thông tin file trong PostgreSQL
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    blob_url = db.Column(db.String(512), nullable=False)

@app.route('/')
def index():
    docs = Document.query.all()
    return render_template('index.html', docs=docs)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('Không tìm thấy file tải lên!')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('Chưa chọn file nào!')
        return redirect(request.url)
    
    if file:
        filename = file.filename
        
        # 1. Tải file lên Azure Blob Storage
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=filename)
        blob_client.upload_blob(file.stream, overwrite=True)
        blob_url = blob_client.url
        
        # 2. Lưu thông tin metadata vào PostgreSQL
        new_doc = Document(filename=filename, blob_url=blob_url)
        db.session.add(new_doc)
        db.session.commit()
        
        flash('Tải tài liệu lên thành công!')
        return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)