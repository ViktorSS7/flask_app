from flaskr.service import service, user as service_user,\
    product as service_product, cart as service_cart
from flaskr.db import get_db

from core import entities


def get_test_user(username='testuser', password='testpass', coins=3):
    return entities.User(
        username=username,
        password=password,
        coins=coins
    )


user_entity = get_test_user(username='TESTUSER')


def get_test_product(title='TetProduct', price=3, owner=None):
    if not owner:
        owner = user_entity
    return entities.Product(
        title=title,
        price=price,
        owner=owner
    )


def test_db_execute_one(app):
    with app.app_context():
        assert service.db_execute_one('SELECT 1')['1'] == 1


def test_db_execute_all(app):
    sql = 'SELECT * FROM user'
    with app.app_context():
        result = service.db_execute_all(sql)
        assert len(get_db().execute(sql).fetchall()) == len(result)


def test_create_user(app):
    payload = {
        'username': 'UserTest',
        'password': 'testpass',
        'coins': 3
    }
    user = get_test_user(**payload)
    with app.app_context():
        user_id = service_user.store_user(user)
        user_data = service.db_execute_one(
            'SELECT * FROM user WHERE id = ?',
            (user_id,)
        )
        assert user_data['username'] == payload['username']
        assert user.password_validate(user_data['password'])
        assert user_data['coins'] == payload['coins']


def test_build_user_by_id(app):
    payload = {
        'username': 'UserTest',
        'password': 'testpass',
        'coins': 3
    }
    user = get_test_user(**payload)
    with app.app_context():
        user_id = service_user.store_user(user)
        db_user = service_user.build_user_by_id(user_id)
        assert db_user.username == payload['username']
        assert db_user.password_validate(payload['password'])
        assert db_user.coins == payload['coins']
        assert db_user.id


def test_update_user(app):
    payload = {
        'username': 'UserTest',
        'password': 'testpass',
        'coins': 3
    }
    new_payload = {
        'username': 'NewName',
        'password': 'NewPassword',
        'coins': 7
    }
    user = get_test_user(**payload)
    with app.app_context():
        user_id = service_user.store_user(user)
        db_user = service_user.build_user_by_id(user_id)
        db_user.username = new_payload['username']
        db_user.change_password(
            payload['password'],
            new_payload['password'],
            new_payload['password']
        )
        db_user.coins = new_payload['coins']
        service_user.store_user(db_user)
        user_data = service.db_execute_one(
            'SELECT * FROM user WHERE id = ?',
            (user_id,)
        )
        assert user_data['username'] == new_payload['username']
        assert user_data['coins'] == new_payload['coins']
        assert db_user.password_validate(user_data['password'])
        assert db_user.password_validate(new_payload['password'])


def test_create_product(app):
    owner = get_test_user(username='Owner1')
    payload = {
        'title': 'Product1',
        'price': 3,
        'owner': owner
    }

    product = get_test_product(**payload)
    with app.app_context():
        owner_id = service_user.store_user(product.owner)
        product_id = service_product.store_product(product)
        product_data = service.db_execute_one(
            'SELECT * FROM product WHERE id = ?',
            (product_id,)
        )
        assert product_data['title'] == payload['title']
        assert product_data['price'] == payload['price']
        assert product_data['owner_id'] == owner_id


def test_build_product_by_id(app):
    owner = get_test_user(username='Owner1')
    payload = {
        'title': 'Product1',
        'price': 3,
        'owner': owner
    }

    product = get_test_product(**payload)
    with app.app_context():
        owner_id = service_user.store_user(product.owner)
        product_id = service_product.store_product(product)
        db_product = service_product.build_product_by_id(product_id)
        assert db_product.owner.id == owner_id
        assert db_product.title == payload['title']
        assert db_product.price == payload['price']


def test_update_product(app):
    owner = get_test_user(username='Owner1')
    new_owner = get_test_user(username='NewOwner1')
    payload = {
        'title': 'Product1',
        'price': 3,
        'owner': owner
    }
    new_payload = {
        'title': 'NewProduct1',
        'price': 7,
        'owner': new_owner
    }

    product = get_test_product(**payload)
    with app.app_context():
        service_user.store_user(product.owner)
        new_owner_id = service_user.store_user(new_owner)
        service_product.store_product(product)
        product.edit(
            owner,
            **new_payload
        )
        product_id = service_product.store_product(product)
        product_data = service.db_execute_one(
            'SELECT * FROM product WHERE id = ?',
            (product_id,)
        )
        assert product_data['title'] == new_payload['title']
        assert product_data['price'] == new_payload['price']
        assert product_data['owner_id'] == new_owner_id


def test_build_products_list(app):
    products = [
        get_test_product(title='Prod1'),
        get_test_product(title='Prod2'),
        get_test_product(title='Prod3'),
    ]
    with app.app_context():
        service_user.store_user(user_entity)
        ids_list = list()
        for prod in products:
            ids_list.append(
                service_product.store_product(prod)
            )
        db_product_list = service_product\
            .build_products_list_by_ids_list(ids_list)
        assert len(db_product_list) == len(products)


def test_store_cart(app):
    cart_owner = get_test_user('CartOwner')
    products = [
        get_test_product('Product1'),
        get_test_product('Product2'),
        get_test_product('Product3')
    ]
    cart = entities.Cart(owner=cart_owner, products=products)
    with app.app_context():
        owner_id = service_user.store_user(cart_owner)
        cart.owner_id = owner_id
        products_ids = set()
        for prod in products:
            products_ids.add(service_product.store_product(prod))
        cart_id = service_cart.store_cart(cart)
        cart_data = service.db_execute_one('SELECT * FROM cart WHERE id = ?', (cart_id,))
        cart_products_data = service.db_execute_all(
            'SELECT * FROM cart_products WHERE cart_id = ?', (cart_id, )
        )
        assert cart_data['owner_id'] == cart.owner.id
        assert len(cart_products_data) == len(products)
        for prod in cart_products_data:
            assert prod['product_id'] in products_ids


def test_build_cart_by_id(app):
    cart_owner = get_test_user('CartOwner')
    products = [
        get_test_product('Product1'),
        get_test_product('Product2'),
        get_test_product('Product3')
    ]
    cart = entities.Cart(owner=cart_owner, products=products)
    with app.app_context():
        owner_id = service_user.store_user(cart_owner)
        cart.owner_id = owner_id
        products_ids = set()
        for prod in products:
            products_ids.add(service_product.store_product(prod))
        cart_id = service_cart.store_cart(cart)
        cart_db = service_cart.build_cart_by_id(cart_id)
        assert cart_db.owner.id == cart.owner.id
        assert len(cart_db.products) == len(cart.products)
        for prod in cart_db.products:
            assert prod.id in products_ids


def test_build_cart_by_owner(app):
    cart_owner = get_test_user('CartOwner')
    products = [
        get_test_product('Product1'),
        get_test_product('Product2'),
        get_test_product('Product3')
    ]
    cart = entities.Cart(owner=cart_owner, products=products)
    with app.app_context():
        owner_id = service_user.store_user(cart_owner)
        cart.owner_id = owner_id
        products_ids = set()
        for prod in products:
            products_ids.add(service_product.store_product(prod))
        service_cart.store_cart(cart)
        cart_db = service_cart.build_cart_by_owner(cart_owner)
        assert cart_db.owner.id == cart.owner.id
        assert len(cart_db.products) == len(cart.products)
        for prod in cart_db.products:
            assert prod.id in products_ids
