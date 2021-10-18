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

    def __repr__(self):
        return "<Inventory product_id=[%s] with condition=[%s] condition>" % self.product_id, self.condition

    def create(self):
        """
        Create an Inventory to the database
        """
        logger.info("Creating %s", self.product_id)
        db.session.add(self)
        db.session.commit()

    def serialize(self):
        """ Serialize an Inventory into a dictionary """
        return {
            "product_id": self.product_id,
            "condition": self.condition.name,
            "quantity": self.quantity,
            "restock_level": self.restock_level,
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

    @classmethod
    def init_db(cls, app: Flask):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls) -> list:
        """ Returns all of the Inventories in the database """
        logger.info("Processing all Inventories")
        return cls.query.all()
