from flask import Flask, render_template, url_for, request, session, redirect, flash
import os
from wtforms import Form, validators, StringField, PasswordField
from wtforms.fields.html5 import DateField, DateTimeField
from flask_wtf import FlaskForm
import mysql.connector
from passlib.hash import sha256_crypt
from random import randint
from datetime import datetime,timedelta


def getDBConnection():
    return mysql.connector.connect(
        user='root',
        password='root',
        host='127.0.0.1',
        port=3306,
        database='bennett_project'
    )


def getURLSyntax(str):
    # converting Silhouette Club to silhouette-club
    str = str.strip().replace(" ", "-").lower()
    return str


app = Flask(__name__)
app.secret_key = 'This is a secret!'

@app.before_request
def make_session_permanent():
    # login session times out after 15 minutes of inactivity
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)


def generateRandomID(length=8):
    _id = ''
    for i in range(length):
        _id += str(randint(1, 9))
    return _id


def addAdmin(URL_Name, Password):
    database = getDBConnection()
    cursor = database.cursor()
    password = sha256_crypt.hash(Password)
    cursor.execute("INSERT INTO admins VALUES(%s,%s,%s)", (URL_Name, password,'0'))
    database.commit()
    database.close()
    cursor.close()

CLUBS={}
EVENT_IDS=[]

database = getDBConnection()
cur = database.cursor()
# get club descriptions from database
cur.execute("SELECT * FROM club_descriptions")
res = cur.fetchall()
# get events data from database
cur.execute("SELECT * FROM club_events")
club_data = cur.fetchall()
database.close()
cur.close()

for club in res:
    CLUBS[club[1]] = {}
    CLUBS[club[1]]['name'] = club[0]
    CLUBS[club[1]]['endpoint'] = club[1]
    CLUBS[club[1]]['description'] = club[2]
    CLUBS[club[1]]['announcements'] = []
    CLUBS[club[1]]['total-announcements'] = 0

for club in club_data:
    CLUBS[club[1]]['announcements'].append(
        {
            'id':club[0],
            'URL_Name':club[1],
            'date':datetime.strptime(club[2], '%Y-%m-%d').strftime('%d/%m/%Y'),
            'time':club[3],
            'venue':club[4],
            'description':club[5]
        })
    EVENT_IDS.extend(club[0])
    CLUBS[club[1]]['total-announcements'] += 1

@app.route("/")
def index():
    return render_template('layout.html',CLUBS=CLUBS)


# logout all active users
@app.route("/logout")
def logout_all(display_flash=True):
    if 'user_id' in session or 'admin-logged-in' in session:
        # Create cursor
        database = getDBConnection()
        cur = database.cursor()
        x = '0'
        cur.execute("UPDATE users SET online=%s", [x])
        database.commit()
        cur.execute("UPDATE admins SET online=%s", [x])
        database.commit()
        database.close()
        cur.close()
        session.clear()
        if display_flash:
            flash("Logged Out Successfully", 'success')
        print("Logged Out Successfully")
    return redirect('/')


@app.route("/user/<string:user_id>/logout")
def logout(user_id):
    user_id = user_id.upper()
    if 'user_id' in session and session['user_id'] == user_id:
        # Create cursor
        database = getDBConnection()
        cur = database.cursor()
        user_id = session['user_id']
        x = '0'
        cur.execute("UPDATE users SET online=%s WHERE id=%s", (x, user_id))
        database.commit()
        database.close()
        cur.close()
        session.clear()
        print("Logged Out Successfully")
        flash("Logged Out Successfully", 'success')
        return redirect(url_for('index'))
    else:
        flash(f"User with ID '{user_id}' Is Not Logged In", 'error')
        return redirect('/login')


class LoginForm(Form):
    user_id = StringField(
        '', [validators.DataRequired()], render_kw={'autofocus': True, 'placeholder': 'Username'})
    password = PasswordField('', [validators.DataRequired()], render_kw={
                             'placeholder': 'Password'})


