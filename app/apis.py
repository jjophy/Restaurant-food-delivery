from app import application
from flask import jsonify, Response, session
from app.models import *
from app import *
import uuid
import datetime
from marshmallow import Schema, fields
from flask_restful import Resource, Api
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
import json


# class for Adding a user
class SignUpRequest(Schema):
    name = fields.Str(default = "name")
    username = fields.Str(default="username")
    password = fields.Str(default = "password")
    level = fields.Int(default = 0)

class LoginRequest(Schema):
    username = fields.Str(default="username")
    password = fields.Str(default="password")

class AddVendorRequest(Schema):
    user_id = fields.Str(default="user_id")

class VendorListResponse(Schema):
    vendors = fields.List(fields.Dict())

class AddItemRequest(Schema):
    item_name = fields.Str(default="item_name")
    calories_per_gm = fields.Int(default=0)
    available_quantity = fields.Int(default=0)
    unit_price = fields.Int(default=0)
    restaurant_name = fields.Str(default="restaurant_name")

class CreateOrderListRequest(Schema):
    item_id = fields.Str(default="item_id")
    quantity = fields.Int(default=0)

class ItemListResponse(Schema):
    items = fields.List(fields.Dict())

class APIResponse(Schema):
    message = fields.Str(default="Success")

class OrderRequest(Schema):
    order_id = fields.Str(default="order_id")
    units = fields.Int(default=0)

class OrderListResponse(Schema):
    orders = fields.List(fields.Dict())


## Task 1(a.)
## With level 2, an admin can be added...choice to input level to be given only to certain persons.
class SignUpAPI(MethodResource, Resource):
    @doc(description='Sign Up API', tags=['Sign Up API'])
    @use_kwargs(SignUpRequest, location=('json'))
    @marshal_with(APIResponse)  # marshalling
    def post(self, **kwargs):
        try:
            user = User(
                uuid.uuid4(),
                kwargs['name'],
                kwargs['username'],
                kwargs['password'],
                kwargs['level'],
                1,
                datetime.datetime.utcnow())
            db.session.add(user)
            db.session.commit()
            return APIResponse().dump(dict(message='User is successfully registered')), 200

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to register user : {str(e)}')), 400

api.add_resource(SignUpAPI, '/signup')
docs.register(SignUpAPI)

## Task 1(b.)
class LoginAPI(MethodResource, Resource):
    @doc(description='Login API', tags=['Login API'])
    @use_kwargs(LoginRequest, location=('json'))
    @marshal_with(APIResponse)  # marshalling
    def post(self, **kwargs):
        try:
            user = User.query.filter_by(username=kwargs['username'], password = kwargs['password']).first()
            if user:
                print('logged in')
                session['user_id'] = user.user_id
                session['level'] = user.level
                session['order_id'] = "initial"
                print(f'User id : {str(session["user_id"])}')
                return APIResponse().dump(dict(message='User is successfully logged in')), 200
                # return jsonify({'message':'User is successfully logged in'}), 200
            else:
                return APIResponse().dump(dict(message='User not found')), 404
                # return jsonify({'message':'User not found'}), 404
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to login user : {str(e)}')), 400

api.add_resource(LoginAPI, '/login')
docs.register(LoginAPI)

## Task 1(c.)
class LogoutAPI(MethodResource, Resource):
    @doc(description='Logout API', tags=['Logout API'])
    @marshal_with(APIResponse)  # marshalling
    def post(self, **kwargs):
        try:
            if session['user_id']:
                session['user_id'] = None
                print('logged out')
                return APIResponse().dump(dict(message='User is successfully logged out')), 200
                # return jsonify({'message':'User is successfully logged out'}), 200
            else:
                print('user not found')
                return APIResponse().dump(dict(message='User is not logged in')), 401
                # return jsonify({'message':'User is not logged in'}), 401
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to logout user : {str(e)}')), 400

api.add_resource(LogoutAPI,'/logout')
docs.register(LogoutAPI)

