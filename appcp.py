import datetime
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

# Define the Temperature model
class Temperature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
        def __repr__(self):
        return '<Temperature {}>'.format(self.temperature)

@app.route("/")
def homepage():
    return "Home page"
    
@app.route("/get_json", methods=['POST'])
def get_post_temp():
    data = request.get_json()
    y = data['year']
    mo = data['month']
    d = data['day']
    h = data['hour']
    mi = data['minute']
    s = data['second']
    t = float(data['temp'])
    dt = datetime.datetime(y, mo, d, h, mi, s)
    new_temp = Temperature(date_time=dt, temperature=t)
    db.session.add(new_temp)
    db.session.commit()
    
    #add datetime and temp to db
    return jsonify('200')



if __name__ == "__main__":
    app.run(host="0.0.0.0")
