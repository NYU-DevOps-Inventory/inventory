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
Test cases for Inventory Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convinient to use this:
    nosetests --stop tests/test_models.py:TestInventoryModel
"""
import logging
import os
import unittest

from service import app
from service.models import Condition, DataValidationError, Inventory, db
from werkzeug.exceptions import NotFound

from tests.factories import InventoryFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  I N V E N T O R Y   M O D E L   T E S T   C A S E S
######################################################################


class TestInventoryModel(unittest.TestCase):
    """ Test Cases for Inventory Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Inventory.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################
    def test_repr_of_an_inventory(self):
        product_id = 1
        condition = Condition.NEW
        inventory = Inventory(product_id=product_id,
                              condition=condition, quantity=2, restock_level=3)
        self.assertIsNot(inventory, None)
        self.assertEqual(
            str(inventory), f"<Inventory product_id=[{product_id}] with condition=[{condition}] condition>")

    def test_create_an_inventory(self):
        """ Create an inventory and assert that it exists """
        inventory = Inventory(
            product_id=1, condition=Condition.NEW, quantity=2, restock_level=3, available=True)
        self.assertTrue(inventory != None)
        self.assertEqual(inventory.product_id, 1)
        self.assertEqual(inventory.condition, Condition.NEW)
        self.assertEqual(inventory.quantity, 2)
        self.assertEqual(inventory.restock_level, 3)
        self.assertEqual(inventory.available, True)

    def test_update_inventory(self):
        """ Update an existing record in inventory """
        inventory = Inventory(
            product_id=1, condition=Condition.NEW, quantity=100, restock_level=40, available=True)
        inventory.create()
        orininal_product_id = inventory.product_id
        original_condition = inventory.condition
        inventory.quantity = 70
        inventory.restock_level = 50
        inventory.available = False
        inventory.update()
        latest_inventory = Inventory.all()
        self.assertEqual(len(latest_inventory), 1)
        self.assertEqual(latest_inventory[0].product_id, orininal_product_id)
        self.assertEqual(latest_inventory[0].condition, original_condition)
        self.assertEqual(latest_inventory[0].quantity, 70)
        self.assertEqual(latest_inventory[0].restock_level, 50)
        self.assertEqual(latest_inventory[0].available, False)

    def test_add_an_inventory(self):
        """ Create an inventory and add it to the database """
        inventories = Inventory.all()
        self.assertEqual(inventories, [])
        inventory = Inventory(
            product_id=1, condition=Condition.NEW, quantity=2, restock_level=3, available=True)
        self.assertTrue(inventory != None)
        self.assertEqual(inventory.product_id, 1)
        inventory.create()
        # Assert that it shows up in the database
        inventories = Inventory.all()
        self.assertEqual(len(inventories), 1)

    def test_delete_an_inventory(self):
        """ Delete an inventory """
        inventory = InventoryFactory()
        inventory.create()
        self.assertEqual(len(Inventory.all()), 1)
        # delete the inventory and make sure it isn't in the database
        inventory.delete()
        self.assertEqual(len(Inventory.all()), 0)

    def test_find_by_product_id_condition(self):
        """ Find an Inventory by [product_id] and [condition] """
        inventory = Inventory(
            product_id=123, condition=Condition.NEW, quantity=2, restock_level=10, available=True)
        if not Inventory.find_by_product_id_condition(inventory.product_id, inventory.condition):
            inventory.create()
        result = Inventory.find_by_product_id_condition(
            inventory.product_id, inventory.condition)
        self.assertIsNot(result, None)
        self.assertEqual(result.product_id, inventory.product_id)
        self.assertEqual(result.condition, inventory.condition)
        self.assertEqual(result.quantity, inventory.quantity)
        self.assertEqual(result.restock_level, inventory.restock_level)
        self.assertEqual(result.available, inventory.available)

    def test_find_by_product_id(self):
        """ Find Inventory by [product_id] """
        inventory = Inventory(
            product_id=124, condition=Condition.NEW, quantity=1, restock_level=10, available=True)
        if not Inventory.find_by_product_id_condition(inventory.product_id, inventory.condition):
            inventory.create()
        inventory = Inventory(
            product_id=124, condition=Condition.USED, quantity=4, available=True)
        if not Inventory.find_by_product_id_condition(inventory.product_id, inventory.condition):
            inventory.create()
        inventories = Inventory.find_by_product_id(inventory.product_id)
        self.assertEqual(len(list(inventories)), 2)

    def test_find_by_condition(self):
        """ Find an Inventory by [condition] """
        inventory = Inventory(
            product_id=333, condition=Condition.NEW, quantity=1, restock_level=10, available=True)
        if not Inventory.find_by_product_id_condition(inventory.product_id, inventory.condition):
            inventory.create()
        inventory = Inventory(
            product_id=344, condition=Condition.NEW, quantity=1, restock_level=10, available=True)
        if not Inventory.find_by_product_id_condition(inventory.product_id, inventory.condition):
            inventory.create()
        inventories = Inventory.find_by_condition(inventory.condition)
        self.assertEqual(len(list(inventories)), 2)

    def test_find_by_quantity(self):
        """ Find an Inventory by [quantity] """
        inventory = Inventory(
            product_id=333, condition=Condition.NEW, quantity=1, restock_level=10, available=True)
        if not Inventory.find_by_product_id_condition(inventory.product_id, inventory.condition):
            inventory.create()
        inventory = Inventory(
            product_id=344, condition=Condition.NEW, quantity=1, restock_level=10, available=True)
        if not Inventory.find_by_product_id_condition(inventory.product_id, inventory.condition):
            inventory.create()
        inventory = Inventory(
            product_id=345, condition=Condition.NEW, quantity=2, restock_level=5, available=True)
        if not Inventory.find_by_product_id_condition(inventory.product_id, inventory.condition):
            inventory.create()
        inventories = Inventory.find_by_quantity(1)
        self.assertEqual(len(list(inventories)), 2)
        inventories = Inventory.find_by_quantity(2)
        self.assertEqual(len(list(inventories)), 1)

    def test_find_by_quantity_range(self):
        """ Find Inventory by [quantity range] """
        inventory = Inventory(
            product_id=333, condition=Condition.NEW, quantity=2, restock_level=10, available=True)
        if not Inventory.find_by_product_id_condition(inventory.product_id, inventory.condition):
            inventory.create()
        inventory = Inventory(
            product_id=344, condition=Condition.NEW, quantity=3, restock_level=10, available=True)
        if not Inventory.find_by_product_id_condition(inventory.product_id, inventory.condition):
            inventory.create()
        inventory = Inventory(
            product_id=345, condition=Condition.NEW, quantity=5, restock_level=5, available=True)
        if not Inventory.find_by_product_id_condition(inventory.product_id, inventory.condition):
            inventory.create()
        inventories = Inventory.find_by_quantity_range(2, 6)
        self.assertEqual(len(list(inventories)), 3)
        inventories = Inventory.find_by_quantity_range(6, 10)
        self.assertEqual(len(list(inventories)), 0)

    def test_find_by_restock_level(self):
        """ Find an Inventory by [restock_level] """
        inventory = Inventory(
            product_id=333, condition=Condition.NEW, quantity=1, restock_level=10, available=True)
        if not Inventory.find_by_product_id_condition(inventory.product_id, inventory.condition):
            inventory.create()
        inventory = Inventory(
            product_id=344, condition=Condition.NEW, quantity=1, restock_level=10, available=True)
        if not Inventory.find_by_product_id_condition(inventory.product_id, inventory.condition):
            inventory.create()
        inventory = Inventory(
            product_id=345, condition=Condition.NEW, quantity=1, restock_level=5, available=True)
        if not Inventory.find_by_product_id_condition(inventory.product_id, inventory.condition):
            inventory.create()
        inventories = Inventory.find_by_restock_level(10)
        self.assertEqual(len(list(inventories)), 2)
        inventories = Inventory.find_by_restock_level(5)
        self.assertEqual(len(list(inventories)), 1)

    def test_find_by_availability(self):
        """ Find an Inventory by [available] """
        inventory = Inventory(
            product_id=333, condition=Condition.NEW, quantity=1, restock_level=10, available=True)
        if not Inventory.find_by_product_id_condition(inventory.product_id, inventory.condition):
            inventory.create()
        inventory = Inventory(
            product_id=344, condition=Condition.USED, quantity=1, restock_level=10, available=False)
        if not Inventory.find_by_product_id_condition(inventory.product_id, inventory.condition):
            inventory.create()
        inventories = Inventory.find_by_availability(True)
        self.assertEqual(len(list(inventories)), 1)
        self.assertEqual(inventories[0].product_id, 333)
        self.assertEqual(inventories[0].condition, Condition.NEW)
        inventories = Inventory.find_by_availability(False)
        self.assertEqual(len(list(inventories)), 1)
        self.assertEqual(inventories[0].product_id, 344)
        self.assertEqual(inventories[0].condition, Condition.USED)
