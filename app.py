from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ini-adalah-secret-key-sangat-rahasia'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///karyawan.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Model Database
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Karyawan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    alamat = db.Column(db.String(200))
    gaji = db.Column(db.Float)
    jabatan = db.Column(db.String(100))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password salah!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/karyawan')
@login_required
def daftar_karyawan():
    semua_karyawan = Karyawan.query.all()
    return render_template('karyawan.html', karyawan=semua_karyawan)

@app.route('/karyawan/tambah', methods=['GET', 'POST'])
@login_required
def tambah_karyawan():
    if request.method == 'POST':
        nama = request.form.get('nama')
        alamat = request.form.get('alamat')
        gaji = request.form.get('gaji')
        jabatan = request.form.get('jabatan')
        
        karyawan_baru = Karyawan(
            nama=nama,
            alamat=alamat,
            gaji=gaji,
            jabatan=jabatan
        )
        
        db.session.add(karyawan_baru)
        db.session.commit()
        
        flash('Karyawan berhasil ditambahkan!', 'success')
        return redirect(url_for('daftar_karyawan'))
    
    return render_template('tambah_edit.html')

@app.route('/karyawan/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_karyawan(id):
    karyawan = Karyawan.query.get_or_404(id)
    
    if request.method == 'POST':
        karyawan.nama = request.form.get('nama')
        karyawan.alamat = request.form.get('alamat')
        karyawan.gaji = request.form.get('gaji')
        karyawan.jabatan = request.form.get('jabatan')
        
        db.session.commit()
        
        flash('Data karyawan berhasil diperbarui!', 'success')
        return redirect(url_for('daftar_karyawan'))
    
    return render_template('tambah_edit.html', karyawan=karyawan)

@app.route('/karyawan/hapus/<int:id>')
@login_required
def hapus_karyawan(id):
    karyawan = Karyawan.query.get_or_404(id)
    db.session.delete(karyawan)
    db.session.commit()
    
    flash('Karyawan berhasil dihapus!', 'success')
    return redirect(url_for('daftar_karyawan'))

# Fungsi untuk membuat user admin awal
def create_admin_user():
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password=generate_password_hash('admin123', method='pbkdf2:sha256')
        )
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin_user()
    app.run(debug=True)
