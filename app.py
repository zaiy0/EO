from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)

# Konfigurasi koneksi database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '' 
app.config['MYSQL_DB'] = 'db_event'

# Inisialisasi MySQL
mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()
        
        if account:
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid credentials'
    return render_template('login.html')

@app.route('/dashboard/')
def dashboard():
    return render_template('layout/dashboard.html')

@app.route('/dashboard/timeline/')
def timeline():
    return render_template('layout/timeline.html')

@app.route('/dashboard/manage/')
def manage():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM divisi')
    data = cursor.fetchall()
    return render_template('layout/manage.html', data=data)

@app.route('/dashboard/mahasiswa/')
def mahasiswa():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM mahasiswa')
    data = cursor.fetchall()
    return render_template('layout/mahasiswa.html', mahasiswa=data)

@app.route('/dashboard/notulensi/')
def notulensi():
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM notulensi')
    data = cursor.fetchall()
    return render_template('layout/notulensi.html', notulensi=data)

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
        mysql.connection.commit()
        
        return redirect(url_for('login'))
    return render_template('register.html')

# Routes for CRUD operations on 'mahasiswa'

@app.route('/dashboard/mahasiswa/add', methods=['GET', 'POST'])
def add_mahasiswa():
    if request.method == 'POST':
        nim = request.form['nim']
        nama = request.form['nama']
        email = request.form['email']
        no_telepon = request.form['no_telepon']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO mahasiswa (nim, nama, email, no_telepon) VALUES (%s, %s, %s, %s)', 
                       (nim, nama, email, no_telepon))
        mysql.connection.commit()
        
        return redirect(url_for('mahasiswa'))
    return render_template('layout/add_mahasiswa.html')

@app.route('/divisi/tambah', methods=['GET', 'POST'])
def add_divisi():
    if request.method == 'POST':
        nama_divisi = request.form['nama_divisi']
        nim = request.form['nim']
        
        # Check if nim exists in mahasiswa table first
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT nim FROM mahasiswa WHERE nim = %s', (nim,))
        mahasiswa = cursor.fetchone()
        
        if mahasiswa:
            # nim exists in mahasiswa table, proceed to insert into divisi
            cursor.execute('INSERT INTO divisi (nama_divisi, nim) VALUES (%s, %s)', (nama_divisi, nim))
            mysql.connection.commit()
            
            return redirect(url_for('manage'))
        else:
            # nim does not exist in mahasiswa table, handle this scenario (e.g., redirect with error message)
            return "Error: nim does not exist in mahasiswa table!"
    
    return render_template('add_divisi.html')

@app.route('/divisi/edit/<int:id>', methods=['GET', 'POST'])
def edit_divisi(id):

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        nama_divisi = request.form['nama_divisi']
        nim = request.form['nim']
        
        cursor.execute('UPDATE divisi SET nama_divisi = %s, nim = %s WHERE id_divisi = %s', 
                       (nama_divisi, nim, id))
        mysql.connection.commit()
        
        return redirect(url_for('manage'))
    else:
        cursor.execute('SELECT * FROM divisi WHERE id_divisi = %s', [id])
        divisi = cursor.fetchone()
        
        return render_template('layout/edit_divisi.html', divisi=divisi)


@app.route('/dashboard/mahasiswa/edit/<int:nim>', methods=['GET', 'POST'])
def edit_mahasiswa(nim):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM mahasiswa WHERE nim = %s', [nim])
    data = cursor.fetchone()
    
    if request.method == 'POST':
        npm = request.form['nim']
        nama = request.form['nama']
        email = request.form['email']
        no_telepon = request.form['no_telepon']
        
        cursor.execute('UPDATE mahasiswa SET nim = %s, nama = %s, email = %s, no_telepon = %s WHERE nim = %s', 
                       (npm, nama, email, no_telepon, nim))
        mysql.connection.commit()
        
        return redirect(url_for('mahasiswa'))
    return render_template('layout/edit_mahasiswa.html', mahasiswa=data)

@app.route('/dashboard/mahasiswa/delete/<nim>', methods=['GET', 'POST'])
def delete_mahasiswa(nim):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM mahasiswa WHERE nim = %s', [nim])
    mysql.connection.commit()
    
    return redirect(url_for('mahasiswa'))

@app.route('/dashboard/divisi/delete/<id>', methods=['GET', 'POST'])
def delete_divisi(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM divisi WHERE id_divisi = %s', [id])
    mysql.connection.commit()
    
    return redirect(url_for('manage'))

# Routes for CRUD operations on 'notulensi'
@app.route('/dashboard/notulensi/add', methods=['GET', 'POST'])
def add_notulensi():
    if request.method == 'POST':
        id_divisi = request.form['id_divisi']
        tanggal = request.form['tanggal']
        status = request.form['status']
        catatan = request.form['catatan']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO notulensi (id_divisi, tanggal, status, catatan) VALUES (%s,%s, %s, %s)', 
                       (id_divisi,tanggal, status, catatan))
        mysql.connection.commit()
        
        return redirect(url_for('notulensi'))
    return render_template('layout/add_notulensi.html')

@app.route('/dashboard/notulensi/edit/<id>', methods=['GET', 'POST'])
def edit_notulensi(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM notulensi WHERE id_notulensi = %s', [id])
    data = cursor.fetchone()
    
    if request.method == 'POST':
        tanggal = request.form['tanggal']
        status = request.form['status']
        catatan = request.form['catatan']
        
        cursor.execute('UPDATE notulensi SET tanggal = %s, status = %s, catatan = %s WHERE id_notulensi = %s', 
                       (tanggal, status, catatan, id))
        mysql.connection.commit()
        
        return redirect(url_for('notulensi'))
    return render_template('layout/edit_notulensi.html', notulensi=data)

@app.route('/dashboard/notulensi/delete/<id>', methods=['GET'])
def delete_notulensi(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM notulensi WHERE id_notulensi = %s', [id])
    mysql.connection.commit()
    
    return redirect(url_for('notulensi'))

if __name__ == '__main__':
    app.run(debug=True)
