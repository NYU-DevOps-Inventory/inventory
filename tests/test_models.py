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

### -----------------------------------------------------------
###  Modified by DevOps Course Fall 2021 Squad - Inventory Team
###  Members:
#      Chen, Peng-Yu | pyc305@nyu.edu | New York | UTC-5
#      Lai, Yu-Wen   | yl8332@nyu.edu | New York | UTC-5
#      Zhang, Haoran | hz2613@nyu.edu | New York | UTC-5
#      Wen, Xuezhou  | xw2447@nyu.edu | New York | UTC-5
#      Hung, Ginkel  | ch3854@nyu.edu | New York | UTC-5
# 
###  Resource URL: /inventory
###  Description:
#      The inventory resource keeps track of how many of each product we
#      have in our warehouse. At a minimum it should reference a product and the
#      quantity on hand. Inventory should also track restock levels and the condition
#      of the item (i.e., new, open box, used). Restock levels will help you know
#      when to order more products. Being able to query products by their condition
#      (e.g., new, used) could be very useful.
### -----------------------------------------------------------

"""
Test cases for Inventory Model

Test cases can be run with:
    nosetests
    coverage report -m
    
While debugging just these tests it's convinient to use this:
    nosetests --stop tests/test_pets.py:TestPetModel
"""
import os
import logging
import unittest
# from werkzeug.exceptions import NotFound
# from service import app
# from service.models import InventoryModel, DataValidationError, db

# DATABASE_URI = os.getenv(
#     "DATABASE_URI", "postgres://postgres:postgres@localhost:[port]/testdb"
# )

######################################################################
#  I N V E N T O R Y   M O D E L   T E S T   C A S E S
######################################################################
class TestYourInventoryModel(unittest.TestCase):
    """ Test Cases for Inventory Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        pass

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        pass

    def tearDown(self):
        """ This runs after each test """
        pass

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_XXXX(self):
        """ Test something """
        self.assertTrue(True)