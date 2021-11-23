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
  - available (boolean): [nullable = False] availability of each Inventory
"""

import logging
from enum import Enum
from typing import Dict, List, Union

from flask import Flask
from flask_sqlalchemy import SQLAlchemy, sqlalchemy

from service.constants import (AVAILABLE, CONDITION, PRODUCT_ID, QUANTITY,
                               RESTOCK_LEVEL)

db = SQLAlchemy()

logger = logging.getLogger("flask.app")


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass


class DBError(Exception):
    """ Used for an DB connection error """
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
        return "<Inventory ({}, {})>".format(self.product_id, self.condition)

    # --------------------------------------------------------------------------
    # CREATE, UPDATE, DELETE
    # --------------------------------------------------------------------------

    def create(self):
        """ Create an Inventory """
        logger.info("Creating (%s, %s)", self.product_id, self.condition)
        db.session.add(self)
        db.session.commit()

    def update(self):
        """ Update an Inventory """
        logger.info("Updating (%s, %s)", self.product_id, self.condition)
        db.session.commit()

    def delete(self):
        """ Delete an Inventory """
        logger.info("Deleting (%s, %s)", self.product_id, self.condition)
        db.session.delete(self)
        db.session.commit()

    # --------------------------------------------------------------------------
    # SERIALIZE, DESERIALIZE
    # --------------------------------------------------------------------------
    def serialize(self):
        """ Serialize an Inventory into a dictionary """
        return {
            PRODUCT_ID: self.product_id,
            CONDITION: self.condition.name,
            QUANTITY: self.quantity,
            RESTOCK_LEVEL: self.restock_level,
            AVAILABLE: self.available
        }

    def deserialize(self, data: Dict[str, Union[str, int]]):
        """ Deserializes an Inventory record from a dictionary """
        try:
            self.product_id = data[PRODUCT_ID]
            self.quantity = data[QUANTITY]
            self.restock_level = data[RESTOCK_LEVEL]
            self.condition = data[CONDITION]
            self.available = data[AVAILABLE]
            return self
        except KeyError as error:
            raise DataValidationError(
                "Invalid Inventory record: missing " + error.args[0])

    # --------------------------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------------------------
    def validate_data(self):
        """
        VALIDATING DATA FORMATS
        """
        error_fields: List[str] = []

        is_valid_quantity: bool = self.__validate_quantity()
        if not is_valid_quantity:
            error_fields.append(QUANTITY)

        is_valid_restock_level: bool = self.__validate_restock_level()
        if not is_valid_restock_level:
            error_fields.append(RESTOCK_LEVEL)

        if not (is_valid_quantity and is_valid_restock_level):
            msg = "Error in data: {}".format(error_fields)
            raise DataValidationError(msg)
        return True

    def __validate_quantity(self):
        """
        Validate quantity format
        """
        if isinstance(self.quantity, int) and self.quantity >= 0:
            return True
        return isinstance(self.quantity, int) and self.quantity >= 0

    def __validate_restock_level(self):
        """
        Validate restock_level format
        """
        if self.condition == Condition.NEW:
            return isinstance(self.restock_level, int) and self.restock_level >= 0
        # self.condition in [Condition.OPEN_BOX, Condition_USED]
        return True

    # --------------------------------------------------------------------------
    # CLASSMETHOD
    # --------------------------------------------------------------------------
    @classmethod
    def init_db(cls, app: Flask):
        """ Initialize the database session """
        try:
            logger.info("Initializing database")
            cls.app = app
            # This is where we initialize SQLAlchemy from the Flask app
            db.init_app(app)
            app.app_context().push()
            db.create_all()  # make our sqlalchemy tables
        except sqlalchemy.exc.ArgumentError as err:
            raise DBError("Invalid DB connection: {}".format(err))
        except sqlalchemy.exc.OperationalError as err:
            raise DBError("Invalid DB connection: {}".format(err))

    @classmethod
    def find_all(cls) -> list:
        """ Return all of the Inventory records """
        logger.info("Processing all Inventories")
        return cls.query.all()

    @classmethod
    def find_by_product_id(cls, product_id: int):
        """ Return Inventory records by product_id """
        logger.info("Processing lookup for product ID %s ...", product_id)
        return cls.query.filter(cls.product_id == product_id).all()

    @classmethod
    def find_by_condition(cls, condition: Condition):
        """ Return Inventory records by condition """
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
        """ Return Inventory records by quantity """
        logger.info("Processing lookup for quantity %s ...",
                    quantity)
        return cls.query.filter(cls.quantity == quantity).all()

    @classmethod
    def find_by_quantity_range(cls, lowerbound: int, upperbound: int):
        """ Return Inventory records by quantity range """
        logger.info(
            "Processing lookup for quantity range [ %s : %s ] ...", lowerbound, upperbound)
        return cls.query.filter(cls.quantity >= lowerbound, cls.quantity <= upperbound).all()

    @classmethod
    def find_by_restock_level(cls, restock_level: int):
        """ Return Inventory records by restock_level """
        logger.info("Processing lookup for restock_level %s ...",
                    restock_level)
        return cls.query.filter(cls.restock_level == restock_level).all()

    @classmethod
    def find_by_available(cls, available: bool = True):
        """ Return Inventory records by available """
        logger.info("Processing lookup for available %s ...",
                    available)
        return cls.query.filter(cls.available == available).all()
