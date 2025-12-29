from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-very-secure-secret-key-change-this-in-production'  # Ganti dengan secret key yang aman
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Model Database
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'admin' atau 'user'
    pets = db.relationship('Pet', backref='owner', lazy=True)

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    species = db.Column(db.String(150), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Buat DB jika belum ada
with app.app_context():
    db.create_all()
    # Buat admin default jika belum ada (jalankan sekali)
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password=generate_password_hash('adminpass'), role='admin')
        db.session.add(admin)
        db.session.commit()
        print("Admin default dibuat: username=admin, password=adminpass")

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/data_hewan', methods=['GET', 'POST'])
@login_required
def data_hewan():
    if request.method == 'POST':
        if 'add' in request.form:
            name = request.form['name']
            species = request.form['species']
            age = int(request.form['age'])
            new_pet = Pet(name=name, species=species, age=age, owner_id=current_user.id)
            db.session.add(new_pet)
            db.session.commit()
            flash('Hewan berhasil ditambahkan!', 'success')
        elif 'update' in request.form:
            pet_id = int(request.form['pet_id'])
            pet = Pet.query.get(pet_id)
            if pet and (pet.owner_id == current_user.id or current_user.role == 'admin'):
                pet.name = request.form['name']
                pet.species = request.form['species']
                pet.age = int(request.form['age'])
                db.session.commit()
                flash('Data hewan berhasil diperbarui!', 'success')
        elif 'delete' in request.form:
            pet_id = int(request.form['pet_id'])
            pet = Pet.query.get(pet_id)
            if pet and (pet.owner_id == current_user.id or current_user.role == 'admin'):
                db.session.delete(pet)
                db.session.commit()
                flash('Hewan berhasil dihapus!', 'success')
    
    if current_user.role == 'admin':
        pets = Pet.query.all()
    else:
        pets = Pet.query.filter_by(owner_id=current_user.id).all()
    return render_template('data_hewan.html', pets=pets)

@app.route('/data_user', methods=['GET', 'POST'])
@login_required
def data_user():
    if current_user.role != 'admin':
        flash('Akses ditolak! Hanya admin yang dapat mengakses halaman ini.', 'error')
        return redirect(url_for('home'))
    users = User.query.all()
    return render_template('data_user.html', users=users)

@app.route('/tambah_user', methods=['GET', 'POST'])
@login_required
def tambah_user():
    if current_user.role != 'admin':
        flash('Akses ditolak!', 'error')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        role = request.form['role']

        # Validasi username kosong atau sudah ada
        if not username:
            flash('Username wajib diisi!', 'error')
            return render_template('tambah_user.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username sudah digunakan! Pilih username lain.', 'error')
            return render_template('tambah_user.html')

        # Validasi password: minimal 6 karakter & tidak kosong
        if not password.strip():
            flash('Password wajib diisi!', 'error')
            return render_template('tambah_user.html')
        
        if len(password.strip()) < 6:
            flash('Password harus minimal 6 karakter!', 'error')
            return render_template('tambah_user.html')

        # Jika lolos validasi, buat user baru
        new_user = User(
            username=username,
            password=generate_password_hash(password),
            role=role
        )
        db.session.add(new_user)
        db.session.commit()
        flash('User baru berhasil ditambahkan!', 'success')
        return redirect(url_for('data_user'))
    
    return render_template('tambah_user.html')

@app.route('/update_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def update_user(user_id):
    if current_user.role != 'admin':
        flash('Akses ditolak!', 'error')
        return redirect(url_for('home'))
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # Cek apakah username sudah dipakai oleh user lain
        if User.query.filter(User.username == username, User.id != user_id).first():
            flash('Username sudah digunakan oleh akun lain!', 'error')
            return render_template('update_user.html', user=user)

        user.username = username
        user.role = role

        if password.strip():  # Jika password diisi
            user.password = generate_password_hash(password)
            flash('User berhasil diperbarui, termasuk password baru!', 'success')
        else:
            flash('User berhasil diperbarui (password tidak diubah karena kosong).', 'success')

        db.session.commit()
        return redirect(url_for('data_user'))

    return render_template('update_user.html', user=user)

@app.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Akses ditolak! Hanya admin yang dapat menghapus user.', 'error')
        return redirect(url_for('home'))
    user = User.query.get(user_id)
    if user and user.username != 'admin':  # Jangan hapus admin
        db.session.delete(user)
        db.session.commit()
        flash('User berhasil dihapus!', 'success')
    else:
        flash('Gagal menghapus user!', 'error')
    return redirect(url_for('data_user'))

@app.route('/fasilitas')
def fasilitas():
    return render_template('fasilitas.html')

@app.route('/alur_layanan')
def alur_layanan():
    return render_template('alur_layanan.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f'Selamat datang, {user.username}!', 'success')
            return redirect(url_for('home'))
        flash('Username atau password salah!', 'error')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Validasi password minimal 6 karakter
        if len(password) < 6:
            flash('Password minimal 6 karakter!', 'error')
            return render_template('signup.html')
        
        # Cek apakah username sudah ada
        if User.query.filter_by(username=username).first():
            flash('Username sudah digunakan! Silakan pilih username lain.', 'error')
            return render_template('signup.html')
        
        new_user = User(username=username, password=generate_password_hash(password), role='user')
        db.session.add(new_user)
        db.session.commit()
        flash('Akun berhasil dibuat! Silakan login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda berhasil logout!', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)