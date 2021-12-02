import os
from unittest import TestCase

from service.constants import (API_URL, CONTENT_TYPE, POSTGRES_DATABASE_URI,
                               QUANTITY, RESTOCK_LEVEL)
from service.error_handlers import internal_server_error, method_not_supported
from service.models import DBError, Inventory, db
from service.routes import app, init_db
from tests.factories import InventoryFactory
from tests.test_routes import CONTENT_TYPE

DATABASE_URI = os.getenv("DATABASE_URI", POSTGRES_DATABASE_URI)


class TestErrorHandlers(TestCase):
    """ Test Cases for DB Errors """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        init_db()

    @classmethod
    def tearDownClass(cls):
        """ Run once after all tests """
        db.session.close()

    def setUp(self):
        """ Runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
