from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from models import db, User, Product, ChatLog
from utils import generate_mock_products

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app, supports_credentials=True)
db.init_app(app)

with app.app_context():
    db.create_all()
    if Product.query.first() is None:
        for p in generate_mock_products():
            product = Product(name=p['name'], description=p['description'], price=p['price'])
            db.session.add(product)
        db.session.commit()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Username already exists"}), 400

    user = User(username=data['username'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        session['user_id'] = user.id
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logged out"})

@app.route('/products', methods=['GET'])
def get_products():
    query = request.args.get('query', '')
    products = Product.query.filter(Product.name.contains(query)).all()
    result = []
    for p in products:
        result.append({
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': p.price
        })
    return jsonify(result)

@app.route('/chatlog', methods=['POST'])
def save_chatlog():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.get_json()
    log = ChatLog(user_id=session['user_id'], message=data['message'], timestamp=datetime.now())
    db.session.add(log)
    db.session.commit()
    return jsonify({"message": "Chat log saved"})

@app.route('/chatlog', methods=['GET'])
def get_chatlogs():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    logs = ChatLog.query.filter_by(user_id=session['user_id']).all()
    result = []
    for log in logs:
        result.append({
            'message': log.message,
            'timestamp': log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
