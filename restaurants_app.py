from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


#Fake Restaurants
restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}

restaurants = [{'name': 'The CRUDdy Crab', 'id': '1'}, {'name':'Blue Burgers', 'id':'2'},{'name':'Taco Hut', 'id':'3'}]


#Fake Menu Items
items = [ {'name':'Cheese Pizza', 'description':'made with fresh cheese', 'price':'$5.99','course' :'Entree', 'id':'1'}, {'name':'Chocolate Cake','description':'made with Dutch Chocolate', 'price':'$3.99', 'course':'Dessert','id':'2'},{'name':'Caesar Salad', 'description':'with fresh organic vegetables','price':'$5.99', 'course':'Entree','id':'3'},{'name':'Iced Tea', 'description':'with lemon','price':'$.99', 'course':'Beverage','id':'4'},{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach','price':'$1.99', 'course':'Appetizer','id':'5'} ]
item =  {'name':'Cheese Pizza','description':'made with fresh cheese','price':'$5.99','course' :'Entree'}

@app.route('/')
@app.route('/restaurants/')
def show_restaurants():
    restaurants = session.query(Restaurant).all() 
    return render_template('restaurants.html', restaurants=restaurants)

@app.route('/restaurant/new/', methods=['GET','POST'])
def new_restaurant():
    if request.method == 'POST':
        new_restaurant = Restaurant(name=request.form['name'])
        session.add(new_restaurant)
        session.commit()
        return redirect(url_for('show_restaurants'))
    return render_template('newrestaurant.html')

@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET','POST'])
def edit_restaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).first()
    if restaurant is None:
        return redirect(url_for(show_restaurants))
    if request.method == 'POST':
        restaurant.name = request.form['name']
        session.add(restaurant)
        session.commit()
        return redirect(url_for('show_restaurants'))
    return render_template('editrestaurant.html', restaurant=restaurant)

@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def delete_restaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).first()
    if restaurant is None:
        return redirect(url_for('show_restaurants'))
    if request.method == 'POST':
        session.delete(restaurant)
        session.commit()
        return redirect(url_for('show_restaurants'))
    return render_template('deleterestaurant.html', restaurant=restaurant)

@app.route('/restaurant/<int:restaurant_id>/')
def menu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).first()
    if restaurant is None:
        return redirect(url_for('show_restaurants'))
    menu_items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return render_template('menu.html', restaurant=restaurant, menu_items=menu_items)

@app.route('/restaurant/<int:restaurant_id>/menu/new/', methods=['GET','POST'])
def new_menu_item(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).first()
    if restaurant is None:
        return redirect(url_for('show_restaurants'))
    if request.method == 'POST':
        new_menu_item = MenuItem(restaurant_id=restaurant_id, name=request.form['name'], description = request.form['description'], price = request.form['price'])
        session.add(new_menu_item)
        session.commit()
        return redirect(url_for('menu', restaurant_id=restaurant_id))
    return render_template('newmenuitem.html', restaurant_id=restaurant_id)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit/', methods=['GET','POST'])
def edit_menu_item(restaurant_id, menu_id):
    menu_item = session.query(MenuItem).filter_by(id=menu_id).first()
    if menu_item is None:
        return redirect(url_for('menu', restaurant_id=restaurant_id))
    if request.method == 'POST':
        if request.form['name']:
	    menu_item.name = request.form['name']
        if request.form['description']:
	    menu_item.description = request.form['description']
        if request.form['price']:
            menu_item.price = request.form['price']
        session.add(menu_item)
        session.commit()
        return redirect(url_for('menu', restaurant_id=restaurant_id))
    return render_template('editmenuitem.html', menu_item=menu_item)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete/', methods=['GET', 'POST'])
def delete_menu_item(restaurant_id, menu_id):
    menu_item = session.query(MenuItem).filter_by(id=menu_id).first()
    if menu_item is None:
        return redirect(url_for('menu', restaurant_id=restaurant_id))
    if request.method == 'POST':
        session.delete(menu_item)
        session.commit()
        return redirect(url_for('menu', restaurant_id=restaurant_id))
    return render_template('deletemenuitem.html', menu_item=menu_item)


# --- REST endpoints ---

@app.route('/restaurants/JSON/')
def restaurants_json():
    restaurants = session.query(Restaurant).all()
    return jsonify(Restaurants=[restaurant.serialize for restaurant in restaurants])

@app.route('/restaurant/<int:restaurant_id>/menu/JSON/')
def menu_json(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).first()
    items = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON/')
def menu_item_json(restaurant_id, menu_id):
    menu_item = session.query(MenuItem).filter_by(id=menu_id).first()
    return jsonify(MenuItem=menu_item.serialize)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

