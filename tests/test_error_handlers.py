import os
from unittest import TestCase

from service import status
from service.constants import (API_URL, CONTENT_TYPE, POSTGRES_DATABASE_URI,
                               QUANTITY, RESTOCK_LEVEL)
from service.error_handlers import internal_server_error, method_not_supported
from service.models import db
from service.routes import app, init_db
from tests.factories import InventoryFactory
from tests.test_routes import CONTENT_TYPE

DATABASE_URI = os.getenv("DATABASE_URI", POSTGRES_DATABASE_URI)


class TestErrorHandlers(TestCase):
    """ Test Cases for Error Handlers """

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

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################
    def test_request_validation_error(self):
        """ Request validation error: HTTP_400_BAD_REQUEST """
        inventory = InventoryFactory()
        resp = self.app.post(
            API_URL, json=inventory.serialize(), content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp = self.app.put(
            "{0}/{1}/condition/{2}".format(
                API_URL,
                inventory.product_id,
                inventory.condition.name),
            json={QUANTITY: -1000, RESTOCK_LEVEL: -400},
            content_type=CONTENT_TYPE)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_method_not_supported(self):
        """ Test method not supported """
        error = 405
        message = str(error)
        resp, status_code = method_not_supported(error)
        self.assertEqual(status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        data = resp.get_json()
        self.assertEqual(data["status"], status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(data["error"], "Method not Allowed")
        self.assertEqual(data["message"], message)

    def test_internal_server_error(self):
        """ Test internal server serror """
        error = 500
        message = str(error)
        resp, status_code = internal_server_error(error)
        self.assertEqual(status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        data = resp.get_json()
        self.assertEqual(data["status"], status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(data["error"], "Internal Server Error")
        self.assertEqual(data["message"], message)
