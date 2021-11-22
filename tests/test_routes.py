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

import json
import logging
import os
import unittest
from typing import Dict, List, Optional, Set
from urllib.parse import quote_plus

from service import status  # HTTP Status Codes
from service.constants import ADDED_AMOUNT, CONDITION, QUANTITY, RESTOCK_LEVEL
from service.error_handlers import bad_request
from service.models import Condition, DataValidationError, Inventory, db
from service.routes import app, init_db

from .factories import InventoryFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/inventory"
API_BASE_URL = "/api/inventory"

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

    def _create_inventories(self, count):
        """ Factory method to create inventories in bulk """
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
    # TEST CASES
    ######################################################################

    def test_create_inventory(self):
        """ Create a new inventory """
        test_inventory = InventoryFactory()
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

    def test_create_inventory_already_exist(self):
        """ Create an inventory already exists """
        test_inventory = InventoryFactory()
        resp = self.app.post(
            BASE_URL, json=test_inventory.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Post again
        resp = self.app.post(
            BASE_URL, json=test_inventory.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

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

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_inventory_list(self):
        """ Get a list of Inventory """
        N = 5
        self._create_inventories(N)
        resp = self.app.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), N)

    def test_get_inventory_by_query_product_id(self):
        """ Get a list of Inventory by query [product_id] """
        N = 5
        count = 0
        inventories: List[Inventory] = self._create_inventories(N)
        for inv in inventories:
            resp = self.app.get(
                f"{BASE_URL}?product_id={inv.product_id}", content_type="application/json")
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            count += len(resp.get_json())
        self.assertEqual(count, N)

    def test_get_inventory_by_query_condition(self):
        """ Get a list of Inventory by query [condition] """
        count: Dict[str, int] = {Condition.NEW.name: 0,
                                 Condition.OPEN_BOX.name: 0,
                                 Condition.USED.name: 0}
        inventories: List[Inventory] = self._create_inventories(5)
        for inv in inventories:
            count[inv.condition.name] += 1
        for condition in Condition:
            resp = self.app.get(f"{BASE_URL}?condition={condition.name}",
                                content_type="application/json")
            data = resp.get_json()
            if isinstance(data, dict):
                error: Optional[str] = data["error"]
                if error:
                    self.assertEqual(resp.status_code,
                                     status.HTTP_404_NOT_FOUND)
            else:  # type(data) == list
                self.assertEqual(len(data), count[condition.name])

    def test_get_inventory_by_query_product_id_and_condition(self):
        """ Get an Inventory by query [product_id] and [condition] """
        N = 5
        inventories: List[Inventory] = self._create_inventories(N)
        inventories_set: Set[Inventory] = set()
        for inv in inventories:
            resp = self.app.get(
                "{0}/{1}/condition/{2}".format(
                    API_BASE_URL,
                    inv.product_id,
                    inv.condition.name),
                content_type="application/json")
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            inventories_set.add(json.dumps(resp.get_json()))
        self.assertEqual(len(inventories_set), N)

    def test_get_inventory_by_query_product_id_and_condition_not_found(self):
        """ Get Inventory by [product_id] and [condition] that not found """
        resp = self.app.get(
            "{0}/1/condition/NEW".format(API_BASE_URL),
            content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_inventory_by_query_quantity(self):
        """ Get a list of Inventory by query [quantity] """
        N = 5
        count = 0
        inventories: List[Inventory] = self._create_inventories(N)
        for inv in inventories:
            resp = self.app.get(
                f"{BASE_URL}?quantity={inv.quantity}", content_type="application/json")
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            count += len(resp.get_json())
        self.assertEqual(count, N)

    def test_get_inventory_by_query_quantity_range(self):
        """ Get a list of Inventory by query [quantity range] """
        N = 5
        inventories: List[Inventory] = self._create_inventories(N)
        lowerbound = min(inv.quantity for inv in inventories)
        upperbound = max(inv.quantity for inv in inventories)
        resp = self.app.get(
            f"{BASE_URL}?quantity_low={lowerbound}&quantity_high={upperbound}", content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(N, len(resp.get_json()))
        resp = self.app.get(
            f"{BASE_URL}?quantity_low={lowerbound}", content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(N, len(resp.get_json()))
        resp = self.app.get(
            f"{BASE_URL}?quantity_high={upperbound}", content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(N, len(resp.get_json()))

    def test_get_inventory_by_query_restock_level(self):
        """ Get a list of Inventory by query [restock_level] """
        N = 5
        count = 0
        inventories: List[Inventory] = self._create_inventories(N)
        for inv in inventories:
            resp = self.app.get(
                f"{BASE_URL}?restock_level={inv.restock_level}", content_type="application/json")
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            count += len(resp.get_json())
        self.assertEqual(count, N)

    def test_get_inventory_by_query_available(self):
        """ Get a list of Inventory by query [available] """
        count: Dict[bool, int] = {True: 0,
                                  False: 0}
        inventories: List[Inventory] = self._create_inventories(5)
        for inv in inventories:
            count[inv.available] += 1
        for available in [True, False]:
            resp = self.app.get(f"{BASE_URL}?available={available}",
                                content_type="application/json")
            data = resp.get_json()
            if isinstance(data, dict):
                error: Optional[str] = data["error"]
                if error:
                    self.assertEqual(resp.status_code,
                                     status.HTTP_404_NOT_FOUND)
            else:  # type(data) == list
                self.assertEqual(len(data), count[available])

    def test_get_inventory_by_query_product_id_and_other_attribute(self):
        """Get an Inventory by query [product_id] and other attribute"""
        # Inventory with {product_id: 1, available: True}
        inventory1 = InventoryFactory()
        inventory1.product_id = 1
        inventory1.condition = Condition.NEW
        inventory1.available = True
        inventory1.create()
        # Invenotry with {product_id: 1, available: True}
        inventory2 = InventoryFactory()
        inventory2.product_id = 1
        inventory2.condition = Condition.USED
        inventory2.available = True
        inventory2.create()
        # Invenotry with {product_id: 2, available: True}
        inventory3 = InventoryFactory()
        inventory3.product_id = 2
        inventory3.condition = Condition.NEW
        inventory3.available = True
        inventory3.create()
        resp = self.app.get(
            f"{BASE_URL}?available=True&product_id=1", content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        for i in data:
            self.assertEqual(i["product_id"], 1)
            self.assertEqual(i["available"], True)

    def test_get_inventory_by_query_condition_and_other_attribute(self):
        """Get an Inventory by query [condition] and other attribute"""
        # Inventory with {condition: NEW, available: True}
        inventory1 = InventoryFactory()
        inventory1.product_id = 1
        inventory1.condition = Condition.NEW
        inventory1.available = True
        inventory1.create()
        # Invenotry with {condition: NEW, available: True}
        inventory2 = InventoryFactory()
        inventory2.product_id = 2
        inventory2.condition = Condition.NEW
        inventory2.available = True
        inventory2.create()
        # Invenotry with {condition: USED, available: True}
        inventory3 = InventoryFactory()
        inventory3.product_id = 3
        inventory3.condition = Condition.USED
        inventory3.available = True
        inventory3.create()
        resp = self.app.get(
            f"{BASE_URL}?available=True&condition=NEW", content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        for i in data:
            self.assertEqual(i["condition"], Condition.NEW.name)
            self.assertEqual(i["available"], True)

    def test_get_inventory_by_query_quantity_and_other_attribute(self):
        """Get an Inventory by query [quantity] and other attribute"""
        # Inventory with {quantity: 100, available: True}
        inventory1 = InventoryFactory()
        inventory1.product_id = 1
        inventory1.condition = Condition.NEW
        inventory1.quantity = 100
        inventory1.available = True
        inventory1.create()
        # Invenotry with {quantity: 100, available: True}
        inventory2 = InventoryFactory()
        inventory2.product_id = 2
        inventory2.condition = Condition.NEW
        inventory2.quantity = 100
        inventory2.available = True
        inventory2.create()
        # Invenotry with {quantity: 200, available: True}
        inventory3 = InventoryFactory()
        inventory3.product_id = 3
        inventory3.condition = Condition.NEW
        inventory3.quantity = 200
        inventory3.available = True
        inventory3.create()
        resp = self.app.get(
            f"{BASE_URL}?available=True&quantity=100", content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        for i in data:
            self.assertEqual(i["quantity"], 100)
            self.assertEqual(i["available"], True)
        # Test Quantity_low
        resp = self.app.get(
            f"{BASE_URL}?available=True&quantity_low=200", content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        for i in data:
            self.assertEqual(i["quantity"], 200)
            self.assertEqual(i["available"], True)
        # Test Quantity_high
        resp = self.app.get(
            f"{BASE_URL}?available=True&quantity_high=100", content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        for i in data:
            self.assertEqual(i["quantity"], 100)
            self.assertEqual(i["available"], True)

    def test_get_inventory_by_query_restock_level_and_other_attribute(self):
        """Get an Inventory by query [restock_level] and other attribute"""
        # Inventory with {restock_level: 100, available: True}
        inventory1 = InventoryFactory()
        inventory1.product_id = 1
        inventory1.condition = Condition.USED
        inventory1.restock_level = 100
        inventory1.available = True
        inventory1.create()
        # Invenotry with {restock_level: 100, available: True}
        inventory2 = InventoryFactory()
        inventory2.product_id = 2
        inventory2.condition = Condition.USED
        inventory2.restock_level = 100
        inventory2.available = True
        inventory2.create()
        # Invenotry with {restock_level: 200, available: True}
        inventory3 = InventoryFactory()
        inventory3.product_id = 3
        inventory3.condition = Condition.USED
        inventory3.restock_level = 200
        inventory3.available = True
        inventory3.create()
        resp = self.app.get(
            f"{BASE_URL}?available=True&restock_level=100", content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        for i in data:
            self.assertEqual(i["restock_level"], 100)
            self.assertEqual(i["available"], True)

    def test_get_inventory_bad_request(self):
        """ Get a list of Inventory that bad request """
        resp = self.app.get("/inventory?bad=0")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_inventory_by_product_id(self):
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

    def test_get_inventory_by_product_id_not_found(self):
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

    def test_get_inventory_by_product_id_condition(self):
        """Get an Inventory by [product_id, condition]"""
        test_inventory = self._create_inventories(1)[0]
        product_id = test_inventory.product_id
        condition = test_inventory.condition.name
        resp = self.app.get("{0}/{1}/condition/{2}".format(BASE_URL,
                                                           product_id, condition), content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["product_id"], product_id)
        self.assertEqual(data["condition"], condition)

    def test_update_inventory(self):
        """Update an existing record in Inventory"""
        # create a record in Inventory
        inventory = InventoryFactory()
        inventory.condition = Condition.NEW
        resp = self.app.post(
            BASE_URL, json=inventory.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # update quantity and restock_level
        resp = self.app.put("/inventory/{}/condition/{}".format(
            inventory.product_id, inventory.condition.name),
            json={QUANTITY: 1000, RESTOCK_LEVEL: 400},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_inventory = resp.get_json()
        self.assertEqual(updated_inventory[QUANTITY], 1000)
        self.assertEqual(updated_inventory[RESTOCK_LEVEL], 400)
        # update quantity by added_amount
        resp = self.app.put("/inventory/{}/condition/{}".format(
            inventory.product_id, inventory.condition.name),
            json={ADDED_AMOUNT: 500},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_inventory = resp.get_json()
        self.assertEqual(updated_inventory[QUANTITY], 1500)
        # update bad quantity
        bad_quantities = [-100, 200.5]
        for bq in bad_quantities:
            resp = self.app.put("/inventory/{}/condition/{}".format(
                inventory.product_id, inventory.condition.name),
                json={QUANTITY: bq},
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # update bad restock_level
        bad_request_levels = [-100, 200.5]
        for brl in bad_request_levels:
            resp = self.app.put("/inventory/{}/condition/{}".format(
                inventory.product_id, inventory.condition.name),
                json={RESTOCK_LEVEL: brl},
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # update bad added_amount
        bad_added_amounts = [-100, 200.5]
        for baa in bad_added_amounts:
            resp = self.app.put("/inventory/{}/condition/{}".format(
                inventory.product_id, inventory.condition.name),
                json={ADDED_AMOUNT: baa},
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # update with both quantity and added_amount
        resp = self.app.put("/inventory/{}/condition/{}".format(
            inventory.product_id, inventory.condition.name),
            json={QUANTITY: 1000, ADDED_AMOUNT: 500},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_used_restock_level(self):
        """Update the restock_level of a USED record"""
        # create a record in Inventory
        inventory = InventoryFactory()
        inventory.condition = Condition.USED
        resp = self.app.post(
            BASE_URL, json=inventory.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # update the record
        resp = self.app.put("/inventory/{}/condition/{}".format(
            inventory.product_id, inventory.condition.name),
            json={RESTOCK_LEVEL: 400},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_activate_inventory(self):
        """Activate an existing record in Inventory"""
        inventory = InventoryFactory()
        inventory.available = False
        json = inventory.serialize()
        resp = self.app.post(
            BASE_URL, json=json, content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # update the record
        resp = self.app.put("/inventory/{}/condition/{}/activate".format(
            json["product_id"], json["condition"]),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_inventory = resp.get_json()
        self.assertEqual(updated_inventory["available"], True)

    def test_deactivate_inventory(self):
        """Deactivate an existing record in Inventory"""
        inventory = InventoryFactory()
        inventory.available = True
        json = inventory.serialize()
        resp = self.app.post(
            BASE_URL, json=json, content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # update the record
        resp = self.app.put("/inventory/{}/condition/{}/deactivate".format(
            json["product_id"], json["condition"]),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_inventory = resp.get_json()
        self.assertEqual(updated_inventory["available"], False)

    def test_update_non_exist_inventory(self):
        """Update a non-existing record in Inventory"""
        # update a record
        resp = self.app.put(
            "/inventory/{}/condition/{}".format(100, "NEW"),
            json={QUANTITY: 500},
            content_type="application/json"
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

    def test_get_inventory_by_product_id_condition_not_found(self):
        """ Get an Inventory by [product_id, condition] that not found """
        resp = self.app.get(
            "{0}/0/condition/NEW".format(BASE_URL), content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_serialize_an_inventory(self):
        """ Test serialization of an Inventory """
        inventory = InventoryFactory()
        data = inventory.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("product_id", data)
        self.assertEqual(data["product_id"], inventory.product_id)
        self.assertIn("condition", data)
        self.assertEqual(data["condition"], inventory.condition.name)
        self.assertIn("quantity", data)
        self.assertEqual(data["quantity"], inventory.quantity)
        self.assertIn("restock_level", data)
        self.assertEqual(data["restock_level"], inventory.restock_level)

    def test_deserialize_an_inventory(self):
        """ Test deserialization of an Inventory """
        data = {
            "product_id": 1,
            "condition": "NEW",
            "quantity": 2,
            "restock_level": 3,
            "available": True
        }
        inventory = Inventory()
        inventory.deserialize(data)
        self.assertNotEqual(inventory, None)
        self.assertEqual(inventory.product_id, 1)
        self.assertEqual(inventory.condition.name, "NEW")
        self.assertEqual(inventory.quantity, 2)
        self.assertEqual(inventory.restock_level, 3)
        self.assertEqual(inventory.available, True)

    def test_deserialize_missing_data(self):
        """ Test deserialization of an Inventory with missing data """
        data = {
            "product_id": 1,
            "quantity": 2,
            "restock_level": 3,
        }
        inventory = Inventory()
        self.assertRaises(DataValidationError, inventory.deserialize, data)

    def test_deserialize_bad_data(self):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        inventory = Inventory()
        self.assertRaises(DataValidationError, inventory.deserialize, data)

    def test_deserialize_bad_condition(self):
        """ Test deserialization of data with bad condition """
        test_inventory = InventoryFactory()
        data = test_inventory.serialize()
        data["condition"] = 'new'  # wrong case
        inventory = Inventory()
        self.assertRaises(DataValidationError, inventory.deserialize, data)

    def test_deserialize_bad_quantity(self):
        """ Test deserialization of data with bad quantity """
        test_inventory = InventoryFactory()
        data = test_inventory.serialize()
        data["quantity"] = 'string'  # wrong type
        inventory = Inventory()
        self.assertRaises(DataValidationError, inventory.deserialize, data)

    def test_deserialize_bad_restock_level(self):
        """ Test deserialization of data with bad restock_level """
        test_inventory = InventoryFactory()
        data = test_inventory.serialize()
        data["restock_level"] = 'string'  # wrong type
        inventory = Inventory()
        self.assertRaises(DataValidationError, inventory.deserialize, data)

    def test_deserialize_bad_available(self):
        """ Test deserialization of data with bad available """
        test_inventory = InventoryFactory()
        data = test_inventory.serialize()
        data["available"] = 'string'  # wrong type
        inventory = Inventory()
        self.assertRaises(DataValidationError, inventory.deserialize, data)