## Task 2(a.)
#Add a vendor..ie. change level to 1 in the Users table ..only an admin can do this
class AddVendorAPI(MethodResource, Resource):
    @doc(description='Add Vendor', tags=['Add Vendor'])
    @use_kwargs(AddVendorRequest, location=('json'))
    @marshal_with(APIResponse)  # marshalling
    def post(self, **kwargs):
        try:
            if session['user_id']:
                level = session['level']
                print("user level: ",level)
                if level == 2:
                    user = User.query.filter_by(user_id=kwargs['user_id'] ,level=0).first()
                    #user = User.query.filter_by(username=kwargs['username'], password=kwargs['password']).first()
                    print(user.user_id)
                    if user:
                        print("user level:",user.level)
                        user.level = 1
                        print("after user level:", user.level)
                        db.session.commit()
                        return APIResponse().dump(dict(message='Vendor is successfully added')), 200
                    else:
                        print('not a valid customer or already a vendor or admin')
                        return APIResponse().dump(dict(message='Not a valid customer or already a vendor')), 401
                else:
                    print("Not authorised to add a vendor - you should be an admin")
                    return APIResponse().dump(dict(message='not authorised to add vendor - you should be admin')), 401
            else:
                print('User not logged in')
                return APIResponse().dump(dict(message='User is not logged in')), 401


        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to add vendor : {str(e)}')), 400

api.add_resource(AddVendorAPI, '/add_vendor')
docs.register(AddVendorAPI)

#TAsk 2(b.)
#get the list of all vendors..only an admin has access to this
class VendorListAPI(MethodResource, Resource):
    @doc(description='Vendor List API', tags=['List of Vendors API'])
    @marshal_with(VendorListResponse)  # marshalling
    def get(self):
        try:
            if session['user_id']:
                level = session['level']
                print("user level: ", level)
                if level == 2:
                    #vendors = User.query.filter_by(level=1).first()
                    vendors = User.query.filter_by(level=1)
                    vendors_list = list()
                    for vendor in vendors:
                        vendor_dict = {}
                        vendor_dict['vendor_id'] = vendor.user_id
                        vendor_dict['name'] = vendor.name
                        vendors_list.append(vendor_dict)
                    print(vendors_list)
                    return VendorListResponse().dump(dict(vendors=vendors_list)), 200
                else:
                    print("Not authorised to list all vendors - you should be an admin")
                    return APIResponse().dump(dict(message='not authorised to list vendors - you should be admin')), 401
            else:
                print('User not logged in')
                return APIResponse().dump(dict(message='User is not logged in')), 401
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to list all vendors : {str(e)}')), 400


api.add_resource(VendorListAPI, '/vendor_list')
docs.register(VendorListAPI)

##Task 3(a.)
## Add an item to the item table
class AddItemAPI(MethodResource, Resource):
    @doc(description='Add Item API', tags=['Add Item API'])
    @use_kwargs(AddItemRequest, location=('json'))
    @marshal_with(APIResponse)  # marshalling
    def post(self, **kwargs):
        try:
            if session['user_id']:
                level = session['level']
                print("user level: ", level)
                if level == 1:  # only a vendor can add items
                    item = Item(
                        uuid.uuid4(),
                        session['user_id'],
                        kwargs['item_name'],
                        kwargs['calories_per_gm'],
                        kwargs['available_quantity'],
                        kwargs['unit_price'],
                        kwargs['restaurant_name'],
                        1,
                        datetime.datetime.utcnow())
                    db.session.add(item)
                    db.session.commit()
                    return APIResponse().dump(dict(message='Item has been successfully added')), 200
                else:
                    print("Not authorised to add items - you should be a vendor")
                    return APIResponse().dump(dict(message='Not authorised to add items - you should be a vendor')), 401
            else:
                print('User not logged in')
                return APIResponse().dump(dict(message='User is not logged in')), 401

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to add items : {str(e)}')), 400

api.add_resource(AddItemAPI, '/add_item')
docs.register(AddItemAPI)

