from flask import render_template, request, flash, redirect,url_for,session
from pyfiles.models import *
from app import app

@app.route('/')
def home():
    lots = ParkingLot.query.all()
    available_lots = {}
    parking_cost = {}
    active_registration={}

    user = User.query.filter_by(email = session.get('email')).first()

    for lot in lots:
        available_spots = [spot for spot in lot.parkingspot if spot.status == 'A']
        available_lots[lot.id] = len(available_spots)
        parking_cost[lot.id] = lot.price

    if user: 
        #check if user has a slot in any of the lots and add to active registration
        reservation = ReserveParkingSpot.query.join(ParkingSpot).filter(
            ReserveParkingSpot.user_id == user.id,
            ReserveParkingSpot.leaving_timestamp ==None
        ).all()
        
        for res in reservation:
            active_registration[res.spot.lot_id] = res

    return render_template('home.html', lots=lots, available_lots=available_lots,
                            parking_cost=parking_cost,active_registration=active_registration,
                         user = user)
    

@app.route('/login',methods =['GET','POST'])
def login():
    if request.method =='GET':
        return render_template('login.html')
    
    if request.method =='POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # data validation
        if not email or not password:
            flash('Enter email and password please','error')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('User not found','error')
            return redirect(url_for('login'))
        
        if user.password != password:
            flash('Incorrect Password','error')
            return redirect(url_for('login'))
        
        session['email'] = email
        session['roles'] = [role.name for role in user.roles]

        flash('Successful Login','success')
        return redirect(url_for('home'))

@app.route('/logout')    
def logout():
    session.pop('email',None)
    session.pop('role',None)
    flash('Logged Out Successfully','success')
    return redirect(url_for('login'))

