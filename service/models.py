"""
All of the models are stored in this module

-----------------------------
I N V E N T O R Y   M O D E L
-----------------------------
Descriptions:
    keeps track of how many of each product we have in our warehouse
Attributes:
  - product_id (integer): [pk] id of each product
  - condition (enum): [pk] condition of each Inventory (NEW/OPEN_BOX/USED)
  - quantity (integer): [nullabl = False] quantity of each Inventory
  - restock_level (integer): [nullable = True]
"""

import logging
from enum import Enum

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()

logger = logging.getLogger("flask.app")


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass


class Condition(Enum):
    """ Enumeration of valid Inventory Conditions """
    NEW = 0
    OPEN_BOX = 1
    USED = 2


class Inventory(db.Model):
    # Table Schema
    __tablename__ = "Inventory"
    product_id = db.Column(db.Integer, primary_key=True)
    condition = db.Column(db.Enum(Condition), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    restock_level = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return "<Inventory id=[%s]>" % self.id

    def __init__(self, product_id: int, condition: Condition):
        self.product_id = product_id
        self.condition = condition

    def serialize(self):
        """ Serializes an Inventory into a dictionary """
        return {
            "product_id": self.product_id,
            "condition": self.condition,
            "quantity": self.quantity,
            "restock_level": self.restock_level,
        }

    def deserialize(self, data):
        """
        Deserializes an Inventory from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.product_id = data["product_id"]
            self.condition = data["condition"]
            self.quantity = data["quantity"]
            self.restock_level = data["restock_level"]
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0])
        except KeyError as error:
            raise DataValidationError(
                "Invalid inventory: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid inventory: body of request contained bad or no data"
            )
        return self