### Extra task
#get the list of items..accessible to all
class ItemListAPI(MethodResource, Resource):
    @doc(description='Item List API', tags=['Item List API'])
    @marshal_with(ItemListResponse)  # marshalling
    def get(self):
        try:
            if session['user_id']:
                    items = Item.query.all()
                    print(items)
                    items_list = list()
                    for item in items:
                        item_dict = {}
                        item_dict['item_id'] = item.item_id
                        item_dict['vendor_id'] = item.vendor_id
                        item_dict['item_name'] = item.item_name
                        item_dict['calories_per_gm'] = item.calories_per_gm
                        item_dict['available_quantity'] = item.available_quantity
                        item_dict['unit_price'] = item.unit_price
                        item_dict['restaurant_name'] = item.restaurant_name
                        items_list.append(item_dict)
                    print(items_list)
                    return ItemListResponse().dump(dict(items=items_list)), 200
            else:
                print('User not logged in')
                return APIResponse().dump(dict(message='User is not logged in')), 401
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to list all vendors : {str(e)}')), 400


api.add_resource(ItemListAPI, '/list_items')
docs.register(ItemListAPI)

### Task 3(b.1)
# create order list -- creates a list of items to be ordered
# here first an order_is is created and an entry made in the order table.
# then one or more entries made in the orderitems table for this order_id
# the is_placed flag in order table remains 0
class CreateOrderListAPI(MethodResource, Resource):
    @doc(description='Create Order List API', tags=['Create Order List API'])
    @use_kwargs(CreateOrderListRequest, location=('json'))
    @marshal_with(APIResponse)  # marshalling
    def post(self, **kwargs):
        try:
            if session['user_id']:
                print("user_id", session['user_id'])
                level = session['level']
                print("user level: ", level)
                session_order_id = session['order_id']
                print("session order id:", session_order_id)
                print("hello")
                if level == 0:  # only a customer can create a list of items to be ordered
                    # first create an order in the Order Table
                    print("how are you")
                    if session_order_id == "initial" :  # create new order_id, only if one does not exist for this session
                        print("creating order_id")
                        order_id = uuid.uuid4()
                        print("new order_id : ", order_id)
                        session['order_id'] = order_id
                        order = Order(
                            order_id,
                            session['user_id'],
                            0,  # total amount
                            0,  # is_placed
                            1,  # is_active
                            datetime.datetime.utcnow()
                        )

                        db.session.add(order)
                        db.session.commit()
                        print("added in order table: ", order_id)



                    # now add line items in the OrderItems table with this order_id

                    order_items = OrderItems(
                        uuid.uuid4(),
                        session['order_id'],
                        kwargs['item_id'],
                        kwargs['quantity'], #- chk to be made if quantity available in items table
                        1,  # is_active
                        datetime.datetime.utcnow()
                    )

                    db.session.add(order_items)
                    db.session.commit()
                    print("order item added: ",kwargs['item_id'])
                    return APIResponse().dump(dict(message="Item  has been successfully added")), 200
                else:
                    print("Not authorised to order items  - you should be a customer")
                    return APIResponse().dump(dict(message='Not authorised to order items  - you should be a customer')), 401
            else:
                print('User not logged in')
                return APIResponse().dump(dict(message='User is not logged in')), 401

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to create order list : {str(e)}')), 400

api.add_resource(CreateOrderListAPI, '/create_order_list')
docs.register(CreateOrderListAPI)

### Task 3(b.2)
# place an order -- change is_placed flag to 1 in order table for the session order_id
# update total_amount for that order based on items in orderitems table for this order_id
# and reset session order_id, reduce available_quantity from item table
# assumption : current order to be placed before creating a new order
# please note - only the is_placed flag is updated. other calculations not done yet

class PlaceOrderAPI(MethodResource, Resource):
    @doc(description='Place Order API', tags=['Place Order API'])
    @marshal_with(APIResponse)  # marshalling
    def post(self, **kwargs):
        try:
            if session['user_id']:
                print("user_id", session['user_id'])
                level = session['level']
                if session['order_id'] is None:
                    print("No order is in session.. new order has to be created")
                    return APIResponse().dump(
                        dict(message='No order is in session.. new order has to be created')), 401

                print("user level: ", level)
                if level == 0:  # only a customer can place an order
                    # update the orders table
                    print("how are you")
                    print(session['order_id'])
                    order = Order.query.filter_by(order_id=session['order_id']).first()
                    if order:
                        print(order.order_id)
                        order.is_placed = 1  # updating the is_placed flag
                        order.total_amount = 650 # dummy update ..need to calculate ..unit_price * quantity
                        order.updated_ts = datetime.datetime.utcnow()
                        db.session.commit()
                        print("placed the given order .. is_placed flag updated ", session['order_id'])
                        return APIResponse().dump(dict(message="Order has been successfully placed")), 200
                    else:
                        print("No order found")
                        return APIResponse().dump(dict(message='No order found')), 401

                else:
                    print("Not authorised to place orders  - you should be a customer")
                    return APIResponse().dump(dict(message='Not authorised to place orders  - you should be a customer')), 401
            else:
                print('User not logged in')
                return APIResponse().dump(dict(message='User is not logged in')), 401

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to create order list : {str(e)}')), 400

