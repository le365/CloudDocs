import os
from werkzeug.utils import secure_filename

# Thư mục lưu file tạm trên server
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
    with app.app_context():
        db.create_all()
    app.run(debug=True)