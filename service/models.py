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

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

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
    available = db.Column(db.Boolean(), nullable=False, default=False)

    def __repr__(self):
        return f"<Inventory product_id=[{self.product_id}] with condition=[{self.condition}] condition>"

    def create(self):
        """
        Create an Inventory to the database
        """
        logger.info("Creating %s", self.product_id)
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates an record in the inventory
        """
        logger.info("Saving product %s with condition %s",
                    self.product_id, self.condition)
        if not self.product_id or not self.condition:
            raise DataValidationError(
                "Update called with empty product ID or condition")
        db.session.commit()

    def delete(self):
        """
        Remove an Inventory from the database
        """
        logger.info("Deleting %s with %s condition",
                    self.product_id, self.condition.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serialize an Inventory into a dictionary """
        return {
            "product_id": self.product_id,
            "condition": self.condition.name,
            "quantity": self.quantity,
            "restock_level": self.restock_level,
            "available": self.available
        }

    def deserialize(self, data):
        """
        Deserialize an Inventory from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.product_id = data["product_id"]
            self.condition = getattr(Condition, data["condition"])
            self.quantity = data["quantity"]
            if isinstance(data["quantity"], int):
                self.quantity = data["quantity"]
            else:
                raise DataValidationError(
                    "Invalid type for int [quantity]: " + type(data["quantity"]))
            if isinstance(data["restock_level"], int):
                self.restock_level = data["restock_level"]
            elif data["restock_level"]:  # If this exists, it must be a wrong type
                raise DataValidationError(
                    "Invalid type for int [restock_level]: " + type(data["restock_level"]))
            if isinstance(data["available"], bool):
                self.available = data["available"]
            else:
                raise DataValidationError(
                    "Invalid type for boolean [available]: " + type(data["available"]))
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

    @classmethod
    def init_db(cls, app: Flask):
        """ Initialize the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls) -> list:
        """ Return all of the Inventories in the database """
        logger.info("Processing all Inventories")
        return cls.query.all()

    @classmethod
    def find_by_product_id(cls, product_id: int):
        """ Find Inventory by product ID """
        logger.info("Processing lookup for id %s ...", product_id)
        return cls.query.filter(cls.product_id == product_id).all()

    @classmethod
    def find_by_condition(cls, condition: Condition):
        """ Return Inventory by condition """
        logger.info("Processing lookup for condition %s ...", condition)
        return cls.query.filter(cls.condition == condition).all()

    @classmethod
    def find_by_product_id_condition(cls, product_id: int, condition: Condition):
        """ Find an Inventory record by product_id and condition """
        logger.info(
            "Processing lookup for product_id %s and condition %s ...", product_id, condition)
        return cls.query.get((product_id, condition))

    @classmethod
    def find_by_quantity(cls, quantity: int):
        """ Return Inventory by quantity """
        logger.info("Processing lookup for quantity %s ...",
                    quantity)
        return cls.query.filter(cls.quantity == quantity).all()

    @classmethod
    def find_by_quantity_range(cls, lowerbound: int, upperbound: int):
        """ Return Inventory by quantity range """
        logger.info(
            "Processing lookup for quantity range [ %s : %s ] ...", lowerbound, upperbound)
        return cls.query.filter(cls.quantity >= lowerbound, cls.quantity <= upperbound).all()

    @classmethod
    def find_by_restock_level(cls, restock_level: int):
        """ Return Inventory by restock_level """
        logger.info("Processing lookup for restock_level %s ...",
                    restock_level)
        return cls.query.filter(cls.restock_level == restock_level).all()

    @classmethod
    def find_by_availability(cls, available: bool = True):
        """ Return Inventory by available """
        logger.info("Processing lookup for available %s ...",
                    available)
        return cls.query.filter(cls.available == available).all()
