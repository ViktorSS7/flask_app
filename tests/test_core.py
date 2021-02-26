import unittest
from core import entities, errors


class TestUser(unittest.TestCase):

    def test_successful_create(self):
        payload = {
            'username': 'testuser',
            'password': 'testpass'
        }

        user = entities.User(**payload)

        self.assertEqual(str(user), payload['username'])
        self.assertTrue(user.password_validate(payload['password']))

    def test_error_create(self):
        payload = {
            'username': 'testuser',
        }

        with self.assertRaises(errors.ValidationException):
            entities.User(**payload)

    def test_successful_buy_product(self):
        product_owner_payload = {
            'username': 'ProductOwner',
            'password': 'testpass',
            'coins': 1
        }
        product_owner = entities.User(**product_owner_payload)

        product_payload = {
            'owner': product_owner,
            'title': 'Test product',
            'price': 3
        }
        product = entities.Product(**product_payload)

        payload = {
            'username': 'testuser',
            'password': 'testpass',
            'coins': 4
        }
        user = entities.User(**payload)

        user.buy_product(product)

        self.assertEqual(product.owner, user)
        self.assertEqual(user.coins, payload['coins'] - product.price)
        self.assertEqual(product_owner.coins,
                         product_owner_payload['coins'] + product.price)

    def test_error_not_enough_money_buy_product(self):
        product_owner_payload = {
            'username': 'ProductOwner',
            'password': 'testpass',
            'coins': 1
        }
        product_owner = entities.User(**product_owner_payload)

        product_payload = {
            'owner': product_owner,
            'title': 'Test product',
            'price': 3
        }
        product = entities.Product(**product_payload)

        payload = {
            'username': 'testuser',
            'password': 'testpass',
            'coins': 2
        }
        user = entities.User(**payload)

        with self.assertRaises(errors.MessageException):
            user.buy_product(product)


class TestProduct(unittest.TestCase):

    def setUp(self) -> None:
        self.user = entities.User(
            username='testuser',
            password='testpass'
        )

    def test_successful_create(self):
        payload = {
            'owner': self.user,
            'title': 'Test product',
            'price': '3'
        }

        product = entities.Product(**payload)

        self.assertEqual(str(product), payload['title'])

    def test_error_create(self):
        payload = {
            # have not owner
            'title': 'Test product',
            'price': '3'
        }

        with self.assertRaises(errors.ValidationException):
            entities.Product(**payload)
