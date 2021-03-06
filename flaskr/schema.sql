DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS cart;
DROP TABLE IF EXISTS cart_products;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  coins INT NOT NULL
);

CREATE TABLE product (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  owner_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  price INTEGER NOT NULL,
  FOREIGN KEY (owner_id) REFERENCES user (id)
);

CREATE TABLE cart (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  owner_id INTEGER NOT NULL,
  hash TEXT NOT NULL,
  FOREIGN KEY (owner_id) REFERENCES user (id)
);

CREATE TABLE cart_products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cart_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  FOREIGN KEY (cart_id) REFERENCES cart (id),
  FOREIGN KEY (product_id) REFERENCES product (id)
);
