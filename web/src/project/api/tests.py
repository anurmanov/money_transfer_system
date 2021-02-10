from rest_framework.test import APITransactionTestCase, APIClient
from money.models import Course, Currency, Transfer, Account
from users.models import User

class TestAPI(APITransactionTestCase):
    
    def setUp(self):
        self.client = APIClient()
    
    def fill_db(self):
        admin = User.objects.create_superuser('admin@server.org', 'asdQWE!@#')
        user1 = User.objects.create_user('user1@server.org', 'wsx123qaz')
        user2 = User.objects.create_user('user2@server.org', 'wsx123qaz')

    def test_create_user(self):
        users = User.objects.all()
        self.assertEqual(len(users), 2, mag='Count of users must be 2!')