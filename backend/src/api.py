import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS , cross_origin

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

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
@cross_origin()
def get_drinks():
    drinks = Drink.query.order_by(Drink.id).all()
    formatted_drinks = [drink.title for drink in drinks]
    if len(formatted_drinks) == 0:
        abort(404)
    else:
        return jsonify(
            {
                "success": True
                , "drinks": formatted_drinks
                , "total_drinks": len(formatted_drinks)
            }
        )


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@cross_origin()
def get_drink_details():
    drinks = Drink.query.order_by(Drink.id).all()
    formatted_drinks = [drink.title for drink in drinks]
    if len(formatted_drinks) == 0:
        abort(404)
    else:
        return jsonify(
            {
                "success": True
                , "drinks": formatted_drinks
                , "total_drinks": len(formatted_drinks)
            }
        )

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@cross_origin()
def create_drink():
    body = request.get_json()
    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)
    try:
        new_drink = Drink(title=new_title,recipe=new_recipe)
        new_drink.insert()
        return jsonify({
            "success": True
            , "created": new_drink.id
        })

    except:
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<drink_id>', methods=['PATCH'])
@cross_origin()
def update_drink(drink_id):
    try:
        drink = Drink.query.get(drink_id)
        body = request.get_json()
        new_title = body.get('title', drink.title)
        new_recipe = body.get('recipe', drink.recipe)
        drink.update()
        return jsonify({
            "success": True
            , "created": drink.id
        })
    except:
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<drink_id>', methods=['DELETE'])
@cross_origin()
def delete_drink(drink_id):
    try:
        drink = Drink.query.get(drink_id)
        drink.delete()
        return jsonify({
            "success": True
            , "deleted": drink.id
        })
    except:
        abort(400)

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                "success": False,
                "error": 422,
                "message": "unprocessable"
                }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
        }), 404

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized"
        }), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forbidden"
        }), 403

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400