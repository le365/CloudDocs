from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

# 1. Khởi tạo Flask app PHẢI ĐẶT Ở ĐẦU TIÊN
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# 2. Cấu hình Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/clouddocs_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Thư mục lưu file tạm trên server
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 3. Model lưu thông tin file
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    blob_url = db.Column(db.String(512), nullable=False)

# Tạo bảng tự động
with app.app_context():
    db.create_all()

# 4. Các Route của ứng dụng
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
        
        # Lưu thông tin vào database PostgreSQL
        new_doc = Document(filename=filename, blob_url=file_path)
        db.session.add(new_doc)
        db.session.commit()
        
        flash('Tải tài liệu lên thành công!')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)