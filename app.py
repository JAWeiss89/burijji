from flask import Flask, render_template, redirect, session
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.secret_key = 'mysecret'

socketio = SocketIO(app) # initialize socket io



@app.route("/")
def show_index_pg():
    """ Gets home page """
    return render_template('index.html')


@socketio.on('message')
def message(data):

    print(f"\n\n{data}\n\n")
    
    send(data, broadcast=True) #This will send the message to connected clients
    

if __name__ == '__main__':
    app.run()