@app.route('/register',methods =['POST','GET'])
def register():
    if request.method =='GET':
        return render_template('register.html')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        #data validation
        if not email or not password:
            flash('Email and password are required.', 'error')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.', 'error')
            return redirect(url_for('register'))
        
        user_role = Role.query.filter_by(name='user').first()
        user = User(
            email=email,
            password=password,
            roles=[user_role]
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
@app.route('/add_lot',methods=['GET','POST'])
def add_lot():
    if request.method =='GET':
        return render_template('add_lot.html')

    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        address = request.form.get('address')
        pin_code = request.form.get('pin_code')
        max_num_spots = request.form.get('max_num_spots')

        # Basic Validation
        if not all([name, price, address, pin_code, max_num_spots]):
            flash('All fields are required.', 'error')
            return redirect(url_for('add_lot'))

        if len(pin_code) != 6 or not pin_code.isdigit():
            flash('Pin code must be exactly 6 digits.', 'error')
            return redirect(url_for('add_lot'))

        existing = ParkingLot.query.filter_by(name=name).first()
        if existing:
            flash('A parking lot with this name already exists.', 'error')
            return redirect(url_for('add_lot'))

        try:
            price = int(price)
            max_num_spots = int(max_num_spots)

            lot = ParkingLot(
                name=name,
                price=price,
                address=address,
                pin_code=pin_code,
                max_num_spots=max_num_spots
            )
            db.session.add(lot)
            db.session.commit()

            for i in range(max_num_spots):
                spot = ParkingSpot(lot_id=lot.id,status='A')
                db.session.add(spot)

            db.session.commit()
            flash('Parking lot added successfully!', 'success')
            return redirect(url_for('home'))

        except ValueError:
            flash('Price and Max Spots must be numbers.', 'error')
            return redirect(url_for('add_lot'))
    
    
@app.route('/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_lot(lot_id):
    lot = ParkingLot.query.get(lot_id)
    existing_spots = len(lot.parkingspot)

    if request.method == 'GET':
        return render_template('edit_lot.html', lot=lot)

    if request.method == 'POST':
        max_num_spots = int(request.form.get('max_num_spots'))
        available_spots = ParkingSpot.query.filter_by(status='A', lot_id=lot_id).all()

        # CASE 1: Reducing spots
        if max_num_spots < existing_spots:
            spots_to_remove = existing_spots - max_num_spots

            if spots_to_remove > len(available_spots):
                flash('Deleting data. Try Again', 'error')
                return redirect(url_for('edit_lot', lot_id=lot.id))

            # DELETE the last N available spots
            for spot in available_spots[-spots_to_remove:]:
                db.session.delete(spot)
            db.session.commit()

        # CASE 2: Increasing spots
        elif max_num_spots > existing_spots:
            excess_spots = max_num_spots - existing_spots
            for _ in range(excess_spots):
                spot = ParkingSpot(lot_id=lot_id, status='A')
                db.session.add(spot)
            db.session.commit()

        # Update Lot Info
        lot.name = request.form.get('name')
        lot.price = request.form.get('price')
        lot.address = request.form.get('address')
        lot.pin_code = request.form.get('pin_code')
        lot.max_num_spots = max_num_spots

        db.session.commit()

        flash('Successfully Edited Parking lot Data', 'success')
        return redirect(url_for('view_lot', lot_id=lot.id))  # optional: redirect to view

    

@app.route('/delete_lot/<int:lot_id>', methods = ['GET'] )
def delete_lot(lot_id):
    lot = ParkingLot.query.get(lot_id)

    #data validation
    if not lot:
        flash ('Lot not found','error')
        return redirect(url_for('home'))
    
    if any(spot.status =='O' for spot in lot.parkingspot):
        flash('Cannot delete as Spots are Occupied','error')
        return redirect(url_for('home'))
    
    db.session.delete(lot)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/lot/<int:lot_id>/view', methods =['GET'])
def view_lot(lot_id):
    lot= ParkingLot.query.get(lot_id)

    #Data Validation
    if not lot:
        flash('Lot not found','error')
        return redirect(url_for('home'))
    
    spots = lot.parkingspot

    return render_template('view_lot.html',spots = spots,lot =lot)

@app.route('/bookspot/<int:lot_id>/<int:spots_available>/<int:parking_rate>',methods=['GET'])
def book_spot(lot_id,spots_available,parking_rate):
    user =User.query.filter_by(email=session['email']).first().id
    if not user:
        flash('User not found','error')
    spot = ParkingSpot.query.filter_by(lot_id=lot_id,status="A").first()
    spot_id = spot.id
    lot = ParkingLot.query.get(lot_id)
    lot_name = lot.name

    parking_entry = ReserveParkingSpot(
        spot_id = spot_id,
        user_id = user,
        lot_id = lot_id,
        lot_name = lot_name,
        parking_timestamp = datetime.utcnow(),
        parking_cost_per_hour = parking_rate
    )

    spot.status='O'

    db.session.add(parking_entry)
    db.session.commit()

    return redirect(url_for('home'))

@app.route('/pay_and_leave/<int:reservation_id>',methods=['GET'])
def pay_and_leave(reservation_id):
    reservation = ReserveParkingSpot.query.get(reservation_id)
    if not reservation:
        flash('No reservation here','error')
        return redirect(url_for('home'))
    
    #user_name = User.query.filter_by(id = reservation_id).first().name

    reservation.leaving_timestamp = datetime.utcnow()

    start_time = reservation.parking_timestamp.timestamp()
    end_time = reservation.leaving_timestamp.timestamp() 
    duration = end_time-start_time
    time = int(duration/3600)
    bill = int(reservation.parking_cost_per_hour)*time 

    #Change reservation status to Available
    reservation.spot.status = 'A'

    db.session.commit()

    return(render_template('pay_and_leave.html',
                           cost_per_hour =reservation.parking_cost_per_hour,
                           time=time,
                           bill=bill
                           ))

@app.route('/admin_summary',methods=['GET'])
def admin_summary():
    if 'email' not in session or 'admin' not in session.get('roles',[]):
        flash('Admin not logged in','error')
        return redirect(url_for('login'))
    
    users = User.query.all()
    summaries=[]

    for user in users:
        user_reservation = user.reservations #Backref
        
        formatted_reservations=[]
        for res in user_reservation:
            start = res.parking_timestamp
            end = res.leaving_timestamp if res.leaving_timestamp is not None else None

            duration = None
            cost = None
            if end:
                duration_seconds = (end - start).total_seconds()
                duration = float(duration_seconds//3600)
                cost = int(duration* res.parking_cost_per_hour)
            
            formatted_reservations.append({
                'lot_name' : res.lot_name,
                'spot_id' : res.spot_id,
                'start': start,
                'end': end,
                'duration':duration,
                'cost': cost
            })
        summaries.append({
            'user': user,
            'reservations': formatted_reservations
        })
    
    return render_template('admin_summary.html',summaries=summaries)

@app.route('/my_summary',methods=['GET'])
def my_summary():
    
    email = session.get('email',[])
    if not email:
        flash('Not Logged in','error')
        return redirect(url_for('login'))
    
    users = User.query.filter_by(email=session['email']).first()
    if not users:
        flash('Users not Found','error')
        return redirect(url_for('login'))
    
    user_reservation = users.reservations
    reservations =[]

    for res in user_reservation:
        
        start = res.parking_timestamp
        end = res.leaving_timestamp if res.leaving_timestamp is not None else None
        duration_in_secs = None
        duration = None
        cost = None

        if end:
            duration_in_secs = (end - start).total_seconds()
            duration = float(duration_in_secs//3600)
            cost = int(duration*res.parking_cost_per_hour)

        reservations.append({
        'lot_name' : res.lot_name,
        'spot_id' : res.spot_id,
        'start':start,
        'end':end,
        'duration':duration,
        'cost':cost
        })

    return render_template('user_summary.html',reservations=reservations)