@app.route('/user/<string:user_id>')
def logged_in(user_id):
    user_id = user_id.upper()
    if 'user_id' in session and session['user_id'] == user_id:
        database = getDBConnection()
        cur = database.cursor()
        user_id = session['user_id']
        cur.execute('SELECT * FROM users WHERE ID=%s', [user_id])
        res = cur.fetchone()

        cur.execute(
            'SELECT InterestedActivities FROM users WHERE ID=%s', [user_id])
        interested_events_ids = [x for x in cur.fetchone()][0]
        interested_events_ids = interested_events_ids.split(',')
        # print(interested_events_ids)

        event_data = []
        for event in interested_events_ids:
            # print(event)
            cur.execute('SELECT * FROM club_events WHERE EventID=%s', [event])
            _event = cur.fetchone()
            # print(_event)
            if _event != None:
                _event=list(_event)
                _event[2]=datetime.strptime(_event[2], '%Y-%m-%d').strftime('%d/%m/%Y')
                event_data.append(_event)
        name = f'{res[0]} {res[1]}'
        database.close()
        cur.close()
        # print(event_data)

        return render_template('logged-in-homepage.html',user_id=user_id ,name=name,CLUBS=CLUBS, event_data=event_data, length=len(event_data))
    else:
        flash(f"User with ID '{user_id}' Is Not Logged In", 'error')
        print(f"User with ID '{user_id}' Is Not Logged In")
        return redirect('/login')


@app.route("/login", methods=['GET', 'POST'])
def login():
    # someone is already logged in
    if 'user_id' in session:
        return redirect('/user/'+session['user_id'])

    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        # Get user form
        user_id = str(form.user_id.data).strip().upper()
        # password_candidate = request.form['password']
        password_candidate = str(form.password.data)

        # Create cursor
        database = getDBConnection()
        mycursor = database.cursor()

        # Get user by username
        result = None
        mycursor.execute(
            "SELECT * FROM users WHERE ID=%s", [user_id])
        result = mycursor.fetchone()

        if result != None:
            # Get stored value
            password = result[3]
            user_id = result[2]
            name = result[0] + ' ' + result[1]

            # Compare password
            if sha256_crypt.verify(password_candidate, password):
                session['user_id'] = user_id
                x = '1'
                mycursor.execute(
                    "UPDATE users SET online=%s WHERE id=%s", (x, user_id))
                database.commit()
                print("Successful Login : Hello", name)
                return redirect('/user/'+user_id)
            else:
                print("Wrong Password")
                flash('Incorrect Password', 'error')

        else:
            print("User Not Found")
            flash('User Not Found', 'error')
        # Close connection
        mycursor.close()
        database.close()
    return render_template('login-page.html', form=form)


class RegisterForm(Form):
    first_name = StringField(
        '', [validators.Length(max=20), validators.DataRequired()], render_kw={'autofocus': True, 'placeholder': 'First Name'})
    last_name = StringField(
        '', [validators.Length(max=20), validators.DataRequired()], render_kw={'placeholder': 'Last Name'})
    user_id = StringField(
        '', [validators.Length(min=2, max=10), validators.DataRequired()], render_kw={'placeholder': 'University ID'})
    password = PasswordField('', [validators.Length(
        min=5), validators.DataRequired()], render_kw={'placeholder': 'Password'})


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)

    if request.method == "POST" and form.validate():

        database = getDBConnection()
        mycursor = database.cursor()

        fname = str(form.first_name.data).strip().title()
        lname = str(form.last_name.data).strip().title()
        user_id = str(form.user_id.data).strip().upper()

        # get all id s and check if incoming id is not already present
        mycursor.execute('SELECT ID FROM users')
        res = mycursor.fetchall()
        res = [x[0] for x in res]

        if user_id in res:
            flash("USER ID is Already Registered !")
        else:
            password = sha256_crypt.hash(str(form.password.data))

            mycursor.execute(
                "INSERT INTO users values (%s,%s,%s,%s,%s,%s)",
                (fname, lname, user_id, password, '0',''))
            print(
                f"Successfully Registered User : {fname} {lname} [{user_id}]")
            flash(
                f"Successfully Registered User : {fname} {lname} [{user_id}]", 'success')

            database.commit()
            mycursor.close()
            database.close()

            return redirect('/login')

    return render_template('register-page.html', form=form)


