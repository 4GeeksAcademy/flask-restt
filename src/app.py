"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS

from src.utils import APIException, generate_sitemap
from src.admin import setup_admin
from src.models import db, User
#from src.models import Person
from src.data import people, planets  # Importamos los datos estáticos

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# Listar todos los usuarios (GET /user)
@app.route('/user', methods=['GET'])
def get_users():
    users = User.query.all()
    users_serialized = [user.serialize() for user in users]
    return jsonify(users_serialized), 200

# Crear usuario (POST /user)
@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400

    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"error": "User with this email already exists"}), 400

    new_user = User(email=data['email'], password=data['password'], is_active=True)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "User created", "user": new_user.serialize()}), 201

# Obtener usuario por ID (GET /user/<id>)
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.serialize()), 200

# Actualizar usuario (PUT /user/<id>)
@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if 'email' in data:
        user.email = data['email']
    if 'password' in data:
        user.password = data['password']
    if 'is_active' in data:
        user.is_active = data['is_active']

    db.session.commit()
    return jsonify({"msg": "User updated", "user": user.serialize()}), 200

# Borrar usuario (DELETE /user/<id>)
@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"msg": "User deleted"}), 200

# Nuevas rutas para Star Wars API

@app.route('/people', methods=['GET'])
def get_people():
    return jsonify(people), 200

@app.route('/people/<int:person_id>', methods=['GET'])
def get_person(person_id):
    person = next((p for p in people if p["id"] == person_id), None)
    if person is None:
        return jsonify({"error": "Person not found"}), 404
    return jsonify(person), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    return jsonify(planets), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = next((p for p in planets if p["id"] == planet_id), None)
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404
    return jsonify(planet), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
