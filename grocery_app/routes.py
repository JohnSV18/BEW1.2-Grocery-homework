from flask import Blueprint, request, render_template, redirect, url_for, flash, Flask
from datetime import date, datetime
from grocery_app.models import GroceryStore, GroceryItem, User
from grocery_app.forms import GroceryStoreForm, GroceryItemForm, LoginForm, SignUpForm
from flask_login import login_required, login_user, logout_user, current_user
from flask_bcrypt import Bcrypt

from grocery_app import app, db

main = Blueprint("main", __name__)
bcrypt = Bcrypt(app)
##########################################
#           Routes                       #
##########################################

@main.route('/')
def homepage():
    all_stores = GroceryStore.query.all()
    print(all_stores)
    return render_template('home.html', all_stores=all_stores)

@main.route('/new_store', methods=['GET', 'POST'])
@login_required 
def new_store():
    form=GroceryStoreForm()

    if form.validate_on_submit():
        print("***** trying to print success *****")
        new_store = GroceryStore(
            title = form.title.data,
            address = form.address.data
        )
        db.session.add(new_store)
        db.session.commit()

        flash('You have Succesfully created a new store')
        return redirect(url_for('main.store_detail', store_id=new_store.id))
    return render_template('new_store.html', form=form)

@main.route('/new_item', methods=['GET','POST'])
@login_required 
def new_item():
    form=GroceryItemForm()

    if form.validate_on_submit():
        print("***** trying to print success *****")
        new_item = GroceryItem(
            name = form.name.data,
            price = form.price.data,
            category = form.category.data,
            photo_url = form.photo_url.data,
            store= form.store.data
        )
        db.session.add(new_item)
        db.session.commit()

        flash('You have Succesfully created a new item')
        return redirect(url_for('main.item_detail', item_id=new_item.id))
    return render_template('new_item.html', form=form)

@main.route('/store/<store_id>', methods=['GET', 'POST'])
@login_required 
def store_detail(store_id):
    store = GroceryStore.query.get(store_id)
    form = GroceryStoreForm(obj=store)
    
    if form.validate_on_submit():
        store.title = form.title.data
        store.address = form.address.data

        db.session.commit()

        flash('You have Succesfully updated your store')
        return redirect(url_for('main.store_detail', store_id=store.id, store=store))
    return render_template('store_detail.html', store=store, form=form)

@main.route('/item/<item_id>', methods=['GET', 'POST'])
@login_required 
def item_detail(item_id):
    item = GroceryItem.query.get(item_id)
    form = GroceryItemForm(obj=item)

    if form.validate_on_submit():
        item.name = form.name.data
        item.price = form.price.data
        item.category = form.category.data
        item.photo_url = form.photo_url.data
        db.session.commit()
        
        flash('You have Succesfully updated your item')
        return redirect(url_for('main.item_detail', item_id=item.id, item=item))
    return render_template('item_detail.html', item=item, form=form)

@main.route('/add_to_shopping_list/<item_id>', methods=['POST'])
def add_to_shopping_list(item_id):
  
    item = GroceryItem.query.get(item_id)
    current_user.shopping_list_items.append(item)
    db.session.add(current_user)
    db.session.commit()
    shopping_list_items = current_user.shopping_list_items
    print('*******Trying to print shopping list items********')
    print(shopping_list_items)
    flash('This your list')

    return render_template('shopping_list.html', shopping_list_items=shopping_list_items)

@main.route('/shopping_list')
@login_required
def shopping_list():
   
    shopping_list_items = current_user.shopping_list_items
   
    return render_template('shopping_list.html', shopping_list_items = shopping_list_items)


##########################################
#            Auth.Routes                 #
##########################################

auth = Blueprint("auth", __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    print('in signup')
    form = SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash('Account Created.')
        print('created')
        return redirect(url_for('auth.login'))
    print(form.errors)
    return render_template('signup.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('main.homepage'))
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.homepage'))