api.add_resource(PlaceOrderAPI, '/place_order')
docs.register(PlaceOrderAPI)

### Task 3(c.)
# list orders by a particular user  -- only customer can list orders
class List_Orders_by_User_API(MethodResource, Resource):
    @doc(description='List Orders by User API', tags=['List Orders by User API'])
    @marshal_with(OrderListResponse)  # marshalling
    def get(self):
        try:
            if session['user_id']:
                if session['level'] == 0:
                    print("session user: ", session['user_id'])
                    orders = Order.query.filter_by(user_id=session['user_id'])
                    print(orders)
                    if orders:
                        orders_list = list()
                        for order in orders:
                            order_dict = {}
                            order_dict['order_id'] = order.order_id
                            order_dict['user_id'] = order.user_id
                            order_dict['total_amount'] = order.total_amount
                            order_dict['is_placed'] = order.is_placed
                            order_dict['created_ts'] = order.created_ts
                            order_dict['updated_ts'] = order.updated_ts
                            orders_list.append(order_dict)
                        print(orders_list)
                        return OrderListResponse().dump(dict(orders=orders_list)), 200
                    else:
                        print("No orders found for user: ", session['user_id'])
                        return APIResponse().dump(dict(message='No order found')), 401
                else:
                    print("Not authorised to list  orders for a user - you should be a customer")
                    return APIResponse().dump(dict(message='Not authorised to list orders for a user - you should be a customer')), 401
            else:
                print('User not logged in')
                return APIResponse().dump(dict(message='User is not logged in')), 401
        except Exception as e:
            return APIResponse().dump(dict(message='Not able to list orders ')), 400

api.add_resource(List_Orders_by_User_API, '/list_orders_by_user')
docs.register(List_Orders_by_User_API)

### Task 3(d.)
#list all orders ..only admin
class List_All_Orders_API(MethodResource, Resource):
    @doc(description='List All Orders API', tags=['List All Orders API'])
    @marshal_with(OrderListResponse)  # marshalling
    def get(self):
        try:
            if session['user_id']:
                if session['level'] == 2:
                    print("session user: ", session['user_id'])
                    orders = Order.query.all()
                    print("hello ",orders)
                    if orders:
                        orders_list = list()
                        print("how are u: ", orders)
                        for order in orders:
                            print("in loop ", order.user_id)
                            order_dict = {}
                            order_dict['order_id'] = order.order_id
                            print("order_id ", order.order_id)
                            order_dict['user_id'] = order.user_id
                            print("user_id ", order.user_id)
                            order_dict['total_amount'] = order.total_amount
                            print("total amt ", order.total_amount)
                            order_dict['is_placed'] = order.is_placed
                            print("is_placed ", order.is_placed)
                            order_dict['is_active'] = order.is_active
                            order_dict['created_ts'] = order.created_ts
                            order_dict['updated_ts'] = order.updated_ts
                            print("updated ts ", order.updated_ts)
                            print("order_dict ",order_dict)

                            orders_list.append(order_dict)
                        print(orders_list)
                        return OrderListResponse().dump(dict(orders=orders_list)), 200
                    else:
                        print("No orders found for user: ", session['user_id'])
                        return APIResponse().dump(dict(message='No order found')), 401
                else:
                    print("Not authorised to list all  orders - you should be an admin")
                    return APIResponse().dump(dict(message='Not authorised to list all  orders - you should be an admin')), 401
            else:
                print('User not logged in')
                return APIResponse().dump(dict(message='User is not logged in')), 401
        except Exception as e:
            return APIResponse().dump(dict(message='Not able to list all  orders')), 400


api.add_resource(List_All_Orders_API, '/list_all_orders')
docs.register(List_All_Orders_API)