@app.route("/clubs/")
def clubs():
    return render_template('clubs/clubs.html', CLUBS=CLUBS)

@app.route('/clubs/<string:club_name>/events/add-to-fav/<string:EventID>')
def add_to_favourite(club_name,EventID):
    if 'user_id' in session:
        database=getDBConnection()
        cursor=database.cursor()
        cursor.execute("SELECT InterestedActivities FROM users WHERE ID=%s",[session['user_id']])
        res=cursor.fetchone()[0]
        if EventID in res:
            flash("Event Already in Favourites",'message')
        else:
            res+=EventID+','
            cursor.execute("UPDATE users SET InterestedActivities=%s WHERE ID=%s",(res,session['user_id']))
            database.commit()
            database.close()
            cursor.close()
            flash("Added To Favourites")
        return redirect('/clubs/'+club_name+'/events')
    else:
        flash("You Need to Login Before Adding Events To Favourites",'error')
        return redirect('/login')
    
@app.route('/admin/login')
def login_admin():
    return 'login admin here'


@app.route('/clubs/<string:club_name>/events/remove-from-fav/<string:EventID>')
def remove_from_favourite(club_name,EventID):
    if 'user_id' in session:
        database=getDBConnection()
        cursor=database.cursor()
        cursor.execute("SELECT InterestedActivities FROM users WHERE ID=%s",[session['user_id']])
        res=cursor.fetchone()[0]
        # print("res",res)
        res=res.replace(EventID+",","")
        # print("res",res)
        cursor.execute("UPDATE users SET InterestedActivities=%s WHERE ID=%s",(res,session['user_id']))
        database.commit()
        database.close()
        cursor.close()
        flash("Removed From Favourites")
        return redirect('/user/'+session['user_id'])
    else:
        flash("You Need to Login Before Adding Events To Favourites",'error')
        return redirect('/login')

@app.route("/clubs/<string:club_name>/home")
def club_names_home(club_name):
    if club_name in CLUBS:
        return render_template('clubs/clubs-string.html', CLUBS=CLUBS, name_of_club=club_name, show_events=0)
    else:
        return render_template('404.html')


@app.route("/clubs/<string:club_name>/events")
def club_names_events(club_name):
    if club_name in CLUBS:
        if 'user_id' in session:
            # user is logged in
            return render_template('clubs/clubs-string.html', CLUBS=CLUBS, name_of_club=club_name, show_events=1)
        else:
            flash("You Need to Login to Access Club Events Data")
            return redirect('/login')
    else:
        return render_template('404.html')

@app.route("/clubs/<string:club_name>/admin")
def club_names_admin(club_name):
    if 'admin-logged-in' in session and session['admin-logged-in']==club_name:
        return render_template('clubs/clubs-admin.html', CLUBS=CLUBS, name_of_club=club_name)
    else:
        flash("Admin For "+ CLUBS[club_name]['name'] +" Not Logged In",'error')
        return redirect('/clubs/'+club_name+'/admin/login')

@app.route("/clubs/<string:club_name>/admin/logout")
def logout_admin(club_name):
    if 'admin-logged-in' in session and session['admin-logged-in'] == club_name:
        # Create cursor
        database = getDBConnection()
        cur = database.cursor()
        x = '0'
        cur.execute("UPDATE admins SET online=%s WHERE URL_Name=%s", (x, club_name))
        database.commit()
        database.close()
        cur.close()
        session.clear()
        print("Logged Out Successfully")
        flash("Logged Out Successfully", 'success')
        return redirect(url_for('index'))
    else:
        flash(f"Admin for '{club_name}' Is Not Logged In", 'error')
        return redirect('/login')

