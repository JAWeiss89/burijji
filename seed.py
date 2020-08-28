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

# Seed chatroom
lounge = Chatroom(roomcode="lounge", name="Lounge")


db.session.add(lounge)
db.session.commit()

