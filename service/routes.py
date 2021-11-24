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
GET    /inventory
      - Return a list of Inventory
POST   /inventory
      - Create an Inventory

GET    /inventory/{product_id}/condition/{condition}
      - Retrieve a single Inventory
DELETE /inventory/{product_id}/condition/{condition}
      - Delete an Inventory
PUT    /inventory/{product_id}/condition/{condition}
      - Update an Inventory

PUT    /inventory/{product_id}/condition/{condition}/activate
      - Activate an Inventory
PUT    /inventory/{product_id}/condition/{condition}/deactivate
      - Deactivate an Inventory
"""

import logging
import sys
from typing import Dict, List, Optional, Union

from flask import request
from flask_restx import Api, Resource, fields, inputs, reqparse

from service.constants import (ADDED_AMOUNT, AVAILABLE, CONDITION, PRODUCT_ID,
                               QUANTITY, QUANTITY_HIGH, QUANTITY_LOW,
                               RESTOCK_LEVEL)
from service.error_handlers import not_found
from service.models import Inventory

from . import app  # Import Flask application
from . import status  # HTTP Status Codes

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL


# Configure Swagger before initializing it
api = Api(app,
          version='1.0.0',
          title='Inventory Demo REST API Service',
          description='This is a sample server Inventory store server.',
          default='Inventory',
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


@app.before_first_request
def init_db():
    """ Initialize the SQLAlchemy app """
    global app
    Inventory.init_db(app)

##########################################################################
# R O U T E S
##########################################################################


@app.route("/")
def index():
    """ Root URL response """
    return app.send_static_file("index.html")


@api.route('/inventory', strict_slashes=False)
class InventoryCollection(Resource):
    """ Handles all interactions with collections of Pets
    GET  /inventory - Return all the Inventory
    POST /inventory - Add a new Inventory
    """
    # ------------------------------------------------------------------
    # RETRIEVE A LIST OF INVENTORY
    # ------------------------------------------------------------------
    @api.doc('get_inventories')
    @api.expect(inventory_args, validate=True)
    @api.marshal_list_with(inventory_model, code=status.HTTP_200_OK)
    def get(self):
        """
        Retrieve a list of Inventory

        This endpoint will return all the Inventory
        """

        app.logger.info("Request for inventory list")
        params: Dict[str, Union[int, str]] = request.args.to_dict()

        if len(params) == 0:
            inventories = Inventory.find_all()
            results = [inventory.serialize() for inventory in inventories]
            return results, status.HTTP_200_OK

        # TODO: Avoid using list intersection for more efficency
        inventories: List[Inventory] = []
        # Actually this condition will always be true in real use cases
        if AVAILABLE in params:
            available: bool = params[AVAILABLE]
            inventories = Inventory.find_by_available(available)
            params.pop(AVAILABLE, None)
        if PRODUCT_ID in params:
            product_id: int = params[PRODUCT_ID]
            founds = Inventory.find_by_product_id(product_id)
            if len(inventories) == 0:
                inventories = founds
            else:
                inventories = list(set(inventories) & set(founds))
            params.pop(PRODUCT_ID, None)
        if CONDITION in params:
            condition: str = params[CONDITION]
            founds = Inventory.find_by_condition(condition)
            if len(inventories) == 0:
                inventories = founds
            else:
                inventories = list(set(inventories) & set(founds))
            params.pop(CONDITION, None)
        if QUANTITY in params:
            quantity: int = params[QUANTITY]
            founds = Inventory.find_by_quantity(quantity)
            if len(inventories) == 0:
                inventories = founds
            else:
                inventories = list(set(inventories) & set(founds))
            params.pop(QUANTITY, None)
        if QUANTITY_HIGH in params or QUANTITY_LOW in params:
            lowerbound: int = params[QUANTITY_LOW] if QUANTITY_LOW in params else 0
            upperbound: int = params[QUANTITY_HIGH] if QUANTITY_HIGH in params else sys.maxsize
            founds = Inventory.find_by_quantity_range(lowerbound, upperbound)
            if len(inventories) == 0:
                inventories = founds
            else:
                inventories = list(set(inventories) & set(founds))
            params.pop(QUANTITY_HIGH, None)
            params.pop(QUANTITY_LOW, None)
        if RESTOCK_LEVEL in params:
            restock_level: int = params[RESTOCK_LEVEL]
            # if restock_level == 0, we should still execute the query
            if restock_level is not None:
                founds = Inventory.find_by_restock_level(restock_level)
                if len(inventories) == 0:
                    inventories = founds
                else:
                    inventories = list(set(inventories) & set(founds))
                params.pop(RESTOCK_LEVEL, None)
        results = [inventory.serialize() for inventory in inventories]
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW INVENTORY
    # ------------------------------------------------------------------

    @api.doc('add_inventory')
    @api.response(status.HTTP_409_CONFLICT, 'The Inventory already exists')
    @api.response(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 'Unsupported media type')
    @api.expect(inventory_model)
    @api.marshal_with(inventory_model, code=status.HTTP_201_CREATED)
    # TODO Add token required check
    def post(self):
        """
        Create an Inventory

        This endpoint will create a Inventory based on the data in the body that is posted
        """
        app.logger.info('Request to create an Inventory')
        inventory = Inventory()
        app.logger.debug(f"Payload = {api.payload}")
        inventory.deserialize(api.payload)
        inventory.validate_data()
        # Prevent create invenotory with same primary key
        if Inventory.find_by_product_id_condition(inventory.product_id, inventory.condition):
            api.abort(status.HTTP_409_CONFLICT,
                      "Inventory ({}, {}) already exists."
                      .format(inventory.product_id, inventory.condition))
        inventory.create()
        app.logger.info("Inventory ({}, {}) created."
                        .format(inventory.product_id, inventory.condition))
        location_url = api.url_for(InventoryResource, product_id=inventory.product_id,
                                   condition=inventory.condition.name, _external=True)
        return inventory.serialize(), status.HTTP_201_CREATED, {'Location': location_url}


@api.route('/inventory/<int:product_id>/condition/<string:condition>')
@api.param('product_id, condition', 'The Inventory identifiers')
class InventoryResource(Resource):
    """
    GET    /inventory/<product_id>/condition/<condition> - Return an Inventory
    PUT    /inventory/<product_id>/condition/<condition> - Update an Inventory
    DELETE /inventory/<product_id>/condition/<condition> - Delete an Inventory
    """

    # ------------------------------------------------------------------
    # RETRIEVE A INVENTORY
    # ------------------------------------------------------------------
    @api.doc('get_inventory')
    @api.response(status.HTTP_404_NOT_FOUND, 'Inventory not found')
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

        This endpoint will update an Inventory based on the body that is posted
        """
        app.logger.info("Request to update inventory with key ({}, {})"
                        .format(product_id, condition))
        inventory: Optional[Inventory] = Inventory.find_by_product_id_condition(
            product_id, condition)
        if not inventory:
            return not_found("Inventory with ({}, {})".format(product_id, condition))
        app.logger.debug(f"Payload = {api.payload}")
        # Get the query parameters
        params: Dict[str, Union[int, str]] = request.args.to_dict()
        added_amount: str = "False"  # False by default
        if ADDED_AMOUNT in params:
            added_amount = params[ADDED_AMOUNT]
        # To conform with expect
        if added_amount == "True":
            # We don't update restock_level
            inventory.quantity += api.payload[QUANTITY]
        else:
            inventory.quantity = api.payload[QUANTITY]
            inventory.restock_level = api.payload[RESTOCK_LEVEL]
        inventory.validate_data()
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


