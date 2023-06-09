from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Set the URI for the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///temperature.db'

# Initialize SQLAlchemy
db = SQLAlchemy(app)

class Temperatures(db.Model):
    """
    Represents a temperature measurement with an associated datetime.
    """

    # Define the columns of the Temperature table
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, nullable=False)
    temperature = db.Column(db.Float, nullable=False)

    
    def commit(self):
       """
       Save the current Temperature object to the database.
       """
       db.session.add(self)
       db.session.commit()
       db.session.close()

    def purge(self):
        """
        Delete all rows from the database.
        """
        self.query.delete()
        db.session.commit()
        db.session.close()
        
    def get_all_temperatures(self, minmax_date = False):
        """
        Retrieve all temperature measurements, optionally filtered by date range.
        """
        if not minmax_date:
            return self.query.order_by(Temperatures.date_time.desc()).all()
        else:          
            min_date, max_date = minmax_date
                        
            return self.query.filter(Temperatures.date_time >= min_date, Temperatures.date_time <= max_date).order_by(Temperatures.date_time.desc())
    
    def get_recent_temperatures(self, limit=10, minmax_date = False):
        """ 
        Retrieve recent temperature measurements, optionally filtered by date range and limited by count.

        """
        
        if limit:
            if minmax_date == False:
                # Query the db for the last by def 10 temperature
                recent_temperatures = self.query.order_by(Temperatures.date_time.desc()).limit(limit).all()
                
            else:         
                min_date, max_date = minmax_date
                recent_temperatures = self.query.filter(Temperatures.date_time >= min_date, Temperatures.date_time <= max_date).order_by(Temperatures.date_time.desc()).limit(limit).all()
        else:
            if minmax_date == False:
                # Query the db for the last by def 10 temperature
                recent_temperatures = self.query.order_by(Temperatures.date_time.desc()).all()
            else:         
                min_date, max_date = minmax_date
                recent_temperatures = self.query.filter(Temperatures.date_time >= min_date, Temperatures.date_time <= max_date).order_by(Temperatures.date_time.desc()).all()
            
        # Create a list of tuples containing the date-time and temperature values
        temperature_data = [((temperature.date_time.strftime('%d-%m-%Y %H:%M:%S')), temperature.temperature) for temperature in recent_temperatures]
        
        return temperature_data
    
    def clean_db(self):
        """
        Remove redundant temperature measurements from the database.
        """
        
        temperature_data = self.get_all_temperatures()
        temperature_data = temperature_data.copy()
        new_data = []
        last_temperature = None
        
        for i, temperature in enumerate(temperature_data):
            if last_temperature is None :
                    new_data.append(temperature)
                    last_temperature = temperature
            if (last_temperature.temperature != temperature.temperature):
                    if temperature_data[i - 1].date_time != temperature_data[i - 2].date_time:
                        new_data.append(temperature_data[i - 1])
                    new_data.append(temperature)
                    last_temperature = temperature

        
        self.purge()
        
        for data in new_data:
            tmp = Temperatures(date_time=data.date_time, temperature=data.temperature)
            tmp.commit()
            
    def db_to_array(self, minmax_date = False):
        """
        Retrieve temperature measurements as arrays of datetimes and temperatures, optionally filtered by date range.
        """
        if not minmax_date :
            temperatures = self.get_all_temperatures()
            
        else:
            temperatures = self.get_all_temperatures(minmax_date)

        temperature = []
        date_time = []
        
        for data in temperatures:
            temperature.append(data.temperature)
            date_time.append(data.date_time)
        return date_time, temperature
    
    def build_from_arr(self, data):
        """
        Rebuild the database from an array of datetime and temperature pairs.
        """
        #data = data.copy()
        
        self.purge()
        
        for i in range(len(data[0])):
            tmp = Temperatures(date_time=data[0][i], temperature=data[1][i])
            tmp.commit()

    def remove(self, temperature=False, date_time=False):
        """
        Remove a temperature measurement from the database, specified by temperature.
        """
        if temperature :
            d, t = self.db_to_array()
            if temperature in t:
                for i in range(len(t)):
                    if t[i] == temperature:
                        d.pop(i)
                        t.pop(i)
                        break
        data = (d, t)
        self.build_from_arr(data)
        
    def minmax(self, minmax_date = False):
        """
        Calculate the minimum, maximum, and average temperatures, optionally filtered by date range.

        """
        
        if not minmax_date:
            d, t = self.db_to_array()
        else:
            d, t = self.db_to_array(minmax_date)
        
        if len(d) and len(t):
            return ((min(d), max(d)), (min(t), max(t), round(sum(t)/len(t),1)))
        else:
            return ((datetime(2000, 1, 1), datetime(2000, 1, 1)),(0, 0, 0))

                
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
    temperature = round(data['temperature'], 1)
    
    # Create a new Temperature object and add it to the database
    tmp = Temperatures(date_time=date_time, temperature=temperature)
    tmp.commit()
    
    # Return a response indicating that the temperature was added, with an HTTP status code of 201 Created
    return jsonify(message='Temperature added'), 201

def display_code(txt):
    content = ""
    with open(txt, "r") as file:
        content = file.read()

    return render_template('displayCode.html', content=content, pageName=txt)

@app.route("/application")
def application():
    return display_code(txt = "app.py")

@app.route("/styles")
def styles():
    return display_code(txt = "static/styles.css")

@app.route("/raspberry")
def styles():
    return display_code(txt = "raspberry.py")

@app.route("/", methods=['GET', 'POST'])
def homepage():
   
    db.create_all() 
     
    dt = Temperatures()
    
    #dt.remove(temperature=5.0)
    
    if request.method == "POST":               
        request_data = request.get_json()

        
        if request_data['button_text'] == 'Set date':        
            min_date = request_data['min_date']
            max_date = request_data['max_date']
            
            min_date = datetime.strptime(min_date, '%Y-%m-%dT%H:%M')
            max_date = datetime.strptime(max_date, '%Y-%m-%dT%H:%M')
            minmax_date = (min_date, max_date)
            
            minmax = dt.minmax(minmax_date)
            temperatures=dt.get_recent_temperatures(minmax_date = minmax_date, limit=False)
            data=dt.db_to_array(minmax_date = minmax_date)
            
            return jsonify({'minmax': minmax, 'temperatures':temperatures, 'data':data})
        
            
    else: 
        minmax = dt.minmax()
        min_date = minmax[0][0].strftime('%Y-%m-%dT%H:%M')
        max_date = minmax[0][1].strftime('%Y-%m-%dT%H:%M')
        minmax = ((min_date, max_date),(minmax[1][0], minmax[1][1], minmax[1][2]))           
        #prin = dt.set_period(minmax[0])
        
        return render_template("index.html", temperatures=dt.get_recent_temperatures(limit=False), data=dt.db_to_array(), minmax=minmax)
 
    
 #Thx https://www.pexels.com/photo/photograph-of-a-burning-fire-672636/ for the photo
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
