from flask import Flask, render_template, request, redirect, session, flash, jsonify
from models import connect_db, db, User, Language, Chatroom, Membership, Message
from forms import RegisterForm, LoginForm, ChatroomForm
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from time import localtime, strftime
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET')
app.config['SECRET_KEY'] = os.environ.get('SECRET', 'abc123')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', "postgres:///burijji_db" )
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

connect_db(app)
# db.drop_all()
db.create_all() # create all tables in database
socketio = SocketIO(app) # initialize socket io


# ===================================
# FLASK ROUTE HANDLING
# ===================================


@app.route("/")
def show_home_pg():
    """ Gets home page """
    if session.get('user_id'):

        user = User.query.get(session["user_id"])

        return render_template('home.html', user=user)

    return render_template('index.html')



@app.route("/login", methods=["GET", "POST"])
def handle_user_login():
    """ Shows or handles user login form """
    form = LoginForm()

    if form.validate_on_submit(): # checks if POST req && if request is coming from out form (not external)

        username = form.username.data
        typed_password = form.password.data

        authenticated_user = User.authenticate(username, typed_password)

        if authenticated_user :
            session["user_id"] = authenticated_user.id 
            return redirect("/chat")
        
        else :
            flash("Could not authenticate")
            return redirect("/")

    return render_template('login.html', form=form)

@app.route("/register", methods=["GET", "POST"])
def handle_user_registration():
    """ Shows or handles user registration form """
    form = RegisterForm()

    if form.validate_on_submit():  # checks if POST req && if request is coming from out form (not external)

        first_name = form.first_name.data
        last_name = form.last_name.data
        username = form.username.data
        password = form.password.data
        email = form.email.data
        preferred_language = form.preferred_language.data
        
        user = User.register(first_name, last_name, username, password, email, preferred_language)

        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id

        return redirect("/chat")
        
    else :
        return render_template('register.html', form=form)



@app.route("/chat")
def show_chat():
    """ Gets chatroom page """

    if not session.get('user_id'):
        return redirect('/')

    user = User.query.get(session['user_id'])

    return render_template('chatroom.html', user=user)


@app.route("/logout", methods=["POST"])
def logout():
    """ Handle logout functionality """
    session.pop('user_id')

    return redirect("/")


# ===================================
# AJAX ROUTES
# ===================================

@app.route("/chatroom/<roomcode>/messages")
def get_old_messages(roomcode) :

    chatroom = Chatroom.query.filter_by(roomcode=roomcode).first()
    if chatroom :
        messages = serialize_message_objs(chatroom.messages)
        return jsonify(messages)
    else :
        return jsonify(errors="No Messages Yet")

# ===================================
# SOCKET-IO HANDLING
# ===================================


@socketio.on('message')
def message(data):

    # For real-time messaging
    user = User.query.get(session["user_id"])
    username = user.username
    time = strftime("%b-%d %I:%M%p", localtime())

    
    
    send({'msg': data['msg'], 'user': username, 'time':time}, room=data['room'], broadcast=True) 
    
    # For posting to DB
    # need user_id(from session), chatroom_id(use query), language_id(use query), timestampt(use above), content(use data['message'])
    chatroom = Chatroom.query.filter_by(roomcode=data['room']).first() #Change search to roomcode since that will be the unique identiifer
    language = Language.query.filter_by(name=user.preferred_language).first()

    new_message = Message(user_id=session["user_id"], chatroom_id=chatroom.id, language_id=language.id, timestamp=time, content=data['msg'])

    db.session.add(new_message)
    db.session.commit()

@socketio.on('join')
def join(data):
    # For socket-io joining
    user = User.query.get(session["user_id"])
    username = user.username

    join_room(data['room'])
    send({'msg': f"{username} has joined the room {data['room']}"}, room=data['room'])

    # Does chatroom exist in db? If not, create it. 
    chatroom = Chatroom.query.filter_by(roomcode=data['room']).first() #Change search to roomcode since that will be the unique identiifer

    if not chatroom :
        chatroom = Chatroom(roomcode = data['room'], name=data['roomname'])

        db.session.add(chatroom)
        db.session.commit()

    # Make user a member of this chatroom if not already member
    
    if chatroom not in user.chatrooms and chatroom.id not in [1,2,3,4]:
        new_membership = Membership(user_id=user.id, chatroom_id=chatroom.id, is_admin=True)

        db.session.add(new_membership)
        db.session.commit()


    

@socketio.on('leave')
def leave(data):

    user = User.query.get(session["user_id"])
    username = user.username

    leave_room(data['room'])
    send({'msg': f"{username} has left the room."}, room=data['room'])



# =======================================
# HELPER FUNCTIONS
# =======================================

def serialize_message_objs(messages):
    msg_list=[]
    for message in messages:
        msgObj= {'msg': message.content, 'time': message.timestamp, 'user': message.user.username}
        msg_list.append(msgObj)

    return msg_list


if __name__ == '__main__':
    app.run()