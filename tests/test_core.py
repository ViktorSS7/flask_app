import unittest
from core import entities, errors
from random import randint


def create_user(username='testuser', password='testpass', coins=10, ):
    return entities.User(username=username, password=password, coins=coins)


def create_product(owner=create_user(), title='TestProduct',
                   price=randint(1, 3)):
    return entities.Product(owner=owner, title=title, price=price)


def create_cart(owner=create_user(),
                products=None):
    if products is None:
        products = [create_product(title='TestProduct1',
                                   owner=create_user('Owner1')),
                    create_product(title='TestProduct2',
                                   owner=create_user('Owner2'))]
    return entities.Cart(owner=owner, products=products)


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

    def test_change_password(self):
        """Test successful changing user's password"""
        old_password = 'oldpass'
        new_password = 'newpass'
        user = create_user(password=old_password)

        user.change_password(old_password, new_password, new_password)

        self.assertTrue(user.password_validate(new_password))

    def test_change_password_with_error(self):
        """Test change password with not equal new and repeat pass"""
        old_password = 'oldpass'
        new_password = 'newpass'
        repeat_password = 'another_pass'
        user = create_user(password=old_password)

        with self.assertRaises(errors.MessageException):
            user.change_password(old_password, new_password, repeat_password)

    def test_successful_buy_cart(self):
        user = create_user('User1')
        cart = create_cart(owner=user)
        user_coins = user.coins

        owner1 = cart.products[0].owner
        owner1_coins = owner1.coins
        owner2 = cart.products[1].owner
        owner2_coins = owner2.coins

        user.buy_cart(cart)

        self.assertEqual(
            user.coins,
            user_coins - (cart.products[0].price + cart.products[1].price)
        )
        self.assertEqual(cart.products[0].owner, user)
        self.assertEqual(cart.products[1].owner, user)
        self.assertEqual(owner1.coins, owner1_coins + cart.products[0].price)
        self.assertEqual(owner2.coins, owner2_coins + cart.products[1].price)


class TestProduct(unittest.TestCase):

    def setUp(self) -> None:
        self.user = entities.User(
            username='testuser',
            password='testpass',
            id=1
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


class TestCart(unittest.TestCase):

    def setUp(self) -> None:
        self.product1 = create_product()
        self.product2 = create_product(owner=create_user('testuser2'),
                                       title='TestProduct2')

    def test_create(self):
        """Test successful cart create"""
        payload = {
            'owner': create_user(username='CartOwner'),
            'products': {self.product1, self.product2}
        }

        cart = entities.Cart(**payload)

        self.assertTrue(isinstance(cart.hash, int))
        self.assertEqual(cart.owner.username, payload['owner'].username)
        self.assertEqual(len(cart.products), 2)
        self.assertEqual(cart.cart_sum,
                         self.product1.price + self.product2.price)

    def test_create_error(self):
        """Test create cart without owner"""

        with self.assertRaises(errors.MessageException):
            entities.Cart(products=[self.product2])
