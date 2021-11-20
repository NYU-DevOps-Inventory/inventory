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
PUT /inventory/{int:product_id}/condition/{string:condition}/activate
    - Activate the Inventory with the given product_id and condition
PUT /inventory/{int:product_id}/condition/{string:condition}/deactivate
    - Deactivate the Inventory with the given product_id and condition

DELETE /inventory/{int:product_id}/condition/{string:condition}
    - Delete the Inventory with the given product_id and condition
"""

from typing import Dict, Union

from flask import abort, jsonify, make_response, request, url_for
# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from werkzeug.exceptions import NotFound

from service.constants import (ADDED_AMOUNT, AVAILABLE, CONDITION, PRODUCT_ID,
                               QUANTITY, QUANTITY_HIGH, QUANTITY_LOW,
                               RESTOCK_LEVEL)
from service.error_handlers import bad_request, not_found
from service.models import Condition, Inventory

from . import app  # Import Flask application
from . import status  # HTTP Status Codes

######################################################################
# GET INDEX
######################################################################


@app.route("/")
def index():
    """ Root URL response """
    return app.send_static_file("index.html")

######################################################################
# GET: LIST ALL INVENTORY
######################################################################


@app.route("/inventory", methods=["GET"])
def list_inventory():
    """ Return a list of the Inventory """
    app.logger.info("Request for inventory list")
    params: Dict[str, Union[int, str]] = request.args
    # message = "A GET request for all inventory"

    if PRODUCT_ID in params:
        product_id: int = params[PRODUCT_ID]
        inventories = Inventory.find_by_product_id(product_id)
    elif CONDITION in params:
        condition: str = params[CONDITION]
        inventories = Inventory.find_by_condition(Condition[condition])
    elif QUANTITY in params:
        quantity: int = params[QUANTITY]
        inventories = Inventory.find_by_quantity(quantity)
    elif QUANTITY_HIGH in params or QUANTITY_LOW in params:
        lowerbound: int = params[QUANTITY_LOW] if QUANTITY_LOW in params else 0
        upperbound: int = params[QUANTITY_HIGH] if QUANTITY_HIGH in params else sys.maxsize
        inventories = Inventory.find_by_quantity_range(lowerbound, upperbound)
    elif RESTOCK_LEVEL in params:
        restock_level: int = params[RESTOCK_LEVEL]
        # if restock_level == 0, we should still execute the query
        if restock_level is not None:
            inventories = Inventory.find_by_restock_level(restock_level)
    elif AVAILABLE in params:
        available: bool = params[AVAILABLE]
        inventories = Inventory.find_by_availability(available)
    elif params:
        return bad_request("Invalid request parameters")
    else:
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
    # Prevent create invenotory with same primary key
    if Inventory.find_by_product_id_condition(inventory.product_id, inventory.condition):
        return bad_request("Product_id and condition already exist.")
    inventory.create()
    message = inventory.serialize()
    location_url = url_for(
        "get_inventory_by_product_id_condition", product_id=inventory.product_id, condition=inventory.condition.name, _external=True)
    app.logger.info("Inventory ({}, {}) created."
                    .format(inventory.product_id, inventory.condition))
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

######################################################################
# GET: RETRIEVE INVENTORY
######################################################################


@app.route("/inventory/<int:product_id>/condition/<string:condition>", methods=["GET"])
def get_inventory_by_product_id_condition(product_id, condition):
    """ Retrieve inventory by the given product_id and condition """
    app.logger.info("A GET request for inventories with product_id {} and condition {}".format(
        product_id, condition))
    inventory = Inventory.find_by_product_id_condition(product_id, condition)
    if not inventory:
        raise NotFound("Inventory with product_id '{}' and condition '{}' was not found.)".format(
            product_id, condition))
    app.logger.info("Return inventory with product_id {} and condition {}".format(
        product_id, condition))
    return make_response(jsonify(inventory.serialize()), status.HTTP_200_OK)


@app.route("/inventory/<int:product_id>", methods=["GET"])
def get_inventory_by_product_id(product_id):
    """
    Retrieve Inventory by product_id

    This endpoint will return Inventory based on product's id
    """
    app.logger.info("Request for inventory with product_id: %s", product_id)
    inventories = Inventory.find_by_product_id(product_id)
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
# PUT: UPDATE IN THE INVENTORY
######################################################################


@app.route("/inventory/<int:product_id>/condition/<string:condition>", methods=["PUT"])
def update_inventory(product_id, condition):
    """ Update the inventory """
    app.logger.info("Request to update the inventory with product_id {} and condition {}".format(
        product_id, condition))
    inventory = Inventory.find_by_product_id_condition(product_id, condition)
    if not inventory:
        raise NotFound("Inventory with product '{}' of condition '{}' was not found".format(
            product_id, condition))
    params = request.get_json()
    app.logger.info(params)
    if params[QUANTITY] and params[ADDED_AMOUNT]:
        return bad_request("Ambiguous request with both QUANTITY and ADDED_AMOUNT")
    if params[QUANTITY]:
        quantity = params[QUANTITY]
        if not isinstance(quantity, int) or quantity <= 0:
            return bad_request("Quantity must be positive integer")
        inventory.quantity = quantity
    if params[ADDED_AMOUNT]:
        added_amount = params[ADDED_AMOUNT]
        if not isinstance(added_amount, int) or added_amount <= 0:
            return bad_request("Quantity must be positive integer")
        inventory.quantity += added_amount
    if params[RESTOCK_LEVEL]:
        if condition != "NEW":
            return bad_request("Restock level only makes sense to NEW products")
        restock_level = params[RESTOCK_LEVEL]
        if not isinstance(restock_level, int) or restock_level <= 0:
            return bad_request("Restock level must be positive integer")
        inventory.restock_level = restock_level
    inventory.update()
    app.logger.info(
        "Inventory of product %s of condition %s updated.", product_id, condition)
    return make_response(jsonify(inventory.serialize()), status.HTTP_200_OK)


def __toggle_inventory_available(product_id, condition, available):
    """ Update `available` of the inventory """
    app.logger.info("Request to update the inventory \
        with product_id {} and condition {}".format(product_id, condition))
    inventory: Inventory = Inventory.find_by_product_id_condition(
        product_id, condition)
    if not inventory:
        raise NotFound("Inventory with product '{}' of condition '{}' \
            was not found".format(product_id, condition))
    inventory.available = available
    inventory.update()
    app.logger.info(
        "Inventory of product %s of condition %s updated.", product_id, condition)
    return make_response(jsonify(inventory.serialize()), status.HTTP_200_OK)


@app.route("/inventory/<int:product_id>/condition/<string:condition>/activate", methods=["PUT"])
def activate_inventory(product_id, condition):
    """ Activate the inventory """
    return __toggle_inventory_available(product_id, condition, True)


@app.route("/inventory/<int:product_id>/condition/<string:condition>/deactivate", methods=["PUT"])
def deactivate_inventory(product_id, condition):
    """ Deactivate the inventory """
    return __toggle_inventory_available(product_id, condition, False)

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
    inventory = Inventory.find_by_product_id_condition(product_id, condition)
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
