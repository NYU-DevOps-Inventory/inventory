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
from typing import List

from service import app
from service.constants import POSTGRES_DATABASE_URI, QUANTITY
from service.models import Condition, DataValidationError, Inventory, db
from sqlalchemy import exc

DATABASE_URI = os.getenv("DATABASE_URI", POSTGRES_DATABASE_URI)

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

    def test_inventory_repr(self):
        """ Inventory __repr__ """
        product_id = 1
        condition = Condition.NEW
        inventory = Inventory(product_id=product_id,
                              condition=condition, quantity=2, restock_level=3)
        self.assertEqual(
            str(inventory), "<Inventory ({}, {})>".format(product_id, condition))

    def test_deserialize_key_error(self):
        """ Deserialize: KeyError """
        inventory = Inventory()
        try:
            inventory.deserialize({QUANTITY: 1})
        except:
            pass

    def test_invalid_restock_level(self):
        """ Find a list of all Inventory """
        # Inventory wich Condition.NEW should have restock_level >= 0
        inventory = Inventory(product_id=1, condition=Condition.NEW,
                              quantity=2, restock_level=None)
        try:
            inventory.validate_data()
        except DataValidationError:
            pass

    def test_find_all(self):
        """ Find a list of all Inventory """
        Inventory(product_id=1, condition=Condition.NEW,
                  quantity=2, restock_level=3).create()
        Inventory(product_id=1, condition=Condition.USED,
                  quantity=2, available=True).create()
        inventories: List[Inventory] = Inventory.find_all()
        self.assertEqual(len(list(inventories)), 2)

    def test_find_by_product_id(self):
        """ Find a list of Inventory by [product_id] """
        p1 = 1
        p2 = 2
        Inventory(product_id=p1, condition=Condition.NEW, quantity=2).create()
        Inventory(product_id=p2, condition=Condition.NEW, quantity=2).create()
        Inventory(product_id=p2, condition=Condition.USED, quantity=2).create()
        for product_id, count in zip([p1, p2], [1, 2]):
            inventories: List[Inventory] = Inventory.find_by_product_id(
                product_id)
            self.assertEqual(len(list(inventories)), count)

    def test_find_by_condition(self):
        """ Find a list of Inventory by [condition] """
        c1 = Condition.NEW
        c2 = Condition.OPEN_BOX
        Inventory(product_id=1, condition=c1, quantity=2).create()
        Inventory(product_id=2, condition=c2, quantity=2).create()
        Inventory(product_id=3, condition=c2, quantity=2).create()
        for condition, count in zip([c1, c2], [1, 2]):
            inventories: List[Inventory] = Inventory.find_by_condition(
                condition)
            self.assertEqual(len(list(inventories)), count)

    def test_find_by_quantity(self):
        """ Find a list of Inventory by [quantity] """
        q1 = 1
        q2 = 2
        Inventory(product_id=1, condition=Condition.NEW, quantity=q1).create()
        Inventory(product_id=2, condition=Condition.NEW, quantity=q2).create()
        Inventory(product_id=3, condition=Condition.NEW, quantity=q2).create()
        for quantity, count in zip([q1, q2], [1, 2]):
            inventories: List[Inventory] = Inventory.find_by_quantity(quantity)
            self.assertEqual(len(list(inventories)), count)

    def test_find_by_quantity_range(self):
        """ Find a list of Inventory by [quantity range] """
        Inventory(product_id=1, condition=Condition.NEW, quantity=2).create()
        Inventory(product_id=2, condition=Condition.NEW, quantity=3).create()
        Inventory(product_id=3, condition=Condition.USED, quantity=5).create()
        inventories: List[Inventory] = Inventory.find_by_quantity_range(2, 6)
        self.assertEqual(len(list(inventories)), 3)
        inventories: List[Inventory] = Inventory.find_by_quantity_range(6, 10)
        self.assertEqual(len(list(inventories)), 0)

    def test_find_by_restock_level(self):
        """ Find a list of Inventory by [restock_level] """
        r1 = 1
        r2 = 2
        Inventory(product_id=1, condition=Condition.NEW,
                  quantity=2, restock_level=r1).create()
        Inventory(product_id=2, condition=Condition.NEW,
                  quantity=3, restock_level=r2).create()
        Inventory(product_id=3, condition=Condition.USED,
                  quantity=5, restock_level=r2).create()
        for restock_level, count in zip([r1, r2], [1, 2]):
            inventories: List[Inventory] = Inventory.find_by_restock_level(
                restock_level)
            self.assertEqual(len(list(inventories)), count)

    def test_find_by_available(self):
        """ Find a list of Inventory by [available] """
        Inventory(product_id=1, condition=Condition.NEW,
                  quantity=2, available=True).create()
        Inventory(product_id=2, condition=Condition.NEW, quantity=3).create()
        Inventory(product_id=3, condition=Condition.USED, quantity=5).create()
        for available, count in zip([True, False], [1, 2]):
            inventories: List[Inventory] = Inventory.find_by_available(
                available)
            self.assertEqual(len(list(inventories)), count)
