from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///temperature.db'
db = SQLAlchemy(app)

# Define the Temperature model
class Temperature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    
    def commit(self):
       db.session.add(self)
       db.session.commit()

@app.route("/")
def homepage():
    return "Home page"
    
@app.route("/get_json", methods=['POST'])
def get_post_temp():
    #Create temperature.db if abs
    db.create_all()
    
    #Grabe data from post expect {'date_time':isoformat_datetime(string), 'temperature':float}
    data = request.get_json()
    date_time = datetime.fromisoformat(data['date_time'])
    temperature=data['temperature']
    
    # Create new Temperature object and add to database
    tmp = Temperature(date_time=date_time, temperature=temperature)
    tmp.commit()
    
    # Return response with HTTP status code 201 Created
    return jsonify(message='Temperature added'), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
