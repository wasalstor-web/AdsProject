import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'dev-key-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ads.db'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Database Model
class Ad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    contact = db.Column(db.String(50), nullable=False)
    image_filename = db.Column(db.String(100), nullable=True)

# Initialize DB
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    ads = Ad.query.order_by(Ad.id.desc()).all()
    return render_template('index.html', ads=ads)

@app.route('/add', methods=('GET', 'POST'))
def add_ad():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        contact = request.form['contact']
        
        image = request.files.get('image')
        image_filename = None
        
        if image and image.filename:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_filename = filename
        
        new_ad = Ad(
            title=title,
            description=description,
            price=float(price),
            contact=contact,
            image_filename=image_filename
        )
        db.session.add(new_ad)
        db.session.commit()
        return redirect(url_for('index'))
        
    return render_template('add_ad.html')

if __name__ == '__main__':
    app.run(debug=True)