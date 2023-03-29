from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Set the URI for the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///temperature.db'

# Initialize SQLAlchemy
db = SQLAlchemy(app)


class Temperature(db.Model):
    """
    A model representing a temperature measurement with a timestamp.
    """

    # Define the columns of the Temperature table
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    
    def commit(self):
       """
       Add the current Temperature object to the database.
       """
       db.session.add(self)
       db.session.commit()
       db.session.close()
       
    def get_recent_temperature(self, limit=10):
        """ 
        Parameters
        ----------
        limit : TYPE, int
            DESCRIPTION. The default is 10.

        Returns list of tuple (date_time, temperature)
        -------
        None.

        """
        
        # Query the db for the last by def 10 temperature
        recent_temperatures = self.query.order_by(Temperature.date_time.desc()).limit(limit).all()
        
        # Create a list of tuples containing the date-time and temperature values
        temperature_data = [((temperature.date_time.strftime('%d-%m-%Y %H:%M:%S')), temperature.temperature) for temperature in recent_temperatures]
        
        return temperature_data
    
    def get_odd_temperature(self, limit=10, cap=10):
        temperatures = self.get_recent_temperature(limit=cap*limit)
        buffer_temp = 300000
        new_temp = []
        
        for t in temperatures:
            if (t[1] > buffer_temp + 0.3) or (t[1] < buffer_temp - 0.3):
                buffer_temp = t[1]
                new_temp.append(t)
                
        if cap > limit * 1000:
            return new_temp[:limit]
                
        if len(new_temp) <= limit:
            return self.get_odd_temperature(limit=limit, cap=cap*2)
        
        return new_temp[:limit]
                

@app.route("/")
def homepage():
    temperatures = Temperature()
    return render_template("index.html", temperatures=temperatures.get_odd_temperature(limit=100))
    
@app.route("/add_temperature", methods=['POST'])
def add_temperature():
    """
    Add a new temperature measurement to the database from JSON POST.

    The JSON POST data is expected to be a object with the following format:
    {
        "date_time": "ISO-formatted datetime string",
        "temperature": float
    }

    Returns JSON response with "message" key indicating that the temperature was added and with the HTTP status code of 201.
    """
    
    # Create the Temperature table if it does not exist
    db.create_all()
    
    # Extract the date_time and temperature from the POST data
    data = request.get_json()
    date_time = datetime.fromisoformat(data['date_time'])
    temperature=data['temperature']
    
    # Create a new Temperature object and add it to the database
    tmp = Temperature(date_time=date_time, temperature=temperature)
    tmp.commit()
    
    
    
    # Return a response indicating that the temperature was added, with an HTTP status code of 201 Created
    return jsonify(message='Temperature added'), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
