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
from typing import Dict, List, Optional, ValuesView

from service import status  # HTTP Status Codes
from service.constants import (API_URL, AVAILABLE, CONDITION, CONTENT_TYPE,
                               POSTGRES_DATABASE_URI, PRODUCT_ID, QUANTITY,
                               RESTOCK_LEVEL)
from service.models import Condition, Inventory, db
from service.routes import app, init_db

from .factories import InventoryFactory

DATABASE_URI = os.getenv("DATABASE_URI", POSTGRES_DATABASE_URI)


class TestInventoryServer(unittest.TestCase):
    """ Test Cases for Inventory server """

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

    def __create_inventories(self, count):
        """ Factory method to create inventories in bulk """
        inventories: List[Inventory] = []
        for _ in range(count):
            inventory = InventoryFactory()
            resp = self.app.post(
                API_URL, json=inventory.serialize(), content_type="application/json")
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
            posted_inventory = resp.get_json()
            inventory.product_id = posted_inventory[PRODUCT_ID]
            inventories.append(inventory)
        return inventories

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    # ------------------------------------------------------------------
    # PATH: /
    # ------------------------------------------------------------------
    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # ------------------------------------------------------------------
    # PATH: /inventory
    # ------------------------------------------------------------------
    def test_get_all_inventory_200_ok(self):
        """ Get all Inventory: HTTP_200_OK """
        N = 5
        self.__create_inventories(N)
        resp = self.app.get(API_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_all_inventory_by_query_available_200_ok(self):
        """ Get all Inventory: HTTP_200_OK [?available={}] """
        count: Dict[bool, int] = {True: 0, False: 0}
        inventories: List[Inventory] = self.__create_inventories(10)
        for inventory in inventories:
            count[inventory.available] += 1
        for available in [True, False]:
            resp = self.app.get("{0}?available={1}".format(API_URL, available))
            data = resp.get_json()
            if isinstance(data, dict):
                error: Optional[str] = data["error"]
                if error:
                    self.assertEqual(resp.status_code,
                                     status.HTTP_404_NOT_FOUND)
            else:  # type(data) == list
                self.assertEqual(len(data), count[available])

    def test_get_all_inventory_by_query_product_id_200_ok(self):
        """ Get all Inventory: HTTP_200_OK [?product_id={}&available={}] """
        product_id = 1
        available = True
        url: str = "{0}?product_id={1}&available={2}".format(
            API_URL,
            product_id,
            available)
        resp = self.app.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)
        Inventory(product_id=product_id, condition=Condition.NEW,
                  quantity=2, available=available).create()
        Inventory(product_id=product_id, condition=Condition.OPEN_BOX,
                  quantity=2, available=available).create()
        Inventory(product_id=product_id, condition=Condition.USED,
                  quantity=2, available=available).create()
        resp = self.app.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        for inventory in data:
            self.assertEqual(inventory[PRODUCT_ID], product_id)
            self.assertEqual(inventory[AVAILABLE], available)

    def test_get_all_inventory_by_query_condition_200_ok(self):
        """ Get all Inventory: HTTP_200_OK [?condition={}&available={}] """
        condition = Condition.NEW
        available = True
        url: str = "{0}?condition={1}&available={2}".format(
            API_URL,
            condition.name,
            available)
        resp = self.app.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)
        Inventory(product_id=1, condition=condition,
                  quantity=2, available=available).create()
        Inventory(product_id=2, condition=condition,
                  quantity=2, available=available).create()
        Inventory(product_id=3, condition=Condition.USED,
                  quantity=2, available=available).create()
        resp = self.app.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        for inventory in data:
            self.assertEqual(inventory[CONDITION], condition.name)
            self.assertEqual(inventory[AVAILABLE], available)

    def test_get_all_inventory_by_query_quantity_200_ok(self):
        """ Get all Inventory: HTTP_200_OK [?quantity={}&available={}] """
        quantity = 100
        available = True
        url: str = "{0}?quantity={1}&available={2}".format(
            API_URL,
            quantity,
            available)
        resp = self.app.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)
        Inventory(product_id=1, condition=Condition.NEW,
                  quantity=quantity, available=available).create()
        Inventory(product_id=2, condition=Condition.NEW,
                  quantity=quantity, available=available).create()
        Inventory(product_id=3, condition=Condition.USED,
                  quantity=quantity, available=available).create()
        resp = self.app.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        for inventory in data:
            self.assertEqual(inventory[QUANTITY], quantity)
            self.assertEqual(inventory[AVAILABLE], available)

    def test_get_all_inventory_by_query_quantity_range_200_ok(self):
        """ Get all Inventory: HTTP_200_OK [?quantity_low={}quantity_high={}&available={}] """
        q1 = 100
        q2 = 200
        q3 = 300
        available = True
        url: str = "{0}?quantity_low={1}&quantity_high={2}&available={3}".format(
            API_URL,
            q2,
            q3,
            available)
        resp = self.app.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)
        Inventory(product_id=1, condition=Condition.NEW,
                  quantity=q1, available=available).create()
        Inventory(product_id=2, condition=Condition.NEW,
                  quantity=q2, available=available).create()
        Inventory(product_id=3, condition=Condition.NEW,
                  quantity=q3, available=available).create()
        resp = self.app.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        for inventory in data:
            self.assertGreaterEqual(inventory[QUANTITY], q2)
            self.assertLessEqual(inventory[QUANTITY], q3)

    def test_get_all_inventory_by_query_restock_level_200_ok(self):
        """ Get all Inventory: HTTP_200_OK [?restock_level={}&available={}] """
        restock_level = 100
        available = True
        url: str = "{0}?restock_level={1}&available={2}".format(
            API_URL,
            restock_level,
            available)
        resp = self.app.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)
        Inventory(product_id=1, condition=Condition.NEW, quantity=2,
                  restock_level=restock_level, available=available).create()
        Inventory(product_id=2, condition=Condition.USED, quantity=2,
                  restock_level=restock_level, available=available).create()
        Inventory(product_id=3, condition=Condition.OPEN_BOX, quantity=2,
                  restock_level=restock_level, available=available).create()
        resp = self.app.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        for inventory in data:
            self.assertEqual(inventory[RESTOCK_LEVEL], restock_level)
            self.assertEqual(inventory[AVAILABLE], available)

    def test_create_inventory_201_created(self):
        """ Create an inventory: HTTP_201_CREATED """
        inventory = InventoryFactory()
        resp = self.app.post(
            API_URL, json=inventory.serialize(), content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)
        data = resp.get_json()
        self.assertEqual(data[PRODUCT_ID], inventory.product_id)
        self.assertEqual(data[CONDITION], inventory.condition.name)
        self.assertEqual(data[QUANTITY], inventory.quantity)
        self.assertEqual(data[RESTOCK_LEVEL], inventory.restock_level)
        # Check that the location header was correct
        resp = self.app.get(
            "{0}/{1}/condition/{2}".format(
                API_URL,
                inventory.product_id,
                inventory.condition.name),
            content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        logging.debug("data = %s", data)
        self.assertEqual(data[PRODUCT_ID], inventory.product_id)
        self.assertEqual(data[CONDITION], inventory.condition.name)
        self.assertEqual(data[QUANTITY], inventory.quantity)
        self.assertEqual(data[RESTOCK_LEVEL], inventory.restock_level)

    def test_create_inventory_409_conflict(self):
        """ Create an inventory: HTTP_409_CONFLICT """
        inventory = InventoryFactory()
        resp = self.app.post(
            API_URL, json=inventory.serialize(), content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Post again
        resp = self.app.post(
            API_URL, json=inventory.serialize(), content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    # ------------------------------------------------------------------
    # PATH: /inventory/<product_id>/condition/<condition>
    # ------------------------------------------------------------------
    def test_get_inventory_404_not_found(self):
        """ Get an Inventory: HTTP_404_NOT_FOUND """
        bad_product_id = 1
        bad_condition = "NEW"
        resp = self.app.get(
            "{0}/{1}/condition/{2}".format(
                API_URL,
                bad_product_id,
                bad_condition),
            content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_inventory_404_not_found(self):
        """ Update an Inventory: HTTP_404_NOT_FOUND """
        bad_product_id = 1
        bad_condition = "NEW"
        resp = self.app.put(
            "{0}/{1}/condition/{2}".format(
                API_URL,
                bad_product_id,
                bad_condition),
            json={},
            content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_inventory_200_ok_true_added_amount(self):
        """ Update an Inventory: HTTP_200_OK [?added_amount=True] """
        inventory = InventoryFactory()
        resp = self.app.post(
            API_URL, json=inventory.serialize(), content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        url: str = "{0}/{1}/condition/{2}?added_amount=True".format(
            API_URL,
            inventory.product_id,
            inventory.condition.name)
        # Add amount to `quantity` and update `restock_level`
        resp = self.app.put(
            url,
            json={QUANTITY: 1000, RESTOCK_LEVEL: 400},
            content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Check the result
        resp = self.app.get(url, content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get_json()[QUANTITY], 1000 + inventory.quantity)
        self.assertEqual(resp.get_json()[RESTOCK_LEVEL], 400)

    def test_update_inventory_200_ok_false_added_amount(self):
        """ Update an Inventory: HTTP_200_OK [?added_amount=False] """
        inventory = InventoryFactory()
        resp = self.app.post(
            API_URL, json=inventory.serialize(), content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        url: str = "{0}/{1}/condition/{2}?added_amount=False".format(
            API_URL,
            inventory.product_id,
            inventory.condition.name)
        # Update `quantity` and update `restock_level`
        resp = self.app.put(
            url,
            json={QUANTITY: 2300, RESTOCK_LEVEL: 400},
            content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Check the result
        resp = self.app.get(url, content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get_json()[QUANTITY], 2300)
        self.assertEqual(resp.get_json()[RESTOCK_LEVEL], 400)

    def test_delete_inventory_204_no_content(self):
        """ Delete an inventory: HTTP_204_NO_CONTENT """
        inventory: Inventory = self.__create_inventories(1)[0]
        url: str = "{0}/{1}/condition/{2}".format(
            API_URL,
            inventory.product_id,
            inventory.condition.name)
        resp = self.app.delete(url, content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        # Make sure it was deleted
        resp = self.app.get(url, content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    # ------------------------------------------------------------------
    # PATH: /inventory/<product_id>/condition/<condition>/activate
    # ------------------------------------------------------------------
    def test_activate_inventory_200_ok(self):
        """ Activate an inventory: HTTP_200_OK """
        inventory = InventoryFactory()
        inventory.available = False
        resp = self.app.post(
            API_URL, json=inventory.serialize(), content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp = self.app.put(
            "{0}/{1}/condition/{2}/activate".format(
                API_URL,
                inventory.product_id,
                inventory.condition.name),
            content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Check the result
        resp = self.app.get(
            "{0}/{1}/condition/{2}".format(
                API_URL,
                inventory.product_id,
                inventory.condition.name),
            content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get_json()[AVAILABLE], True)

    def test_activate_inventory_404_not_found(self):
        """ Activate an inventory: HTTP_404_NOT_FOUND """
        bad_product_id = 1
        bad_condition = "NEW"
        resp = self.app.put(
            "{0}/{1}/condition/{2}/activate".format(
                API_URL,
                bad_product_id,
                bad_condition),
            content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_activate_inventory_409_conflict(self):
        """ Activate an inventory: HTTP_409_CONFLICT """
        inventory = InventoryFactory()
        inventory.available = True
        resp = self.app.post(
            API_URL, json=inventory.serialize(), content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp = self.app.put(
            "{0}/{1}/condition/{2}/activate".format(
                API_URL,
                inventory.product_id,
                inventory.condition.name),
            content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    # ------------------------------------------------------------------
    # PATH: /inventory/<product_id>/condition/<condition>/deactivate
    # ------------------------------------------------------------------
    def test_deactivate_inventory_200_ok(self):
        """ Deactivate an inventory: HTTP_200_OK """
        inventory = InventoryFactory()
        inventory.available = True
        resp = self.app.post(
            API_URL, json=inventory.serialize(), content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp = self.app.put(
            "{0}/{1}/condition/{2}/deactivate".format(
                API_URL,
                inventory.product_id,
                inventory.condition.name),
            content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Check the result
        resp = self.app.get(
            "{0}/{1}/condition/{2}".format(
                API_URL,
                inventory.product_id,
                inventory.condition.name),
            content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get_json()[AVAILABLE], False)

    def test_deactivate_inventory_404_not_found(self):
        """ Deactivate an inventory: HTTP_404_NOT_FOUND """
        bad_product_id = 1
        bad_condition = "NEW"
        resp = self.app.put(
            "{0}/{1}/condition/{2}/deactivate".format(
                API_URL,
                bad_product_id,
                bad_condition),
            content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_deactivate_inventory_409_conflict(self):
        """ Deactivate an inventory: HTTP_409_CONFLICT """
        inventory = InventoryFactory()
        inventory.available = False
        resp = self.app.post(
            API_URL, json=inventory.serialize(), content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp = self.app.put(
            "{0}/{1}/condition/{2}/deactivate".format(
                API_URL,
                inventory.product_id,
                inventory.condition.name),
            content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
