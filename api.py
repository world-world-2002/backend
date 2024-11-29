from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

# Database Configuration: Update with your database connection details
# Example for MySQL: 'mysql+pymysql://username:password@host/dbname'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///refill_app.db'  # Replace with your actual database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models: Adjust column names and types based on your actual database schema
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    rewards = db.Column(db.Integer, default=0)

class RefillStation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True)

# Replace or add tables here to match your database schema

# Endpoints

# User Registration
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"})

# User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        return jsonify({"message": "Login successful!", "user_id": user.id})
    return jsonify({"message": "Invalid credentials!"}), 401

# Get All Refill Stations
@app.route('/stations', methods=['GET'])
def get_stations():
    stations = RefillStation.query.all()
    station_list = [
        {"id": s.id, "name": s.name, "latitude": s.latitude, "longitude": s.longitude, "description": s.description}
        for s in stations
    ]
    return jsonify(station_list)

# Add a New Refill Station
@app.route('/stations', methods=['POST'])
def add_station():
    data = request.json
    new_station = RefillStation(
        name=data['name'],
        latitude=data['latitude'],
        longitude=data['longitude'],
        description=data.get('description', '')
    )
    db.session.add(new_station)
    db.session.commit()
    return jsonify({"message": "Station added successfully!"})

# Add Rewards
@app.route('/reward/<int:user_id>', methods=['POST'])
def add_reward(user_id):
    user = User.query.get(user_id)
    if user:
        user.rewards += 10  # Adjust reward logic if needed
        db.session.commit()
        return jsonify({"message": f"Reward added! Total points: {user.rewards}"})
    return jsonify({"message": "User not found!"}), 404

# Get User Rewards
@app.route('/reward/<int:user_id>', methods=['GET'])
def get_rewards(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({"rewards": user.rewards})
    return jsonify({"message": "User not found!"}), 404

# Mock Payment Endpoint
@app.route('/payment', methods=['POST'])
def process_payment():
    data = request.json
    if data['amount'] > 0:  # Replace with actual payment gateway logic
        return jsonify({"message": "Payment successful!"})
    return jsonify({"message": "Invalid payment amount!"}), 400

# Start the Server
if __name__ == '__main__':
    # Uncomment the following line if you need to create tables in your database
    # with app.app_context(): db.create_all()
    app.run(debug=True)
