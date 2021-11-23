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

import sys
from typing import Dict, Optional, Union

from flask import abort, jsonify, make_response, request, url_for
from flask_restx import Api, Resource, fields, inputs, reqparse
# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from werkzeug.exceptions import NotFound

from service.constants import (ADDED_AMOUNT, AVAILABLE, CONDITION, PRODUCT_ID,
                               QUANTITY, QUANTITY_HIGH, QUANTITY_LOW,
                               RESTOCK_LEVEL)
from service.error_handlers import (bad_request, mediatype_not_supported,
                                    not_found)
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
# Configure Swagger before initializing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Inventory Demo REST API Service',
          description='This is a sample server Inventory store server.',
          default='inventory',
          default_label='Inventory shop operations',
          doc='/apidocs',  # default also could use doc='/apidocs/'
          prefix='/api'
          )


# Define the model so that the docs reflect what can be sent
inventory_model = api.model('Inventory', {
    PRODUCT_ID: fields.Integer(readOnly=True,
                               description='The unique id assigned to a Product\n'),
    CONDITION: fields.String(readOnly=True,
                             description='Condition of the product\nNote: {} in ["new", "used", "open box"]'
                             .format(CONDITION)),
    QUANTITY: fields.Integer(required=True,
                             description='The Quantity of Inventory item\nNote: {} >= 0'.format(QUANTITY)),
    RESTOCK_LEVEL: fields.Integer(required=True,
                                  description='The level below which restock this item is triggered.\nNote: {} >= 0'
                                  .format(RESTOCK_LEVEL)),
    AVAILABLE: fields.Boolean(required=True,
                              description='Is the Product avaialble?\nNote: Available (True) or Unavailable (False)')
})


# query string arguments
inventory_args = reqparse.RequestParser()
inventory_args.add_argument(PRODUCT_ID, type=int, required=False,
                            help='List Inventory by Product ID')
inventory_args.add_argument(CONDITION, type=str, required=False,
                            help='List Inventory by Condition')
inventory_args.add_argument(QUANTITY, type=int, required=False,
                            help='List Inventory by (>=) Quantity')
inventory_args.add_argument(AVAILABLE, type=inputs.boolean, required=False,
                            help='List Inventory by Availability')

################################################################################
#  U T I L I T Y   F U N C T I O N S
################################################################################


@app.before_first_request
def init_db():
    """ Initialize the SQLAlchemy app """
    global app
    Inventory.init_db(app)


######################################################################
# PATH: /inventory/{product_id}/condition/{condition}
######################################################################
@api.route('/inventory/<int:product_id>/condition/<string:condition>')
@api.param('product_id, condition', 'The Inventory identifiers')
class InventoryResource(Resource):
    """
    GET     /inventory/<int:product_id>/condition/<string:condition> - Return an Inventory
    PUT     /inventory/<int:product_id>/condition/<string:condition> - Update an Inventory
    DELETE  /inventory/<int:product_id>/condition/<string:condition> - Delete an Inventory
    """

    # ------------------------------------------------------------------
    # RETRIEVE A INVENTORY
    # ------------------------------------------------------------------
    @api.doc('get_inventory')
    @api.response(404, 'Inventory not found')
    @api.marshal_with(inventory_model)
    def get(self, product_id: int, condition: str):
        """
        Retrieve a single Inventory

        This endpoint will return an Inventory based on product_id and condition
        """
        app.logger.info("Request to get inventory with key ({}, {})"
                        .format(product_id, condition))
        inventory: Optional[Inventory] = Inventory.find_by_product_id_condition(
            product_id, condition)
        if not inventory:
            api.abort(status.HTTP_404_NOT_FOUND,
                      "Inventory ({}, {}) NOT FOUND".format(product_id, condition))
        app.logger.info("Inventory ({}, {}) returned."
                        .format(product_id, condition))
        return inventory.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING INVENTORY
    # ------------------------------------------------------------------
    @api.doc('update_inventory')
    @api.response(status.HTTP_404_NOT_FOUND, 'Inventory not found')
    @api.response(status.HTTP_400_BAD_REQUEST, 'The posted Inventory data was not valid')
    @api.expect(inventory_model)
    @api.marshal_with(inventory_model)
    def put(self, product_id: int, condition: str):
        """
        Update an Inventory

        This endpoint will update an Inventory based the body that is posted
        """
        app.logger.info("Request to update inventory with key ({}, {})"
                        .format(product_id, condition))
        inventory: Optional[Inventory] = Inventory.find_by_product_id_condition(
            product_id, condition)
        if not inventory:
            api.abort(status.HTTP_404_NOT_FOUND,
                      "Inventory with ({}, {})".format(product_id, condition))
        app.logger.debug(f"Payload = {api.payload}")
        # To conform with expect
        inventory_dict = inventory.serialize()
        for key in inventory_dict.keys():
            if key in api.payload:
                inventory_dict[key] = api.payload[key]
        inventory.deserialize(inventory_dict)
        inventory.update()
        app.logger.info("Inventory ({}, {}) updated."
                        .format(product_id, condition))
        return inventory.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE AN INVENTORY
    # ------------------------------------------------------------------
    @api.doc('delete_inventory')
    @api.response(status.HTTP_204_NO_CONTENT, 'Inventory deleted')
    def delete(self, product_id: int, condition: str):
        """
        Delete an Inventory

        This endpoint will delete an Inventory based on product_id and condition
        """
        app.logger.info("Request to delete inventory with key ({}, {})"
                        .format(product_id, condition))
        inventory: Optional[Inventory] = Inventory.find_by_product_id_condition(
            product_id, condition)
        if inventory:
            inventory.delete()
        app.logger.info("Inventory ({}, {}) deleted."
                        .format(product_id, condition))
        return '', status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /inventory
