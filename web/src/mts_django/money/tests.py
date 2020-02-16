import os
import json
import logging
import random
from decimal import Decimal
from datetime import datetime
import requests
from django.test import TestCase
from mts_django.settings import DATABASES
from money.models import *
from users.models import *

info_logger = logging.getLogger('info')

class TestMoneyOperations(TestCase):
    session = None
    def setUp(self):
        """Initialize parameters for next HTTP requests"""
        self.session = requests.Session()
        self.protocol = 'http:/'
        self.host = '127.0.0.1'
        self.port = '8000'
        self.service_path = 'api'
        self.token_auth_path = 'token'
        #admin's credentials, could be passed through environment variables ADMIN_EMAIL, ADMIN_PASSWORD
        self.admin = os.getenv('ADMIN_EMAIL', default='email')
        self.admin_pass = os.getenv('ADMIN_PASSWORD', default='password')
        #requests are done on behalf of admin user by default
        self.get_auth_token(self.admin, self.admin_pass)

    def get_url(self, path):
        return '/'.join([self.protocol, self.host + ':' + self.port, self.service_path, path]) + '/'

    def get_auth_token(self, user, password):
        """"Authorization through getting token"""
        info_logger.info('get_auth_token')
        self.user = user
        self.password = password
        auth_url = self.get_url(self.token_auth_path)
        payload = {'email': self.user, 'password': self.password}
        self.session.headers.update({'Content-Type': 'application/json'})
        r = self.session.post(auth_url, data=json.dumps(payload))
        d = r.json()
        self.token = d['access']
        self.session.headers.update({'Authorization': 'Bearer %s' % self.token})
    
    def test_check_course_rates(self):
        """Testing list of course rates"""
        url = self.get_url('money/courses')
        r = self.session.get(url)
        self.assertEqual(r.status_code, 200, msg='Course rates url %s - is not responding!' % url)
        rates = r.json()
        self.assertGreater(len(rates), 0, msg='Course rates list is empty!')
        return rates

    def test_check_currency_list(self):
        """Testing list of currencies"""
        url = self.get_url('money/currencies')
        r = self.session.get(url)
        self.assertEqual(r.status_code, 200, msg='Currency list url %s - is not responding!' % url)
        currency_list = r.json()
        self.assertGreater(len(currency_list), 0, msg='Currency list is empty!')
        return currency_list
    
    def test_convertation(self):
        """Testing convertation of random currencies"""
        rates = self.test_check_course_rates()
        currency_list = self.test_check_currency_list()
        #getting 2 random currencies
        currency1, currency2 = random.choices(currency_list, k=2)
        #getting random course
        rate = random.choice(rates)
        date_of_rate = datetime.strptime(rate['date'], '%Y-%m-%dT%H:%M:%S')
        amount = 245000.00
        course1, course2, converted_amount = convert_amount(currency1['name'], currency2['name'], amount, date=date_of_rate)
        calculated_amount = course2/course1 * Decimal(amount)
        #comparing manual convertation to convert_amount function result
        self.assertEqual(calculated_amount, converted_amount, 'Error in currency convertation function "convert_amount"!')

    def test_create_user(self):
        """Testing of user creation mechanism"""
        username = 'Test4'
        email = 'test4@test4.org'
        password = '12345678'
        balance = 1000.00
        currency = 'USD'
        payload = {'username': username, 'email': email, 'password': password, 'balance': balance, 'currency': currency}
        url = self.get_url('users/create')
        r = self.session.post(url, data=json.dumps(payload))
        if r.status_code != 201:
            user_list_url = self.get_url('users')
            r = self.session.get(user_list_url)
            user_list = r.json()
            self.assertGreater(len(user_list), 0, msg='User list is empty!')
            user = list(filter(lambda user: user['email'] == email, user_list))
            self.assertIsNotNone(user, 'User %s is not found' % email)

    def get_account_info(self, user, currency):
        """Method for getting information about account"""
        #fetching all account of user
        user_accounts_url = self.get_url('users/%s/accounts' % user['pk'])
        r = self.session.get(user_accounts_url)
        self.assertEqual(r.status_code, 200, msg='Url %s is not available!' % user_accounts_url)
        user_accounts = r.json()
        self.assertGreater(len(user_accounts), 0, msg='User %s does not have any accounts!' % user['email'])
        #filtering user's accounts to get account with currency
        user_account = list(filter(lambda account: account['currency']['name'] == currency, user_accounts))
        self.assertIsNotNone(user_account, msg='User %s does not have %s account!' % (user['email'], currency))
        return user_account[0]

    def test_create_transfer(self):
        """Tests related to transfer creation issues"""
        #sender's info
        user2 = {'username': 'Test40', 'email': 'test40@test40.org', 'password': '12345678', 'balance': 1000.00, 'currency': 'USD'}
        #receiver's info
        user1 = {'username': 'Test41', 'email': 'test41@test41.org', 'password': '12345678', 'balance': 1000.00, 'currency': 'USD'}
        create_user_url = self.get_url('users/create')
        self.session.post(create_user_url, data=json.dumps(user1))
        self.session.post(create_user_url, data=json.dumps(user2))

        #getting user list to check whether sender and receiver were successfully created
        user_list_url = self.get_url('users')
        r = self.session.get(user_list_url)
        self.assertEqual(r.status_code, 200, msg='Url %s is not available!' % user_list_url)
        user_list = r.json()
        #testing user list for emptiness
        self.assertGreater(len(user_list), 0, msg='User list is empty!')
        #looking for sender and receiver
        user1_dict = list(filter(lambda user: user['email'] == user1['email'], user_list))
        user2_dict = list(filter(lambda user: user['email'] == user2['email'], user_list))
        #testing search results
        self.assertIsNotNone(user1_dict, 'User %s is not found' % user1['email'])
        self.assertIsNotNone(user2_dict, 'User %s is not found' % user2['email'])
        user1_dict = user1_dict[0]
        user2_dict = user2_dict[0]

        #getting sender and receiver account info
        sender_account = self.get_account_info(user1_dict, user1['currency'])
        receiver_account = self.get_account_info(user2_dict, user2['currency'])
        #primary key and balance of the account are necessary for the request
        sender_account_pk = sender_account['pk']
        sender_balance = Decimal(sender_account['balance'].replace(',', '.'))
        receiver_account_pk = receiver_account['pk']
        receiver_balance = Decimal(receiver_account['balance'].replace(',', '.'))

        create_transfer_url = self.get_url('money/transfers/create')
        #we must sign in as sender before making transfer requests 
        self.get_auth_token(user1['email'], user1['password'])
        #zero amount transfer testing
        transfer = {'sender_account': sender_account_pk, 'receiver_account': receiver_account_pk, 'amount': '0'}
        r = self.session.post(create_transfer_url, data=json.dumps(transfer))
        d = r.json()
        msg = '; '.join([str(m) for m in d.values()])
        self.assertNotEqual(r.status_code, 201, msg='Transfer validation errors must be: %s' % msg)

        #test attempts to make a transfer from someone else's account
        transfer = {'sender_account': sender_account_pk, 'receiver_account': receiver_account_pk, 'amount': '0'}
        r = self.session.post(create_transfer_url, data=json.dumps(transfer))
        d = r.json()
        msg = '; '.join([str(m) for m in d.values()])
        self.assertNotEqual(r.status_code, 201, msg='Transfer validation errors must be: %s' % msg)

        #negative amount transfer testing
        transfer = {'sender_account': sender_account_pk, 'receiver_account': receiver_account_pk, 'amount': '-2'}
        r = self.session.post(create_transfer_url, data=json.dumps(transfer))
        d = r.json()
        msg = '; '.join([str(m) for m in d.values()])
        self.assertNotEqual(r.status_code, 201, msg='Transfer validation errors must be: %s' % msg)

        #unsufficient balance testing
        transfer = {'sender_account': sender_account_pk, 'receiver_account': receiver_account_pk, 'amount': str(sender_balance + 1)}
        r = self.session.post(create_transfer_url, data=json.dumps(transfer))
        d = r.json()
        msg = '; '.join([str(m) for m in d.values()])
        self.assertNotEqual(r.status_code, 201, msg='Transfer validation errors must be: %s' % msg)

        #normal amount transfer testing
        transfer = {'sender_account': sender_account_pk, 'receiver_account': receiver_account_pk, 'amount': str(sender_balance)}
        r = self.session.post(create_transfer_url, data=json.dumps(transfer))
        self.assertEqual(r.status_code, 201, msg='Transfer failed!')

        #testing balance of sender and receiver's accounts after transfer
        sender_account = self.get_account_info(user1_dict, user1['currency'])
        receiver_account = self.get_account_info(user2_dict, user2['currency'])
        sender_new_balance = Decimal(sender_account['balance'].replace(',', '.'))
        receiver_new_balance = Decimal(receiver_account['balance'].replace(',', '.'))
        self.assertEqual(sender_new_balance, 0, msg="Sender's balance must be zero")
        self.assertEqual(receiver_new_balance, receiver_balance + sender_balance, msg="Receiver's balance must be %s !" % (receiver_balance + sender_balance))

    def test_update_user(self):
        """Testing user update mechanism"""
        #creating user for testing editing mechanism
        user = {'username': 'NewUser', 'email': 'test51@test51.org', 'password': 'asdQWE!@#', 'balance': 1000.00, 'currency': 'USD'}
        url = self.get_url('users/create')
        self.session.post(url, data=json.dumps(user))
        #searching user object among all users
        user_list_url = self.get_url('users')
        r = self.session.get(user_list_url)
        user_list = r.json()
        new_user = list(filter(lambda u: u['email'] == user['email'], user_list))
        new_user_pk = new_user[0]['pk']
        #new fields
        new_username = 'NewName2ForNewUser'
        current_password =  user['password']
        new_password = 'sdfWER@#$'
        payload = {'email': user['email'], 'new_username': new_username, 'current_password': current_password, 'new_password': new_password}
        url = self.get_url('users/%s/edit' % new_user_pk)
        r = self.session.patch(url, data=json.dumps(payload))
        #checking out request's result
        self.assertEqual(r.status_code, 202, msg="Error occured while editing user's information!")
        #searching user object to compare edited fields
        user_list_url = self.get_url('users')
        r = self.session.get(user_list_url)
        user_list = r.json()
        new_user = list(filter(lambda user: user['username'] == new_username, user_list))
        self.assertIsNotNone(new_user, 'User %s was not updated!' % user['email'])