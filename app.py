from flask import Flask, render_template, request, redirect, session, url_for, jsonify, flash
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'rahasia'

# Koneksi ke MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['smart_akuarium']
user_collection = db['users']
monitoring_collection = db['monitoring']

# Batas normal parameter air
THRESHOLDS = {
    "tds_min": 200,
    "tds_max": 500
}

# Simulasi data sensor (dummy)
def get_sensor_data():
    return {
        "tds": 250,
        "timestamp": datetime.now()
    }

def is_anomaly(data):
    try:
        tds = float(data.get('tds', 0))
    except (KeyError, ValueError):
        return False
    return tds < THRESHOLDS['tds_min'] or tds > THRESHOLDS['tds_max']


@app.route("/")
def index():
    return render_template("index.html", username=session.get("username"))

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('index'))

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            user_collection.insert_one({
                'username': request.form['username'],
                'email': request.form['email'],
                'password': request.form['password'],
                'role': 'user'
            })
            flash("User baru berhasil ditambahkan.")

        elif action == 'edit':
            user_id = request.form['user_id']
            user_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {
                    'username': request.form['username'],
                    'email': request.form['email'],
                    'password': request.form['password']
                }}
            )
            flash("Data user berhasil diperbarui.")

        elif action == 'delete':
            user_id = request.form['user_id']
            user_collection.delete_one({'_id': ObjectId(user_id)})
            flash("User berhasil dihapus.")

        return redirect(url_for('admin_dashboard'))

    users = list(user_collection.find())
    return render_template('admin.html', users=users)

@app.route('/monitoring')
def monitoring():
    if "username" not in session or session.get('role') != 'user':
        return redirect(url_for('index'))
    return render_template('monitoring.html', username=session["username"])

@app.route('/register', methods=['POST'])
def register_user():
    uname = request.form['username']
    email = request.form['email']
    passwd = request.form['password']

    if user_collection.find_one({'username': uname}):
        flash('Username sudah terdaftar.')
        return redirect(url_for('index'))

    user_collection.insert_one({
        'username': uname,
        'email': email,
        'password': passwd,
        'role': 'user'
    })

    flash('Registrasi berhasil! Silakan login.')
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    uname = request.form['username']
    passwd = request.form['password']

    user = user_collection.find_one({'username': uname, 'password': passwd})
    if user:
        session['username'] = uname
        session['logged_in'] = True
        session['role'] = user.get('role', 'user')

        flash('Login berhasil. Selamat datang!')
        if session['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('index'))
    else:
        flash('Username atau password salah.')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    flash("Anda telah logout.")
    return redirect(url_for('index'))

@app.route('/history')
def history():
    if not session.get('logged_in') or session.get('role') != 'user':
        return redirect(url_for('login'))
    return render_template('history.html', username=session['username'])

@app.route('/history_data')
def history_data():
    if "username" not in session or session.get('role') != 'user':
        return jsonify({'error': 'unauthorized'}), 401

    records = list(monitoring_collection.find(
        {"username": session["username"]}
    ).sort("timestamp", -1))

    for r in records:
        r["_id"] = str(r["_id"])
        r["timestamp"] = r["timestamp"].strftime("%Y-%m-%d %H:%M:%S") if "timestamp" in r else "-"
    return jsonify(records)

@app.route('/clear_history', methods=['POST'])
def clear_history():
    if "username" not in session or session.get('role') != 'user':
        return redirect(url_for('login'))

    monitoring_collection.delete_many({"username": session["username"]})
    flash("Riwayat berhasil dihapus.")
    return redirect(url_for('history'))

@app.route('/check_anomaly')
def check_anomaly():
    if not session.get('logged_in') or session.get('role') != 'user':
        return jsonify({'error': 'unauthorized'}), 401

    latest = monitoring_collection.find_one(
        {"username": session["username"]},
        sort=[('timestamp', -1)]
    )

    if latest and is_anomaly(latest):
        return jsonify({
            'anomaly': True,
            'data': {
                "tds": latest['tds'],
                "timestamp": latest['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            }
        })

    return jsonify({'anomaly': False})

@app.route('/data')
def data():
    if not session.get('logged_in') or session.get('role') != 'user':
        return jsonify({'error': 'unauthorized'}), 401

    latest = monitoring_collection.find_one(
        {"username": session["username"]},
        sort=[('timestamp', -1)]
    )
    if latest:
        timestamp = latest.get("timestamp")
        if isinstance(timestamp, datetime):
            timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        return jsonify({
            'tds': float(latest.get('tds', 0)),
            'timestamp': timestamp
        })
    else:
        return jsonify({'message': 'No data available'})

@app.route('/save_data', methods=['POST'])
def save_data():
    if "username" not in session or session.get('role') != 'user':
        return jsonify({'error': 'unauthorized'}), 401

    data = request.get_json()
    if data:
        data['timestamp'] = datetime.now()
        data['username'] = session["username"]
        monitoring_collection.insert_one(data)
        return jsonify({'message': 'Data saved'}), 200
    else:
        return jsonify({'error': 'No data received'}), 400

@app.route('/api/tds', methods=['POST'])
def api_tds():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No JSON received'}), 400

        tds = float(data.get('tds', 0))
        username = data.get('username', None)

        if not username:
            return jsonify({'message': 'Username missing in request'}), 400

        monitoring_collection.insert_one({
            "tds": tds,
            "timestamp": datetime.now(),
            "username": username
        })

        return jsonify({'message': 'Data inserted successfully'}), 200

    except Exception as e:
        print("API Error:", e)
        return jsonify({'message': 'Failed to insert data'}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
