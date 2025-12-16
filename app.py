import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tiktok-master-key-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tiktok.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max limit for videos

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    videos = Video.query.order_by(Video.created_at.desc()).all()
    return render_template('index.html', videos=videos)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'video' not in request.files:
            flash('لم يتم اختيار ملف فيديو', 'danger')
            return redirect(request.url)
        
        file = request.files['video']
        
        if file.filename == '':
            flash('لم يتم اختيار ملف', 'danger')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to filename to avoid duplicates
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            new_video = Video(
                title=request.form.get('title', 'بدون عنوان'),
                description=request.form.get('description', ''),
                filename=filename
            )
            db.session.add(new_video)
            db.session.commit()
            
            flash('تم رفع الفيديو بنجاح!', 'success')
            return redirect(url_for('index'))
        else:
            flash('صيغة الملف غير مدعومة. يرجى رفع فيديو (MP4, MOV, AVI)', 'danger')
            
    return render_template('upload.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
