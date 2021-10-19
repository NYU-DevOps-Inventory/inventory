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
from service.models import Condition, db
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
    def _create_inventories(self, count):
        """ Factory method to create pets in bulk """
        inventories = []
        for _ in range(count):
            test_inventory = InventoryFactory()
            resp = self.app.post(
                BASE_URL, json=test_inventory.serialize(), content_type="application/json"
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test inventory"
            )
            new_inventory = resp.get_json()
            test_inventory.product_id = new_inventory["product_id"]
            inventories.append(test_inventory)
        return inventories

    ######################################################################
    # Testing POST

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
        # Check that the location header was correct
        resp = self.app.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_inventory = resp.get_json()
        self.assertEqual(
            new_inventory["product_id"], test_inventory.product_id, "Product_id do not match")
        self.assertEqual(
            new_inventory["condition"], test_inventory.condition.name, "Condition do not match"
        )
        self.assertEqual(
            new_inventory["quantity"], test_inventory.quantity, "Quantity does not match"
        )
        self.assertEqual(
            new_inventory["restock_level"], test_inventory.restock_level, "Restock_level does not match"
        )

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
        test_inventory = inventory.serialize()
        test_inventory["condition"] = "new"    # wrong case
        resp = self.app.post(
            BASE_URL, json=test_inventory, content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_inventory_no_content_type(self):
        """ Create a Inventory with no content type """
        resp = self.app.post(BASE_URL)
        self.assertEqual(resp.status_code,
                         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    ######################################################################
    # Testing GET
    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], "Inventory REST API Service")

    def test_get_inventory_list(self):
        """ Get a list of Inventory """
        count = 5
        self._create_inventories(count)
        resp = self.app.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), count)

    def test_get_inventory_by_pid(self):
        """ Get Inventory by [product_id] """
        N = 5
        count = 0
        inventories = self._create_inventories(N)
        for inv in inventories:
            resp = self.app.get(
                "{0}/{1}".format(BASE_URL, inv.product_id), content_type="application/json")
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            count += len(resp.get_json())
        self.assertEqual(count, N)

    def test_get_inventory_by_pid_not_found(self):
        """ Get Inventory by [product_id] that not found """
        resp = self.app.get("{0}/{1}".format(BASE_URL, 0),
                            content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_inventory_by_condition(self):
        """ Get Inventory by [condition] """
        count_new = 0
        count_open = 0
        count_used = 0
        inventories = self._create_inventories(10)
        for inv in inventories:
            if inv.condition == Condition.NEW:
                count_new += 1
            elif inv.condition == Condition.OPEN_BOX:
                count_open += 1
            elif inv.condition == Condition.USED:
                count_used += 1

        resp = self.app.get("{0}/condition/NEW".format(BASE_URL),
                            content_type="application/json")
        if resp.status_code == status.HTTP_200_OK:
            count = len(resp.get_json())
            self.assertEqual(count, count_new)

        resp = self.app.get("{0}/condition/OPEN_BOX".format(BASE_URL),
                            content_type="application/json")
        if resp.status_code == status.HTTP_200_OK:
            count = len(resp.get_json())
            self.assertEqual(count, count_open)

        resp = self.app.get("{0}/condition/USED".format(BASE_URL),
                            content_type="application/json")
        if resp.status_code == status.HTTP_200_OK:
            count = len(resp.get_json())
            self.assertEqual(count, count_used)

    def test_get_inventory_by_pid_condition(self):
        """Get an Inventory by [product_id, condition]"""
        test_inventory = self._create_inventories(1)[0]
        pid = test_inventory.product_id
        condition = test_inventory.condition.name
        resp = self.app.get("{0}/{1}/condition/{2}".format(BASE_URL,
                                                           pid, condition), content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["product_id"], pid)
        self.assertEqual(data["condition"], condition)

    def test_update_inventory(self):
        """Update an existing record in Inventory"""
        # create a record in Inventory
        inventory = InventoryFactory()
        resp = self.app.post(
            BASE_URL, json=inventory.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # update the record
        new_inventory = resp.get_json()
        logging.debug(new_inventory)
        new_inventory["quantity"] = 999
        new_inventory["restock_level"] = 99
        resp = self.app.put(
            "/inventory/{}/condition/{}".format(new_inventory["product_id"], new_inventory["condition"]),
            json=new_inventory,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_inventory = resp.get_json()
        self.assertEqual(updated_inventory["quantity"], 999)
        self.assertEqual(updated_inventory["restock_level"], 99)
    
    def test_update_non_exist_inventory(self):
        """Update a non-existing record in Inventory"""
        # update a record
        inventory = InventoryFactory()
        test_inventory = inventory.serialize()
        resp = self.app.put(
            "/inventory/{}/condition/{}".format(test_inventory["product_id"],test_inventory["condition"]),
            json=test_inventory,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_inventory(self):
        """ Delete an inventory """
        test_invenotory = self._create_inventories(1)[0]
        resp = self.app.delete(
            "{0}/{1}/condition/{2}".format(BASE_URL, test_invenotory.product_id, test_invenotory.condition.name), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get(
            "{}/{}/condition/{}".format(BASE_URL, test_invenotory.product_id, test_invenotory.condition.name), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_inventory_by_pid_condition_not_found(self):
        """ Get an Inventory by [product_id, condition] that not found """
        resp = self.app.get(
            "{0}/0/condition/NEW".format(BASE_URL), content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
