from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='uploads')
app.config['SECRET_KEY'] = 'your_secret_key'

# Cấu hình Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/clouddocs_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    blob_url = db.Column(db.String(512), nullable=False)

with app.app_context():
    db.create_all()

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
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Lưu đường dẫn tương đối để hiển thị link đúng
        new_doc = Document(filename=filename, blob_url=f'/uploads/{filename}')
        db.session.add(new_doc)
        db.session.commit()
        
        flash('Tải tài liệu lên thành công!')
        return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)