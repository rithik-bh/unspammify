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
    

# club_names = [
#     ['Silhouette Club', 'Silhouette club is the creative society of the university, which aims to promote the rich and vibrant art by organizing activities like painting, sketching, calligraphy, decoration, craft work, graffiti and contemporary designing. The club hosts various exhibitions, workshops and competitions. It also organizes trips to art museums and encourages students to participate in college fests.'],
#     ['MUN Society', 'The MUN society focuses on enhancing the student experience by providing a platform to improve skills like critical thinking, public speaking, group communication, & research and policy analysis. The society follows the United Nations core values of Integrity, Professionalism and Respect for Diversity, and aims to create leaders of tomorrow. Its activities include organizing and hosting workshops, debates and MUN conferences.'],
#     ['Alexis Club', 'Alexis is not merely a club but an outlet and a platform for the students who want to work for the society and leave a mark. The club conducts activities to protect the nature and also provide students with opportunities to work for the welfare of the society. Alexis is involved in various initiatives like teaching the underprivileged, organizing visits to places like old age homes, an orphanage, yoga, meditation, tree plantation, etc.'],
#     ['Robotics Club', 'The club helps the students to form a brief understanding of various concepts and dynamics of Robotics. Students of the Robotics Club attend workshops, hold competitions and take part in different events to strengthen their technical skills'],
#     ['Pulse', "The basic idea behind this club is to promote healthy adventure activities like river rafting, trekking and camping. The club aims at familiarizing the students with the beauty and the thrill that’s hidden in nature. Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged."],
#     ['Cerebrum Club', 'Cerebrum Club as the name suggests is a group of travel enthusiats and adventure sports lovers. The club aims to make students experience the beauty and the thrill that’s hidden in nature. The members participates in adventure activities like river rafting, trekking and camping.'],
#     ['Flucs', "The basic idea behind this club is to promote healthy adventure activities like river rafting, trekking and camping. The club aims at familiarizing the students with the beauty and the thrill that’s hidden in nature. Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged."],
#     ['Spark Club',
#         'SPARK is a student Club which closely works with the Centre for Innovation and Entrepreneurship (CIE) and the Bennett Hatchery to nurture creativity and an entrepreneurial bent of mind amongst students. Our objectives include: encouraging creative thinking, supporting future start upfounders, and facilitating interaction with entrepreneurs, industry expertsand venture capitalists.'],
#     ['Nomads', 'Nomads club as the name suggests is a group of travel enthusiats and adventure sports lovers. The club aims to make students experience the beauty and the thrill that’s hidden in nature. The members participates in adventure activities like river rafting, trekking and camping.'],
#     ['Spice Macay Club', 'This is the society for the promotion of Indian classical music and culture amongst youth. The university through this club organizes various cultural events to keep the students rooted to Indian culture and traditions.'],
#     ['Virtuoso Club', 'This club is the spice of the University with its fathomless zest and exuberance towards dance, drama and music. The club sponsors the deserving students in big events and organizes activities to unearth the hidden talent.'],
#     ['ISAAC Club', """
#         The Photography Club is a platform built for photography Beginners, Amateurs, Enthusiasts and Hobbyists, on an idea to connect every photography enthusiast by a common thread. We are growing on a single set of mind where everyone is welcome to join us, and stimulate the inception of new ideas in this visual art. We are here in order to inculcate and motivate the art of photography in our students.
#         We are a place where people are not judged by their skills, rather they have to come up with enthusiasm, and rest we help them in providing the right expertise. We are there to give the support to one other and learn from the unlearned skills from our team as well as build on each other's artistry. We seek to display our love of photography through the constructive criticism of our peers, leisure activities, and the promotion of photography throughout the campus and carve a niche for ourselves as a club on different platforms.
#         We are an inclusive club, where we also promote creative videography. We welcome all sorts of individuals to come and join us over our monthly sessions, discuss their aspirations and creativity, find the like minded people and transform them through various club activities.
#     """],
#     ['Astronomy Club', 'Astronomy Club as the name suggests is a group of travel enthusiats and adventure sports lovers. The club aims to make students experience the beauty and the thrill that’s hidden in nature. The members participates in adventure activities like river rafting, trekking and camping.']
# ]


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

# def updateCLUBS(CLUBS,EVENT_IDS):
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
    CLUBS[club[1]]['ids'] = []
    CLUBS[club[1]]['date'] = []
    CLUBS[club[1]]['time'] = []
    CLUBS[club[1]]['venue'] = []
    CLUBS[club[1]]['total-announcements'] = 0

for club in club_data:
    CLUBS[club[1]]['announcements'].append(club[5])
    CLUBS[club[1]]['ids'].append(club[0])
    CLUBS[club[1]]['date'].append(club[2])
    CLUBS[club[1]]['time'].append(club[3])
    CLUBS[club[1]]['venue'].append(club[4])
    EVENT_IDS.extend(CLUBS[club[1]]['ids'])
    CLUBS[club[1]]['total-announcements'] += 1


    # return CLUBS,EVENT_IDS

# INTERESETED_EVENTS=[]

# def getClubData(club_name):
#     database = getDBConnection()
#     cur = database.cursor()
#     cur.execute("SELECT * FROM club_events WHERE URL_Name=%s",[club_name])
#     res = cur.fetchall()
#     database.close()
#     cur.close()
#     return res



@app.route("/")
def index():
    return render_template('layout.html')


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
                event_data.append(_event)
        name = f'{res[0]} {res[1]}'
        database.close()
        cur.close()
        # print(event_data)

        return render_template('logged-in-homepage.html',user_id=user_id ,name=name, event_data=event_data, length=len(event_data))
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

                CLUBS[club_name]['announcements'].append(description)
                CLUBS[club_name]['ids'].append(random_id)
                CLUBS[club_name]['total-announcements'] += 1
                CLUBS[club_name]['date'].append(date)
                CLUBS[club_name]['time'].append(time)
                CLUBS[club_name]['venue'].append(venue)
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
            # print(res)

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

                index=CLUBS[club_name]['ids'].index(EventID)
                CLUBS[club_name]['announcements'][index]=description
                CLUBS[club_name]['date'][index]=date
                CLUBS[club_name]['time'][index]=time
                CLUBS[club_name]['venue'][index]=venue

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

            index=CLUBS[club_name]['ids'].index(EventID)

            CLUBS[club_name]['announcements'].pop(index)
            CLUBS[club_name]['ids'].pop(index)
            CLUBS[club_name]['total-announcements'] -= 1
            CLUBS[club_name]['date'].pop(index)
            CLUBS[club_name]['time'].pop(index)
            CLUBS[club_name]['venue'].pop(index)
            EVENT_IDS.remove(EventID)

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
