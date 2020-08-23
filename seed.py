from app import app
from models import db, Language, Chatroom

# Seed languages
english = Language(name="english")
spanish = Language(name="spanish")
portuguese = Language(name="portuguese")

db.session.add(english)
db.session.add(spanish)
db.session.add(portuguese)

db.session.commit()

# Seed chatrooms
lounge = Chatroom(roomcode="lounge", name="Lounge")
politics = Chatroom(roomcode="politics", name="Politics")
sports = Chatroom(roomcode="sports", name="Sports")
food = Chatroom(roomcode="food", name="Food")

db.session.add(lounge)
db.session.add(politics)
db.session.add(sports)
db.session.add(food)

db.session.commit()