class AddEvent(Form):
    date = DateField('', [validators.DataRequired()], render_kw={
                     'autofocus': True, 'placeholder': 'Event Date ?'})
    venue = StringField('', [validators.DataRequired()], render_kw={
                        'placeholder': 'Event Venue'})
    time = StringField('', [validators.DataRequired()],
                       render_kw={'placeholder': 'Event Time'})
    description = StringField('', [validators.DataRequired()], render_kw={
                              'placeholder': 'Event Description'})

# add a new event
@app.route("/clubs/<string:club_name>/admin/add", methods=['GET', 'POST'])
def club_names_add_event(club_name):
    # CLUBS,EVENT_IDS=updateCLUBS(CLUBS,EVENT_IDS)
    if club_name in CLUBS:
        if 'admin-logged-in' in session and session['admin-logged-in']==club_name:

            form = AddEvent(request.form)

            if request.method == "POST" and form.validate():
                database = getDBConnection()
                mycursor = database.cursor()

                description = str(form.description.data).strip()
                date = str(form.date.data).strip()
                time = str(form.time.data).strip().upper()
                venue = str(form.venue.data).strip().upper()

                # generate random id
                while True:
                    random_id = generateRandomID()
                    if not random_id in EVENT_IDS:
                        break

                mycursor.execute("INSERT INTO club_events VALUES(%s,%s,%s,%s,%s,%s)",
                                (random_id, club_name, date, time, venue, description))
                database.commit()

                mycursor.close()
                database.close()

                CLUBS[club_name]['announcements'].append(
                    {
                        'id':random_id,
                        'URL_Name':club_name,
                        'date':date,
                        'time':time,
                        'venue':venue,
                        'description':description
                    })
                CLUBS[club_name]['total-announcements'] += 1
                EVENT_IDS.append(random_id)

                # CLUBS,EVENT_IDS=updateCLUBS(CLUBS,EVENT_IDS)
                flash(f"Event Added Succesfully [ID : {random_id}]")
        else:
            # admin not logged in 
            flash("Admin For " + CLUBS[club_name]['name'] + " Not Logged In",'error')
            return redirect('/clubs/'+club_name+'/admin/login')
        return render_template('clubs/clubs-add-event.html', CLUBS=CLUBS, name_of_club=club_name, form=form)
    else:
        flash(f"Club '{club_name}' Does Not Exist", 'error')
        return redirect('/')


class AdminLogin(Form):
    password = PasswordField('', [validators.DataRequired()], render_kw={
                             'autofocus': True, 'placeholder': 'Password'})
class ModifyEvent(Form):
    date = DateField('', [validators.DataRequired()], render_kw={
                        'autofocus': True, 'placeholder': 'Event Date ?'})
    venue = StringField('', [validators.DataRequired()], render_kw={
                        'placeholder': 'Event Venue'})
    time = StringField('', [validators.DataRequired()],
                       render_kw={'placeholder': 'Event Time'})
    description = StringField('', [validators.DataRequired()], render_kw={
                              'placeholder': 'Event Description'})

@app.route("/clubs/<string:club_name>/admin/modify/<string:EventID>", methods=['GET', 'POST'])
def clubs_modify_event(club_name,EventID):
    if club_name in CLUBS:
        if 'admin-logged-in' in session and session['admin-logged-in']==club_name:
            database=getDBConnection()
            cursor=database.cursor()
            cursor.execute("SELECT * FROM club_events WHERE EventID=%s",[EventID])
            res=cursor.fetchone()
            print(res)

            form=ModifyEvent(request.form,date=datetime.strptime(res[2],'%Y-%m-%d').date(),time=res[3],venue=res[4],description=res[5])
            if request.method=="POST" and form.validate():
                description = str(form.description.data).strip()
                date = str(form.date.data).strip()
                time = str(form.time.data).strip()
                venue = str(form.venue.data).strip()

                cursor.execute("""
                UPDATE club_events
                SET 
                    EventDate = %s,
                    EventTime = %s,
                    EventVenue = %s,
                    EventDescription = %s
                WHERE
                    EventID=%s;
                """,(date,time,venue,description,EventID))
                database.commit()
                flash("Event Modified Successfully",'message')


                for event in CLUBS[club_name]['announcements']:
                    if event['id']==EventID:
                        event['date']=datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
                        event['time']=time
                        event['venue']=venue
                        event['description']=description
                        break

            database.close()
            cursor.close()
        else:
            flash("Admin For " + CLUBS[club_name]['name'] + " Not Logged In",'error')
            return redirect('/clubs/'+club_name+'/admin/login')
        return render_template('clubs/clubs-add-event.html', CLUBS=CLUBS, name_of_club=club_name, form=form)

    else:
        flash(f"Club '{club_name}' Does Not Exist", 'error')
        return redirect('/')

