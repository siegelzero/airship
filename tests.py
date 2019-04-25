"""
# Unit Tests for Contacts API.
"""
import json
import unittest
from base64 import b64encode
from urllib.parse import urlencode

from api import app, db


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        user_password = b64encode(b"tester:testerpw").decode("ascii")
        self.headers = {
            'Authorization': f'Basic {user_password}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        self.url = '/contacts/'

    def tearDown(self):
        db.clear()

    def get(self, id=None, data=None):
        if id is not None:
            url = f'{self.url}{id}'
        elif data is not None:
            url = f'{self.url}?{urlencode(data)}'
        else:
            url = self.url
        return self.app.get(url).json

    def patch(self, id, data):
        return self.app.patch(f'{self.url}{id}', data=json.dumps(data), headers=self.headers).json

    def post(self, data):
        return self.app.post(self.url, data=json.dumps(data), headers=self.headers).json

    def delete(self, id):
        return self.app.delete(f'{self.url}{id}', headers=self.headers).json


class PostTest(BaseTest):
    def test_simple_post(self):
        # Verify that no contacts exist.
        self.assertEqual(self.get(), {'data': []})

        # POST a contact.
        result = self.post({
            'name': "Michael Scott",
            'email': "michael.scott@gmail.com",
            'phone': "(555) 123-4567",
        })['data'][0]

        # Verify data
        self.assertEqual(result['name'], "Michael Scott")
        self.assertEqual(result['email'], "michael.scott@gmail.com")
        self.assertEqual(result['phone'], "(555) 123-4567")


class GetTest(BaseTest):
    def test_simple_get(self):
        # POST a contact.
        result = self.post({'name': "Dwight Schrute"})
        dwight_id = result['data'][0]['id']
        result = self.get(id=dwight_id)['data'][0]
        self.assertEqual(result['name'], "Dwight Schrute")

    def test_invalid_id(self):
        result = self.get(id='123')
        self.assertEqual(result['error']['status'], 404)

    def test_get_multiple(self):
        # POST two contacts.
        self.post({'name': "Jim Halpert"})
        self.post({'name': "Pam Halpert"})

        # GET all contacts.
        result = self.get()

        # Verify that we have both (in created-time order)
        self.assertEqual(len(result['data']), 2)
        self.assertEqual(result['data'][0]['name'], "Jim Halpert")
        self.assertEqual(result['data'][1]['name'], "Pam Halpert")

    def test_get_multiple_filter(self):
        # POST two contacts with the same phone and one with a different.
        self.post({'name': "Ryan Howard", 'phone': '(314) 159-2653'})
        self.post({'name': "Kelly Kapoor", 'phone': '(314) 159-2653'})
        self.post({'name': "Oscar Martinez", 'phone': '(555) 111-2222'})

        # GET them back, filtering by phone.
        data = {'phone': '(314) 159-2653'}
        result = self.get(data=data)['data']

        # Verify that we get back the correct results.
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], "Ryan Howard")
        self.assertEqual(result[1]['name'], "Kelly Kapoor")


class DeleteTest(BaseTest):
    def test_delete(self):
        # POST two contacts.
        result = self.post({'name': "Stanley Hudson"})
        result = self.post({'name': "Angela Martin"})
        angela_id = result['data'][0]['id']

        # Delete one contact.
        self.delete(angela_id)

        # Verify that only one contact remains.
        result = self.get()['data']
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], "Stanley Hudson")


class PatchTest(BaseTest):
    def test_patch(self):
        result = self.post({'name': "Darryl Philbin", 'phone': "(555) 555-5555"})
        darryl_id = result['data'][0]['id']
        self.patch(darryl_id, {'phone': "(987) 654-3210"})

        # Now GET to ensure record is updated.
        result = self.get(id=darryl_id)
        self.assertEqual(result['data'][0]['phone'], "(987) 654-3210")


if __name__ == '__main__':
    unittest.main()
