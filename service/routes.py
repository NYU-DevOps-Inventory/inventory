# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Inventory Store Service

Paths:
------
GET /inventory
    - Returns a list all of the Inventory
GET /inventory/{int:product_id}/condition/{enum:condition}
    - Returns the Inventory with the given product_id and condition

POST /inventory
    - Creates a new Inventory record in the database

PUT /inventory/{int:product_id}/condition/{enum:condition}
    - Updates the Inventory with the given product_id and condition

DELETE /inventory/{int:product_id}/condition/{enum:condition}
    - Deletes the Inventory with the given product_id and condition
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from . import status  # HTTP Status Codes
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Inventory, DataValidationError

from . import app  # Import Flask application


@app.route("/")
def index():
    return "Hello, World!"


######################################################################
# ADD A NEW INVENTORY
######################################################################
@app.route("/inventoy", methods=["POST"])
def create_inventory():
    """
    Create an inventory
    This endpoint will create an inventory based the data in the body that is posted
    """
    app.logger.info("Request to create an inventory")
    check_content_type("application/json")
    inventory = Inventory()
    inventory.deserialize(request.get_json())
    inventory.create()
    message = inventory.serialize()
    location_url = url_for(
        "create_inventory", product_id=inventory.product_id, _external=True)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Inventory.init_db(app)


def check_content_type(content_type):
    """ Checks that the media type is correct """
    if "Content-Type" in request.headers and request.headers["Content-Type"] == content_type:
        return
    app.logger.error(
        "Invalid Content-Type: [%s]", request.headers.get("Content-Type"))
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
          "Content-Type must be {}".format(content_type))
