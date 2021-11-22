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

import requests
from behave import given
from compare import expect


@given('the following inventory')
def step_impl(context):
    """ Delete all Inventory and load new ones """
    headers = {"Content-Type": "application/json"}
    # list all of the inventory and delete them one by one
    context.resp = requests.get(
        context.base_url + "/inventory", headers=headers)
    expect(context.resp.status_code).to_equal(200)

    for inventory in context.resp.json():
        context.resp = requests.delete(
            "{0}/inventory/{1}/condition/{2}".format(
                context.base_url,
                inventory["product_id"],
                inventory["condition"]),
            headers=headers)
        expect(context.resp.status_code).to_equal(204)

    # load the database with new inventory
    create_url = context.base_url + '/inventory'
    for row in context.table:
        try:
            restock_level = int(row["restock_level"])
        except:
            restock_level = None
        data = {
            "product_id": int(row["product_id"]),
            "condition": row["condition"],
            "quantity": int(row["quantity"]),
            "restock_level": restock_level,
            "available": row["available"] in ["True", "true", "1"]
        }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)
