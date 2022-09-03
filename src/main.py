"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Character, Planets, Starships, Favorite


app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route("/character", methods=["GET"])
def get_character():
    try:
        all_character = Character.query.all()
        all_character = list(map(lambda character: character.serialize(), all_character))
    except Exception as error:
        print(f"Character error : {error}")    
    return jsonify(all_character)

@app.route("/planets", methods=["GET"])
def get_planets():
    try:
        all_planets = Planets.query.all()
        all_planets = list(map(lambda planets: planets.serialize(), all_planets))
    except Exception as error:
        print(f"Planets error : {error}")
    return jsonify(all_planets)

@app.route("/starships", methods=["GET"])
def get_starships():
    try:
        all_starships = Starships.query.all()
        all_starships = list(map(lambda starships: starships.serialize(), all_starships))
    except Exception as error:
        print(f"Starships error : {error}")
    return jsonify(all_starships)

@app.route("/favorite/", methods=["GET"])
def get_favorite():
    try:
        all_favorite = Favorite.query.all()
        all_favorite = list(map(lambda favorite: favorite.serialize(), all_favorite))
    except Exception as error:
        print(f"Favorite error : {error}")
    return jsonify(all_favorite)

@app.route("/favorite", methods=["POST"])
def create_favorite():
    try: 
        favorite = Favorite()
        body = request.get_json()
        favorite.favorito = body["favorito"]       
        db.session.add(favorite)
        db.session.commit()
    except Exception as error:
        print(f"FavoritePOST error : {error}")
    return jsonify({"favorite": body["favorito"]})


@app.route("/favorite/<int:id>", methods=["PUT"])
def update_favorite(id):
    if id is not None:
        favorite = Favorite.query.get(id)
        if favorite is not None:
            favorite.id = request.json.get("id")
            db.session.commit()
            return jsonify(favorite.serialize()), 200
        else:
            return jsonify({
                "msg": "Favorite not found"
            }), 404
    else:
        return jsonify({
            "msg": "Favorite is missing"
        }), 400


@app.route('/favorite <int:favorite_id>', methods=['DELETE'])
def delete_favorite(favorite_id):
    favorite = Favorite.query.all(id=favorite_id).one_or_none()
    if favorite is None:
        return jsonify({"message": "Not Found"}), 404
    deleted = favorite.delete()
    if deleted == False:
        return jsonify({"message": "Something happen try again"}), 500
    return jsonify([]), 204



if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)