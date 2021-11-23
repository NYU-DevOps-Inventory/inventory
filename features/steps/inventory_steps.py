######################################################################
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
######################################################################

"""
Inventory Steps

Steps file for inventory.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import json
import logging

import requests
from behave import given
from compare import expect

from service.constants import (API_URL, AVAILABLE, CONDITION, CONTENT_TYPE,
                               PRODUCT_ID, QUANTITY, RESTOCK_LEVEL)


@given('the following inventory')
def step_impl(context):
    """ Delete all Inventory and load new ones """
    BASE_URL: str = context.base_url + API_URL
    headers = {"Content-Type": CONTENT_TYPE}
    # list all of the inventory and delete them one by one
    context.resp = requests.get(BASE_URL)
    expect(context.resp.status_code).to_equal(200)

    for inventory in context.resp.json():
        context.resp = requests.delete(
            "{0}/{1}/condition/{2}".format(
                BASE_URL,
                inventory[PRODUCT_ID],
                inventory[CONDITION])
        )
        expect(context.resp.status_code).to_equal(204)

    # load the database with new inventory
    for row in context.table:
        try:
            restock_level = int(row[RESTOCK_LEVEL])
        except:
            restock_level = None
        data = {
            PRODUCT_ID: int(row[PRODUCT_ID]),
            CONDITION: row[CONDITION],
            QUANTITY: int(row[QUANTITY]),
            RESTOCK_LEVEL: restock_level,
            AVAILABLE: row[AVAILABLE] == "True"
        }
        logging.critical(data)
        payload = json.dumps(data)
        context.resp = requests.post(BASE_URL, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)
