# Flask-application-for-online-food-delivery

Flask Restaurant  Assignment 	 IIITH-SEDS-Part A_July 21
Nov 21, 2021	Student: Jophy Joseph

This is a complete backend system for a Restaurant Website, implemented in Flask, which allows you to signup
customers and vendors, login them using their credentials, as a vendor add items in the
database, as a customer place an order, and as an admin I should be able to see all the orders
placed etc.


This file explains the file and code organisation and each of the tasks assigned. 

M01-Flask-REST-API-Source-Code has an app folder which has 3 python files __init__.py, apis.py and models.py

The application is triggered with main.py, which has the application run command.

__init__.py is first executed..here the application config file is updated. APISPEC, marshmallow and swagger is used. The models.py is imported here.

models.py : this file creates the 4 tables in the flask_restaurant db
a.) user : user of the app. 3 levels - customer(0), vendor(1), admin(2)
b.) item : details of the food item
c.) order : an order, which contains one or more order items
d.) orderitems : details of each line item in the order

apis.py : this files contains all the methods (assignment tasks)
1 (a.) /signup 
		-name
		-uname
		-pass
		-level

Adds a user. The level parameter of 2 is passed to add an admin and would be exposed only to certain users.

1 (b.)/login
		-uname
		-pass

1.(c.)/logout

2(a.) /add_vendor
		[-only admin]
		
		-user_id

2(b.)/vendor_list
	get	[-only admin]

3(a.)/add_item
		[-only vendor]
		
		-item_name
		-item_description
		-unit_price
		-quantity
		-calories_per_gram
		-restaurant_name

3(b.1)/create_order_list [-only customer]
		items: [
				{item_id:<>, quantity:<>}
		       ]
		       
		       	-order_id is created 
		       	-make entries in order_items table
		       	
		       	db.session.commit()
		       	
3(b.2)	/place_order [-only customer]
		-order_id 

  		the order_id is stored in the session. 
		order.is_placed flag is updated to 1

		(order.total_amount is updated  (unit_price [-from items tbl] * quantity)
		order.updated_ts is updated
		item.available_quantity is decremented) ..not implemented 

3.(c.) /list_orders_by_user [-only customer]
	get

3 (d.) /list_all_orders [-only admin]
	get
