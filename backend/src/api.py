import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS, cross_origin

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()


# ROUTES
@app.route('/drinks', methods=['GET'])
@cross_origin()
def get_drinks():
    drinks = Drink.query.order_by(Drink.id).all()
    formatted_drinks = [drink.short() for drink in drinks]
    if len(formatted_drinks) == 0:
        abort(404)
    else:
        return jsonify({'success': True, 'drinks': formatted_drinks,
                       'total_drinks': len(formatted_drinks)})


@app.route('/drinks-detail', methods=['GET'])
@cross_origin()
@requires_auth(permission='get:drinks-detail')
def get_drink_details(jwt):
    drinks = Drink.query.order_by(Drink.id).all()
    formatted_drinks = [drink.long() for drink in drinks]
    if len(formatted_drinks) == 0:
        abort(404)
    else:
        return jsonify({'success': True, 'drinks': formatted_drinks,
                       'total_drinks': len(formatted_drinks)})


@app.route('/drinks', methods=['POST'])
@cross_origin()
@requires_auth('post:drinks')
def create_drink(jwt):
    body = request.get_json()
    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)
    try:
        new_drink = Drink(title=new_title,
                          recipe=str(new_recipe).replace("'", '"'))
        new_drink.insert()
        formatted_drinks = []
        formatted_drinks.append(new_drink.long())
        return jsonify({'success': True, 'created': new_drink.id,
                       'drinks': formatted_drinks})
    except:

        abort(422)


@app.route('/drinks/<id>', methods=['PATCH'])
@cross_origin()
@requires_auth('patch:drinks')
def update_drink(id, jwt):
    try:
        drink = Drink.query.get(id)
        if drink is None:
            abort(404)
        body = request.get_json()
        new_title = body.get('title', drink.title)
        new_recipe = body.get('recipe', drink.recipe)
        drink.title = new_title
        drink.recipe = new_recipe
        drink.update()
        formatted_drinks = []
        formatted_drinks.append(drink.long())
        return jsonify({'success': True, 'updated': drink.id,
                       'drinks': formatted_drinks})
    except:
        abort(422)


@app.route('/drinks/<id>', methods=['DELETE'])
@cross_origin()
@requires_auth('delete:drinks')
def delete_drink(id, jwt):
    try:
        drink = Drink.query.get(id)
        if drink is None:
            abort(404)
        else:
            drink.delete()
            return jsonify({'success': True, 'delete': drink.id})
    except:
        abort(400)


# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return (jsonify({'success': False, 'error': 422,
            'message': 'unprocessable'}), 422)


@app.errorhandler(404)
def not_found(error):
    return (jsonify({'success': False, 'error': 404,
            'message': 'resource not found'}), 404)


@app.errorhandler(401)
def unauthorized(error):
    return (jsonify({'success': False, 'error': 401,
            'message': 'Unauthorized'}), 401)


@app.errorhandler(403)
def forbidden(error):
    return (jsonify({'success': False, 'error': 403,
            'message': 'Forbidden'}), 403)


@app.errorhandler(400)
def bad_request(error):
    return (jsonify({'success': False, 'error': 400,
            'message': 'Bad Request'}), 400)
