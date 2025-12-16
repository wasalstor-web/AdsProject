import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tiktok-master-key-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tiktok.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max limit

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة'
login_manager.login_message_category = 'warning'

# --- Models ---

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='customer')  # customer, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ads = db.relationship('Ad', backref='author', lazy=True)

class Ad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    package = db.Column(db.String(50), nullable=False) # basic, first, advanced
    status = db.Column(db.String(20), default='pending_review') # pending_review, approved, rejected, published
    
    # Analytics
    tiktok_url = db.Column(db.String(255), nullable=True)
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    shares = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('البريد الإلكتروني مسجل مسبقاً', 'danger')
        else:
            new_user = User(email=email, name=name, password=generate_password_hash(password, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash('تم إنشاء الحساب بنجاح!', 'success')
            return redirect(url_for('dashboard'))
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('تم تسجيل الدخول بنجاح', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('البريد الإلكتروني أو كلمة المرور غير صحيحة', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    my_ads = Ad.query.filter_by(user_id=current_user.id).order_by(Ad.created_at.desc()).all()
    return render_template('dashboard.html', ads=my_ads)

@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        abort(403)
    
    all_ads = Ad.query.order_by(Ad.created_at.desc()).all()
    return render_template('admin_dashboard.html', ads=all_ads)

@app.route('/create_ad', methods=['GET', 'POST'])
@login_required
def create_ad():
    if request.method == 'POST':
        if 'video' not in request.files:
            flash('لم يتم اختيار ملف فيديو', 'danger')
            return redirect(request.url)
        
        file = request.files['video']
        title = request.form.get('title')
        description = request.form.get('description')
        package = request.form.get('package')
        
        if file.filename == '' or not title or not package:
            flash('جميع الحقول مطلوبة', 'danger')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            new_ad = Ad(
                title=title,
                description=description,
                filename=filename,
                package=package,
                user_id=current_user.id,
                status='pending_review' # Skip payment for MVP, go straight to review
            )
            db.session.add(new_ad)
            db.session.commit()
            
            flash('تم رفع الإعلان وإرساله للمراجعة!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('صيغة الملف غير مدعومة', 'danger')
            
    return render_template('create_ad.html')

@app.route('/admin/action/<int:ad_id>/<action>')
@login_required
def admin_action(ad_id, action):
    if current_user.role != 'admin':
        abort(403)
        
    ad = Ad.query.get_or_404(ad_id)
    
    if action == 'approve':
        ad.status = 'approved'
        flash('تم قبول الإعلان. سيتم نشره قريباً.', 'success')
    elif action == 'reject':
        ad.status = 'rejected'
        flash('تم رفض الإعلان.', 'warning')
    elif action == 'publish':
        # Simulate TikTok API Call
        ad.status = 'published'
        ad.tiktok_url = f"https://www.tiktok.com/@ads_market/video/{datetime.now().strftime('%f')}"
        ad.views = 150
        flash('تم نشر الإعلان على تيك توك بنجاح!', 'success')
        
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

# Setup initial admin user
@app.cli.command("create-admin")
def create_admin():
    db.create_all()
    if not User.query.filter_by(email="admin@tiktokhub.com").first():
        admin = User(
            email="admin@tiktokhub.com",
            name="Admin",
            password=generate_password_hash("admin123", method='pbkdf2:sha256'),
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created: admin@tiktokhub.com / admin123")
    else:
        print("Admin user already exists")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
