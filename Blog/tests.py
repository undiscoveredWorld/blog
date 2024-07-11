from django.test import TestCase
from django.db import connections
from django.db.utils import OperationalError


class DBTest(TestCase):
    def test_connection(self):
        self.assertTrue(_is_connected_to_db('default'))


def _is_connected_to_db(conn_name: str) -> bool:
    db_conn = connections[conn_name]
    try:
        db_conn.cursor()
    except OperationalError:
        return False
    else:
        return True
