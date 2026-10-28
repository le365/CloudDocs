from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Cấu hình kết nối PostgreSQL (tự động nhận từ Render hoặc dùng mặc định khi chạy local)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/clouddocs_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model lưu thông tin file trong PostgreSQL
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
        filename = file.filename
        
        # Lưu thông tin tạm thời hoặc xử lý file tại đây nếu cần
        # (Đã lược bỏ phần Azure Blob Storage theo yêu cầu)
        
        flash('Tải tài liệu lên thành công!')
        return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)