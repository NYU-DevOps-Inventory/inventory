"""
All of the models are stored in this module

Models
-----------------------------
I N V E N T O R Y   M O D E L
-----------------------------
Descriptions:
    Keeps track of the condition of each Inventory
Attributes:
  - id (integer): the primary key (auto-incremented)
  - product_id (integer): the foreign key used to refer a Product (Product.id)
  - condition (enum): condition of each Inventory (e.g. new/expired/broken, etc)
  - created_at (date): purchase date of each Inventory

-------------------------
P R O D U C T   M O D E L
-------------------------
Descriptions:
    Keeps track of the restock level and quantity of each product
Attributes:
  - id (integer): the primary key (auto-incremented)
  - name (string): the name of each Product
  - restock_level (integer): the minimum level of the quantity of a stock item
  - quantity (integer): the quantity of each Product
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
    New = 0
    Expired = 1
    Broken = 2


class Inventory(db.Model):
    # Table Schema
    __tablename__ = 'Inventory'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey(
        "product.id"), nullable=False)
    condition = db.Column(db.Enum(Condition), nullable=False,
                          server_default=Condition.New.name)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())

    def __repr__(self):
        return "<Inventory id=[%s]>" % self.id

    def __init__(self, product_id=None, condition=None):
        self.product_id = product_id
        self.condition = condition

    def serialize(self):
        """ Serializes an Inventory into a dictionary """
        return {
            "id": self.id,
            "product_id": self.product_id,
            "condition": self.condition,
            "created_at": self.created_at,
        }

    def deserialize(self, data):
        """
        Deserializes an Inventory from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.product_id = data["product_name"]
            self.condition = data["condition"]
            self.created_at = data["created_at"]
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


class Product(db.Model):
    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    restock_level = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    inventory = db.relationship("Inventory", backref="product", lazy=True)

    def __repr__(self):
        return "<Product %r id=[%s]>" % (self.name, self.id)

    def serialize(self):
        """ Serializes an Product into a dictionary """
        return {
            "id": self.id,
            "name": self.name,
            "restock_level": self.restock_level,
            "quantity": self.quantity
        }

    def deserialize(self, data):
        """
        Deserializes an Product from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.restock_level = data["restock_level"]
            self.quantity = data["quantity"]
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0])
        except KeyError as error:
            raise DataValidationError(
                "Invalid product: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid product: body of request contained bad or no data"
            )
        return self