@api.route('/inventory/<int:product_id>/condition/<string:condition>/activate')
@api.param('product_id, condition', 'The Inventory identifiers')
class ActivateResource(Resource):
    """ Activate actions on an Inventory """
    @api.doc('activate_inventory')
    @api.response(status.HTTP_404_NOT_FOUND, 'Inventory not found')
    @api.response(status.HTTP_409_CONFLICT, 'The Inventory is already activated')
    def put(self, product_id: int, condition: str):
        """
        Activate an Inventory

        This endpoint will activate an Inventory
        """
        app.logger.info('Request to activate an Inventory')
        inventory: Optional[Inventory] = Inventory.find_by_product_id_condition(
            product_id, condition)
        if not inventory:
            api.abort(status.HTTP_404_NOT_FOUND,
                      "Inventory ({}, {}) NOT FOUND".format(product_id, condition))
        if inventory.available:
            api.abort(status.HTTP_409_CONFLICT,
                      "Inventory ({}, {}) is already available.".format(product_id, condition))
        inventory.available = True
        inventory.update()
        app.logger.info('Inventory ({}, {}) is activated!'.format(
            product_id, condition))
        return inventory.serialize(), status.HTTP_200_OK


@api.route('/inventory/<int:product_id>/condition/<string:condition>/deactivate')
@api.param('product_id, condition', 'The Inventory identifiers')
class DeactivateResource(Resource):
    """ Deactivate actions on an Inventory """
    @api.doc('deactivate_inventory')
    @api.response(status.HTTP_404_NOT_FOUND, 'Inventory not found')
    @api.response(status.HTTP_409_CONFLICT, 'The Inventory is already deactivated')
    def put(self, product_id: int, condition: str):
        """
        Deactivate an Inventory

        This endpoint will deactivate an Inventory
        """
        app.logger.info('Request to deactivate an Inventory')
        inventory: Optional[Inventory] = Inventory.find_by_product_id_condition(
            product_id, condition)
        if not inventory:
            api.abort(status.HTTP_404_NOT_FOUND,
                      "Inventory ({}, {}) NOT FOUND".format(product_id, condition))
        if not inventory.available:
            api.abort(status.HTTP_409_CONFLICT,
                      "Inventory ({}, {}) is already unavailable.".format(product_id, condition))
        inventory.available = False
        inventory.update()
        app.logger.info('Inventory ({}, {}) is deactivated!'.format(
            product_id, condition))
        return inventory.serialize(), status.HTTP_200_OK