@app.route("/clubs/<string:club_name>/admin/delete/<string:EventID>", methods=['GET', 'POST'])
def clubs_delete_event(club_name,EventID):
    if club_name in CLUBS:
        if 'admin-logged-in' in session and session['admin-logged-in']==club_name:
            database=getDBConnection()
            cursor=database.cursor()
            # cursor.execute("SELECT E FROM club_events WHERE EventID=%s",[EventID])
            # res=cursor.fetchall()
            cursor.execute("DELETE FROM club_events WHERE EventID=%s",[EventID])
            database.commit()
            database.close()
            cursor.close()

            # print(res)

            # index=CLUBS[club_name]['ids'].index(EventID)
            for event in CLUBS[club_name]['announcements']:
                if event['id']==EventID:
                    del CLUBS[club_name]['announcements'][CLUBS[club_name]['announcements'].index(event)]
                    break

            # CLUBS[club_name]['announcements'].pop(index)
            # CLUBS[club_name]['ids'].pop(index)
            CLUBS[club_name]['total-announcements'] -= 1
            # CLUBS[club_name]['date'].pop(index)
            # CLUBS[club_name]['time'].pop(index)
            # CLUBS[club_name]['venue'].pop(index)
            # EVENT_IDS.remove(EventID)
            print("Deleted Event")
            flash("Deleted Event with ID : "+EventID,'message')
            return redirect('/clubs/'+club_name+'/admin')
        else:
            flash("Admin For " + CLUBS[club_name]['name'] + " Not Logged In",'error')
            return redirect('/clubs/'+club_name+'/admin/login')
    else:
        flash(f"Club '{club_name}' Does Not Exist", 'error')
        return redirect('/')

@app.route("/clubs/<string:club_name>/admin/login", methods=['GET', 'POST'])
def admin_login(club_name):
    if club_name in CLUBS:

        if 'admin-logged-in' in session and session['admin-logged-in']==club_name:
            return redirect('/clubs/'+club_name+'/admin')

        form = AdminLogin(request.form)
        if request.method == "POST" and form.validate():
            password_entered = str(form.password.data)
            database = getDBConnection()
            cursor = database.cursor()
            cursor.execute(
                "SELECT Password FROM admins WHERE URL_Name=%s", [club_name])
            res = cursor.fetchone()[0]

            if sha256_crypt.verify(password_entered,res):
                session['admin-logged-in']=club_name
                cursor.execute("UPDATE admins SET Online='1' WHERE URL_Name=%s",[club_name])
                database.commit()
                database.close()
                cursor.close()
                return redirect('/clubs/'+club_name+'/admin')
            else:
                flash("Incorrect Password",'error')
    else:
        flash("Club Not Found", 'error')
        return redirect('/clubs')
    return render_template('admin-login.html', form=form,name=CLUBS[club_name]['name'])

# ERROR HANDLING


@app.errorhandler(404)
# inbuilt function which takes error as parameter
def not_found(e):
    # defining function
    return render_template("404.html")


if __name__ == "__main__":
    # EVENT_IDS = []
    # # global CLUBS
    # CLUBS = {}
    # CLUBS,EVENT_IDS=updateCLUBS(CLUBS,EVENT_IDS)
    app.run()
