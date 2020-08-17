from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, send
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET')
app.config['SECRET_KEY'] = 'aaaaa'

socketio = SocketIO(app) # initialize socket io



@app.route("/")
def show_landing_pg():
    """ Gets home page """
    return render_template('landing.html')

@app.route("/", methods=["POST"])
def handle_form():
    """ Get name and add to session """
    name = request.form.get('name')
    print(name)
    session['name'] = name
    print(session['name'])

    return redirect('/chat')


@app.route("/chat")
def show_chat():
    """ Gets home page """
    return render_template('index.html')


@socketio.on('message')
def message(data):

    # print(f"\n\n{data}\n\n")
    edited = f"{session['name']}: {data}"
    
    send(edited, broadcast=True) #This will send the message to connected clients
    

if __name__ == '__main__':
    app.run()