######################################################################
@api.route('/inventory', strict_slashes=False)
class InventoryCollection(Resource):
    """ Handles all interactions with collections of Pets
    POST    /inventory - Add a new Inventory
    GET     /inventory - Return a list of the Inventory
    """

    # ------------------------------------------------------------------
    # ADD A NEW INVENTORY
    # ------------------------------------------------------------------
    @api.doc('get_inventory')
    @api.response(status.HTTP_404_NOT_FOUND, 'Inventory not found')
    @api.response(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 'Unsuppoted media requests')
    @api.response(status.HTTP_400_BAD_REQUEST, 'The posted Inventory data was not valid')
    @api.expect(inventory_model)
    @api.marshal_with(inventory_model, code=201)
    # TODO Add token required check
    def post(self):
        """
        Create an Inventory

        This endpoint will create a Inventory based the data in the body that is posted
        """
        app.logger.info('Request to Create an Inventory')
        check_content_type("application/json")
        inventory = Inventory()
        app.logger.debug(f"Payload = {api.payload}")
        inventory.deserialize(api.payload)
        # Prevent create invenotory with same primary key
        if Inventory.find_by_product_id_condition(inventory.product_id, inventory.condition):
            return bad_request("Product_id and condition already exist.")
        inventory.create()
        app.logger.info("Inventory ({}, {}) created."
                        .format(inventory.product_id, inventory.condition))
        location_url = api.url_for(InventoryResource, product_id=inventory.product_id,
                                   condition=inventory.condition.name, _external=True)
        return inventory.serialize(), status.HTTP_201_CREATED, {'Location': location_url}

######################################################################
# GET: LIST ALL INVENTORY
######################################################################


@app.route("/inventory", methods=["GET"])
def list_inventory():
    """ Return a list of the Inventory """
    app.logger.info("Request for inventory list")
    params: Dict[str, Union[int, str]] = request.args.to_dict()
    # message = "A GET request for all inventory"

    if len(params) == 0:
        inventories = Inventory.all()
        results = [inventory.serialize() for inventory in inventories]
        return make_response(jsonify(results), status.HTTP_200_OK)

    # TODO: Avoid using list intersection for more efficency
    # TODO: Unit test intersection function
    inventories = []
    # Actually this condition will always be true in real use cases
    if AVAILABLE in params:
        available: bool = params[AVAILABLE]
        inventories = Inventory.find_by_availability(available)
        params.pop(AVAILABLE, None)

    if PRODUCT_ID in params:
        product_id: int = params[PRODUCT_ID]
        finds = Inventory.find_by_product_id(product_id)
        if len(inventories) == 0:
            inventories = finds
        else:
            inventories = list(set(inventories) & set(finds))
        params.pop(PRODUCT_ID, None)
    if CONDITION in params:
        condition: str = params[CONDITION]
        finds = Inventory.find_by_condition(Condition[condition])
        if len(inventories) == 0:
            inventories = finds
        else:
            inventories = list(set(inventories) & set(finds))
        params.pop(CONDITION, None)
    if QUANTITY in params:
        quantity: int = params[QUANTITY]
        finds = Inventory.find_by_quantity(quantity)
        if len(inventories) == 0:
            inventories = finds
        else:
            inventories = list(set(inventories) & set(finds))
        params.pop(QUANTITY, None)
    if QUANTITY_HIGH in params or QUANTITY_LOW in params:
        lowerbound: int = params[QUANTITY_LOW] if QUANTITY_LOW in params else 0
        upperbound: int = params[QUANTITY_HIGH] if QUANTITY_HIGH in params else sys.maxsize
        finds = Inventory.find_by_quantity_range(lowerbound, upperbound)
        if len(inventories) == 0:
            inventories = finds
        else:
            inventories = list(set(inventories) & set(finds))
        params.pop(QUANTITY_HIGH, None)
        params.pop(QUANTITY_LOW, None)
    if RESTOCK_LEVEL in params:
        restock_level: int = params[RESTOCK_LEVEL]
        # if restock_level == 0, we should still execute the query
        if restock_level is not None:
            finds = Inventory.find_by_restock_level(restock_level)
            if len(inventories) == 0:
                inventories = finds
            else:
                inventories = list(set(inventories) & set(finds))
            params.pop(RESTOCK_LEVEL, None)
    if len(params) != 0:
        return bad_request("Invalid request parameters")
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
    if QUANTITY in params.keys() and params[QUANTITY] and ADDED_AMOUNT in params.keys() and params[ADDED_AMOUNT]:
        return bad_request("Ambiguous request with both QUANTITY and ADDED_AMOUNT")
    if QUANTITY in params.keys() and params[QUANTITY]:
        quantity = params[QUANTITY]
        if not isinstance(quantity, int) or quantity <= 0:
            return bad_request("Quantity must be positive integer")
        inventory.quantity = quantity
    if ADDED_AMOUNT in params.keys() and params[ADDED_AMOUNT]:
        added_amount = params[ADDED_AMOUNT]
        if not isinstance(added_amount, int) or added_amount <= 0:
            return bad_request("Quantity must be positive integer")
        inventory.quantity += added_amount
    if RESTOCK_LEVEL in params.keys() and params[RESTOCK_LEVEL]:
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


def check_content_type(content_type):
    """ Check that the media type is correct """
    if "Content-Type" in request.headers and request.headers["Content-Type"] == content_type:
        return
    app.logger.error(
        "Invalid Content-Type: [%s]", request.headers.get("Content-Type"))
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
          "Content-Type must be {}".format(content_type))
