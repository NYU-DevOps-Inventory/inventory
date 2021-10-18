# Copyright 2016, 2021 John J. Rofrano. All Rights Reserved.
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

# -----------------------------------------------------------
# Modified by DevOps Course Fall 2021 Squad - Inventory Team
# Members:
#      Chen, Peng-Yu | pyc305@nyu.edu | New York | UTC-5
#      Lai, Yu-Wen   | yl8332@nyu.edu | New York | UTC-5
#      Zhang, Haoran | hz2613@nyu.edu | New York | UTC-5
#      Wen, Xuezhou  | xw2447@nyu.edu | New York | UTC-5
#      Hung, Ginkel  | ch3854@nyu.edu | New York | UTC-5
#
# Resource URL: /inventory
# Description:
#      The inventory resource keeps track of how many of each product we
#      have in our warehouse. At a minimum it should reference a product and the
#      quantity on hand. Inventory should also track restock levels and the condition
#      of the item (i.e., new, open box, used). Restock levels will help you know
#      when to order more products. Being able to query products by their condition
#      (e.g., new, used) could be very useful.
# -----------------------------------------------------------

"""
Inventory API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN

While debugging just these tests it's convinient to use this:
    nosetests --stop tests/test_routes.py:TestInventoryServer
"""

import logging
import os
import unittest

from urllib.parse import quote_plus
from service import status  # HTTP Status Codes
from service.models import db
from service.routes import app, init_db
from .factories import InventoryFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/inventory"

######################################################################
#  T E S T   C A S E S
######################################################################


class TestInventoryServer(unittest.TestCase):
    """ Inventory API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        """ Runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################
    def test_create_inventory(self):
        """ Create a new inventory """
        test_inventory = InventoryFactory()
        logging.debug(test_inventory)
        resp = self.app.post(
            BASE_URL, json=test_inventory.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_inventory = resp.get_json()
        self.assertEqual(
            new_inventory["product_id"], test_inventory.product_id, "Product_id do not match")
        self.assertEqual(
            new_inventory["condition"], test_inventory.condition.name, "Condition do not match")
        self.assertEqual(
            new_inventory["quantity"], test_inventory.quantity, "Quantity does not match"
        )
        self.assertEqual(
            new_inventory["restock_level"], test_inventory.restock_level, "Restock_level does not match"
        )
        # TODO: After implementing "GET" method, check that the location header was correct.

    def test_create_inventory_no_data(self):
        """ Create an inventory with missing data """
        resp = self.app.post(
            BASE_URL, json={}, content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_inventory_bad_condition(self):
        """ Create a Inventory with bad condition data """
        inventory = InventoryFactory()
        logging.debug(inventory)
        # change condition to a bad string
        test_pet = inventory.serialize()
        test_pet["condition"] = "new"    # wrong case
        resp = self.app.post(
            BASE_URL, json=test_pet, content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_pet_no_content_type(self):
        """ Create a Inventory with no content type """
        resp = self.app.post(BASE_URL)
        self.assertEqual(resp.status_code,
                         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_index(self):
        """ Test index call """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
