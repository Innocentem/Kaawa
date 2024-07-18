from flask import Blueprint, render_template, url_for, flash, redirect, request
from app import db, bcrypt
from app.forms import RegistrationForm, LoginForm, MessageForm, ListingForm
from app.models import User, Message, Listing, Order
from flask_login import login_user, current_user, logout_user, login_required

main = Blueprint('main', __name__)

@main.route('/')
def landing():
    return render_template('landing.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, account_type=form.account_type.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.landing'))

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard')

@main.route('/listings')
@login_required
def view_listings():
    if current_user.account_type == 'farmer':
        listings = Listing.query.filter_by(user_id=current_user.id).all()
    else:
        listings = Listing.query.all()
    return render_template('listings.html', listings=listings, title='Listings')

@main.route('/add_listing', methods=['GET', 'POST'])
@login_required
def add_listing():
    if current_user.account_type != 'farmer':
        flash('Only farmers can add listings.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = ListingForm()
    if form.validate_on_submit():
        listing = Listing(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            user_id=current_user.id
        )
        db.session.add(listing)
        db.session.commit()
        flash('Your listing has been added!', 'success')
        return redirect(url_for('main.view_listings'))
    return render_template('add_listing.html', form=form, title='Add Listing')

@main.route('/manage_orders')
@login_required
def manage_orders():
    if current_user.account_type != 'farmer':
        flash('Only farmers can manage orders.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    orders = Order.query.filter_by(farmer_id=current_user.id).all()
    return render_template('manage_orders.html', orders=orders, title='Manage Orders')

@main.route('/browse_listings')
@login_required
def browse_listings():
    listings = Listing.query.all()
    return render_template('browse_listings.html', listings=listings, title='Browse Listings')

@main.route('/your_orders')
@login_required
def your_orders():
    orders = Order.query.filter_by(buyer_id=current_user.id).all()
    return render_template('your_orders.html', orders=orders, title='Your Orders')

@main.route('/favorite_farmers')
@login_required
def favorite_farmers():
    # Placeholder for future implementation
    return render_template('favorite_farmers.html', title='Favorite Farmers')

@main.route('/send_message/<int:receiver_id>', methods=['GET', 'POST'])
@login_required
def send_message(receiver_id):
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(sender_id=current_user.id, receiver_id=receiver_id, content=form.content.data)
        db.session.add(message)
        db.session.commit()
        flash('Message sent!', 'success')
        return redirect(url_for('main.messages'))
    return render_template('send_message.html', form=form, title='Send Message')

@main.route('/messages')
@login_required
def messages():
    received_messages = Message.query.filter_by(receiver_id=current_user.id).all()
    sent_messages = Message.query.filter_by(sender_id=current_user.id).all()
    return render_template('messages.html', received=received_messages, sent=sent_messages)
