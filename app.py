#!/usr/bin/env python3

import csv
from datetime import datetime
from collections import OrderedDict
import os

from peewee import *


db = SqliteDatabase('inventory.db')


class Product(Model):
    product_id = IntegerField(primary_key=True, unique=True)
    product_name = CharField(max_length=255, unique=True)
    product_price = IntegerField(null=False)
    product_quantity = IntegerField()
    date_updated = DateTimeField()

    class Meta:
        database = db

def initialize():
    db.connect()
    db.create_tables([Product], safe=True)
    create_and_add_products_from_csv()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def view_product():
    """View details about existing product"""
    try:
        products = Product.select().order_by(Product.product_id.asc()) 
        product_id_input = int(input("What is the Product ID? "))
        if product_id_input:
            products = products.where(Product.product_id ==  product_id_input)
        if products:
            for product in products:
                product_price = [price for price in str(product.product_price)]
                product_price.insert(-2, ".")
                product_price = "".join(product_price)
                print(f'\nProduct Name: {product.product_name}, \nProduct Price: {product_price}, \nProduct Quantity: {product.product_quantity}, \nLast Updated: {product.date_updated}\n')
        else:
            print(f"A product id with the number you entered does not exist. We only have product id's from 1 to {Product.select().count()}.")
    except ValueError:
        print("Product price and quantity must be an integer.")
        view_product()

def add_product():
    """Add new product"""
    try:
        product_name = input("Product Name: ")
        product_price = input("Product Price(example: 4.50): ")
        product_quantity = input("Product Quantity: ")
        date_added = datetime.now()
        if isinstance(product_quantity, str):
            int(product_quantity)
        if isinstance(product_price, str):
            product_price = int(''.join(product for product in product_price if product.isdigit()))
        if input('Save entry? [Yn] ').lower() != 'n':
            Product.create(product_name=product_name, product_price=product_price, product_quantity=product_quantity, date_updated=date_added)
            print("Saved Successfully!")
    except ValueError:
        print("Product price and quantity must be an integer.")
        add_product()
    except IntegrityError:
        update_product_date = Product.select().where(Product.product_name == product_name).get().date_updated
        if update_product_date <= date_added:
            Product.update(product_name=product_name, product_price=product_price, product_quantity=product_quantity, date_updated=date_added).where(Product.product_name == product_name).execute()
            print("Existing product price updated")

def backup_database():
    """Backup database"""
    with open('backup.csv', 'a') as csvfile:
        fieldnames = ['product_id', 'product_name', 'product_price', 'product_quantity', 'date_updated']
        product_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        product_writer.writeheader()
        products = Product.select().order_by(Product.product_id.asc()) 
        for product in products:
            product_writer.writerow({
                'product_id': product.product_id,
                'product_name': product.product_name,
                'product_quantity': product.product_quantity,
                'product_price': product.product_price,
                'date_updated': product.date_updated,
            })
        print("Backup completed successfully to backup.csv")

def create_and_add_products_from_csv():
    with open("inventory.csv", "rt") as file:
        reader = csv.DictReader(file, delimiter=',')
        rows = list(reader)
    for row in rows:
        product_name = row['product_name']
        product_quantity = row['product_quantity']
        product_price = row['product_price']
        date = row['date_updated']
        product_quantity = int(product_quantity)
        product_price = int(''.join(product for product in product_price if product.isdigit()))
        date = datetime.strptime(date, "%m/%d/%Y")
        if not Product.select().where(Product.product_name == product_name).exists():
            add_products = Product(product_name=product_name, product_quantity=product_quantity, product_price=product_price, date_updated=date)
            add_products.save()
        if Product.select().where(Product.product_name == product_name).exists():
            if date >= Product.date_updated:
                Product.update(product_name=product_name, product_price=product_price, product_quantity=product_quantity, date_updated=date).where(Product.product_name == product_name).execute()

menu = OrderedDict([
    ('v', view_product),
    ('a', add_product),
    ('b', backup_database),
])

def menu_loop():
    try:
        print("\nWelcome to our product inventory!\n") 
        choice = None
        while choice != 'q':
            print("Enter 'q' to quit")
            for key, value in menu.items():
                print(f'{key}) {value.__doc__}')
            choice = input('Action: ').lower().strip()
            if choice in menu:
                clear()
                menu[choice]()
            if choice == 'q':
                print("Thanks for looking at our inventory.")
    except KeyError:
        print("\nPlease choose a valid menu option: v, a, or b\n")
        menu_loop()

if __name__ == '__main__':
    initialize()
    menu_loop()
    
