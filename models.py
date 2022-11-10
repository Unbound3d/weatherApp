from main import db, app

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


with app.app_context():
        #test code
        db.create_all()