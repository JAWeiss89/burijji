from flask import Flask, render_template, request, redirect, session, flash, jsonify
from models import connect_db, db, User, Language, Chatroom, Membership, Message
from forms import RegisterForm, LoginForm, ChatroomForm
from translate import translate

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

        return redirect("/chat")

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

    return render_template('chatroom2.html', user=user)



@app.route("/language", methods=["POST"])
def change_user_language() :
    user_id = session["user_id"]
    user = User.query.get(user_id)

    new_language = request.form["language"]
    user.preferred_language = new_language

    db.session.add(user)
    db.session.commit()

    return redirect("/chat")


@app.route("/logout", methods=["POST"])
def logout():
    """ Handle logout functionality """
    session.pop('user_id')

    return redirect("/")




# ===================================
# AJAX ROUTES
# ===================================

@app.route("/chatroom/<roomcode>/info")
def get_meeting_info(roomcode) :

    meeting = Chatroom.query.filter_by(roomcode=roomcode).first()
    if meeting :
        messages = serialize_message_objs(meeting.messages)
        users = serialize_user_objs(meeting.users)
        info = {"name": meeting.name, "roomcode": meeting.roomcode}
        return jsonify(info=info, messages=messages, users=users)
    else :
        return jsonify(errors="Meeting not found")


@app.route("/chatroom/<roomcode>/unsubscribe")
def unsubscribe_from_meeting(roomcode) :

    meeting = Chatroom.query.filter_by(roomcode=roomcode).first()
    if meeting :
        user_id = session["user_id"]
        meeting_id = meeting.id

        membership = Membership.query.filter_by(user_id = user_id, chatroom_id = meeting_id).first()
        
        db.session.delete(membership)
        db.session.commit()

        return jsonify(msg= "Unsubscribed Succesfully")

    else :
        return jsonify(msg= "Error: could not find meeting to unsubscribe")

# ===================================
# SOCKET-IO HANDLING
# ===================================


@socketio.on('message')
def message(data):

    # Data that passes through here is coming from client-side
    
    user = User.query.get(session["user_id"])
    username = user.username
    orig_message = data["msg"]
    orig_language = user.preferred_language
    time = strftime("%b-%d %I:%M%p", localtime())

    
    # FOR REAL TIME MESSAGING
    
    # Send received message to all connected users
    send({'msg': orig_message, 'user': username, 'time':time, 'language': orig_language}, room=data['room'], broadcast=True) 

    # Now translate message into other languages and also send to all connected users
    if orig_language != 'spanish' :
        #translate
        msg_es = translate(orig_message, 'es')
        send({'msg': msg_es, 'user': username, 'time':time, 'language': 'spanish'}, room=data['room'], broadcast=True) 

    if orig_language != 'english' :
        #translate
        msg_en = translate(orig_message, 'en')
        send({'msg': msg_en, 'user': username, 'time':time, 'language': 'english'}, room=data['room'], broadcast=True) 

    if orig_language != 'portuguese' :
        #translate
        msg_pt = translate(orig_message, 'pt')
        send({'msg': msg_pt, 'user': username, 'time':time, 'language': 'portuguese'}, room=data['room'], broadcast=True) 


    # FOR POSTING TO DATABASE

    # Post received message to database
    chatroom = Chatroom.query.filter_by(roomcode=data['room']).first() #Change search to roomcode since that will be the unique identiifer
    language = Language.query.filter_by(name=user.preferred_language).first()

    new_message = Message(user_id=session["user_id"], chatroom_id=chatroom.id, language_id=language.id, timestamp=time, content=data['msg'])
    db.session.add(new_message)
    db.session.commit()

    # Send translated messages to database
    
    if orig_language != 'spanish' :
        new_message_es = Message(user_id=session["user_id"], chatroom_id=chatroom.id, language_id=2, timestamp=time, content=msg_es, is_translated=True)
        db.session.add(new_message_es)
        db.session.commit()

    if orig_language != 'english' :
        new_message_en = Message(user_id=session["user_id"], chatroom_id=chatroom.id, language_id=1, timestamp=time, content=msg_en, is_translated=True)
        db.session.add(new_message_en)
        db.session.commit()

    if orig_language != 'portuguese' :
        new_message_pt = Message(user_id=session["user_id"], chatroom_id=chatroom.id, language_id=3, timestamp=time, content=msg_pt, is_translated=True)
        db.session.add(new_message_pt)
        db.session.commit()


@socketio.on('new_meeting_request')
def new_meeting_req(data):
    # Check if this is a request to create a new meeting or join one already in db
    current_room = data['currentroom']
    user_id = session["user_id"]
    if data.get('roomname'):
        roomname = data['roomname']
        roomcode = data['roomcode']

        # Request is to create a new meeting
        meeting = Chatroom(roomcode=roomcode, name=roomname)

        db.session.add(meeting)
        db.session.commit()

        send({'msg': 'Meeting created', 'join_request': 'success', 'roomcode': roomcode, 'roomname': roomname, 'user_id': user_id}, room=current_room)

    else :
        roomcode = data['roomcode']
        chatroom = Chatroom.query.filter_by(roomcode=roomcode).first()
        

        if not chatroom:
            send({'msg': 'Could not find meeting.', 'join_request': 'failed'}, room=current_room)
        else :
            roomname = chatroom.name
            send({'msg': 'Request granted.', 'join_request': 'success', 'roomcode': roomcode, 'roomname': roomname, 'user_id': user_id}, room=current_room)

        


@socketio.on('join')
def join(data):
    # For socket-io joining
    user = User.query.get(session["user_id"])
    username = user.username
    room = data['room']
    
    found_room = Chatroom.query.filter_by(roomcode=room).first()
    roomname = found_room.name

    join_room(room)
    send({'msg': f"{username} has joined the meeting {roomname}"}, room=room)

                # Does chatroom exist in db? If not, create it. 
                # chatroom = Chatroom.query.filter_by(roomcode=data['room']).first() #Change search to roomcode since that will be the unique identiifer

                # if not chatroom :
            
                #     chatroom = Chatroom(roomcode = data['room'], name="FAKE NAME") # THIS IS BREAKING BECAUSE INCOMING DOESNT HAVE CHATROOM NAME

                #     db.session.add(chatroom)
                #     db.session.commit()

    # Make user a member of this chatroom if not already member
    
    if found_room not in user.chatrooms and found_room.id not in [1,2,3,4]:
        new_membership = Membership(user_id=user.id, chatroom_id=found_room.id, is_admin=True)

        db.session.add(new_membership)
        db.session.commit()


    

@socketio.on('leave')
def leave(data):

    user = User.query.get(session["user_id"])
    username = user.username
    room = data['room']

    leave_room(room)
    send({'msg': f"{username} has left the meeting."}, room=room)



# =======================================
# HELPER FUNCTIONS
# =======================================

def serialize_message_objs(messages):
    msg_list=[]
    languages = {1:'english', 2:'spanish', 3:'portuguese'}


    for message in messages:
        msgObj= {'msg': message.content, 'time': message.timestamp, 'user': message.user.username, 'language': languages[message.language_id]}
        msg_list.append(msgObj)

    return msg_list

def serialize_user_objs(users):
    user_list=[]

    for user in users:
        user_obj= {'username': user.username}
        user_list.append(user_obj)

    return user_list

if __name__ == '__main__':
    app.run()