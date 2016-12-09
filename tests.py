import os
import json
import main
import unittest
import tempfile
import config

def create_user(client, email, password):
    """Helper function to register a user"""
    return client.post('/users', data={
        'email': email,
        'password': password
    })


def login(client, username, password):
    """Helper function to login"""
    return client.post('/login', data={
        'email': username,
        'password': password
    })


def activate_user(client, code):
    """Helper function to activate user"""
    url = "/activation/{}".format(code)
    return client.get(url)


def access_protected(client):
    """Helper function to access protected url"""
    return client.get('/protected')


def create_user_and_login(client, email, password):
    """Created a user and logins"""
    result = create_user(client, email, password)
    code = json.loads(result.data)['code']
    activate_user(client, code)
    return login(client, email, password)


def logout(client):
    """Helper function to logout"""
    return client.get('/logout', follow_redirects=True)


class EndpointTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, config.DATABASE = tempfile.mkstemp()
        main.app.config['TESTING'] = True
        self.app = main.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(config.DATABASE)

    def test_user_creation(self):
        result = create_user(self.app, 'test@me.com', '1234')
        self.assertEqual(result.status_code, 200)
        self.assertTrue("code" in result.data)
        result = create_user(self.app, 'test@me.com', '1234')
        self.assertEqual(result.status_code, 400)
        self.assertTrue("error" in result.data)

    def test_login(self):
        result = login(self.app, 'test@me.com', '1234')
        self.assertEqual(result.status_code, 400)
        result = create_user_and_login(self.app, 'test@me.com', '1234')
        self.assertEqual(result.status_code, 200)

    def test_activation(self):
        result = create_user(self.app, 'test@me.com', '1234')
        code = json.loads(result.data)['code']
        result = login(self.app, 'test@me.com', '1234')
        self.assertEqual(result.status_code, 400)
        result = activate_user(self.app, code)
        self.assertEqual(result.status_code, 200)
        result = activate_user(self.app, code)
        self.assertEqual(result.status_code, 400)
        result = login(self.app, 'test@me.com', '1234')
        self.assertEqual(result.status_code, 200)

    def test_logout(self):
        result = create_user_and_login(self.app, 'test@me.com', '1234')
        self.assertEqual(result.status_code, 200)
        result = access_protected(self.app)
        self.assertEqual(result.status_code, 200)
        result = logout(self.app)
        self.assertEqual(result.status_code, 200)
        result = access_protected(self.app)
        self.assertEqual(result.status_code, 401)

if __name__ == '__main__':
    unittest.main()
