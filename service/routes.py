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
    - Return a list all of the Inventory
GET /inventory/{int:product_id}/condition/{string:condition}
    - Return the Inventory with the given product_id and condition

POST /inventory
    - Create a new Inventory record in the database

PUT /inventory/{int:product_id}/condition/{string:condition}
    - Update the Inventory with the given product_id and condition

DELETE /inventory/{int:product_id}/condition/{string:condition}
    - Delete the Inventory with the given product_id and condition
"""

import logging
import os
import sys

from flask import Flask, abort, jsonify, make_response, request, url_for
# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import NotFound

from service.models import DataValidationError, Inventory

from . import app  # Import Flask application
from . import status  # HTTP Status Codes

######################################################################
# GET INDEX
######################################################################


@app.route("/")
def index():
    """ Root URL response """
    return (
        jsonify(
            name="Inventory REST API Service",
            version="1.0",
            paths=url_for("list_inventory", _external=True),
        ),
        status.HTTP_200_OK,
    )

######################################################################
# GET: LIST ALL INVENTORY
######################################################################


@app.route("/inventory", methods=["GET"])
def list_inventory():
    """ Return all of the Inventory """
    app.logger.info("Request for inventory list")
    inventories = Inventory.all()
    results = [inventory.serialize() for inventory in inventories]
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# POST: ADD A NEW INVENTORY
######################################################################


@app.route("/inventory", methods=["POST"])
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
        "get_inventory_by_pid_condition", product_id=inventory.product_id, condition=inventory.condition.name, _external=True)
    app.logger.info("Inventory ({}, {}) created."
                    .format(inventory.product_id, inventory.condition))
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

######################################################################
# GET: RETRIEVE INVENTORY
######################################################################


@app.route("/inventory/<int:product_id>/condition/<string:condition>", methods=["GET"])
def get_inventory_by_pid_condition(product_id, condition):
    """ Retrieve inventory by the given product_id and condition """
    app.logger.info("A GET request for inventories with product_id {} and condition {}".format(
        product_id, condition))
    inventory = Inventory.find_by_pid_condition(product_id, condition)
    if not inventory:
        return NotFound("Inventory with product_id '{}' and condition '{}' was not found.)".format(product_id, condition))
    app.logger.info("Return inventory with product_id {} and condition {}".format(
        product_id, condition))
    return make_response(jsonify(inventory.serialize()), status.HTTP_200_OK)


@app.route("/inventory/<int:product_id>", methods=["GET"])
def get_inventory_by_pid(product_id):
    """
    Retrieve Inventory by product_id

    This endpoint will return Inventory based on product's id
    """
    app.logger.info("Request for inventory with product_id: %s", product_id)
    inventories = Inventory.find_by_pid(product_id)
    if not inventories:
        raise NotFound(
            "Inventory with product_id '{}' was not found.".format(product_id))

    results = [inventory.serialize() for inventory in inventories]
    return make_response(jsonify(results), status.HTTP_200_OK)


@app.route("/inventory/condition/<string:condition>", methods=["GET"])
def get_inventory_by_condition(condition):
    """
    Retrieve Inventory by condition

    This endpoint will return Inventory based on product's condition
    """
    app.logger.info("Request for inventory with condition: %s", condition)
    inventories = Inventory.find_by_condition(condition)
    if not inventories:
        raise NotFound(
            "Inventory with condition '{}' was not found.".format(condition))

    results = [inventory.serialize() for inventory in inventories]
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# DELETE A INVENTORY
######################################################################


@app.route("/inventory/<int:product_id>/condition/<string:condition>", methods=["DELETE"])
def delete_inventory(product_id, condition):
    """
    Delete a Inventory
    This endpoint will delete an inventory based the product_id and condition specified in the path
    """
    app.logger.info(
        "Request to delete inventory of which product_id: %s and condition %s", product_id, condition)
    inventory = Inventory.find_by_pid_condition(product_id, condition)
    if inventory:
        inventory.delete()
    return make_response("", status.HTTP_204_NO_CONTENT)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """ Initialize the SQLAlchemy app """
    global app
    Inventory.init_db(app)


def check_content_type(content_type):
    """ Check that the media type is correct """
    if "Content-Type" in request.headers and request.headers["Content-Type"] == content_type:
        return
    app.logger.error(
        "Invalid Content-Type: [%s]", request.headers.get("Content-Type"))
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
          "Content-Type must be {}".format(content_type))
