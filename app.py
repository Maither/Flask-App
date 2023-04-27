from datetime import datetime
from flask import Flask, render_template, request, jsonify, request, redirect
from flask_sqlalchemy import SQLAlchemy
import matplotlib.pyplot as plt
import io
import base64 
import json


app = Flask(__name__)

# Set the URI for the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///temperature.db'

# Initialize SQLAlchemy
db = SQLAlchemy(app)

class Temperatures(db.Model):
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

    def purge(self):
        """
        rm all data from db
        """
        self.query.delete()
        db.session.commit()
        db.session.close()
        
    def get_data(self, minmax_date = False):
        """
        

        Returns all data order by date
        -------
        TYPE
            adress

        """
        if not minmax_date:
            return self.query.order_by(Temperatures.date_time.desc()).all()
        else:
            #min_date = datetime.strptime(minmax_date[0], '%Y-%m-%dT%H:%M')
            #max_date = datetime.strptime(minmax_date[1], '%Y-%m-%dT%H:%M')
            
            min_date, max_date = minmax_date
                        
            return self.query.filter(Temperatures.date_time >= min_date, Temperatures.date_time <= max_date).order_by(Temperatures.date_time.desc())
            
    
    def db_to_array(self):
        '''
        

        Returns array of tuple dateTime and temperature float
        -------
        data : TYPE
            DESCRIPTION.

        '''
        datas = self.get_data()
        
        data = []
        
        for dt in datas:
            data.append((dt.date_time, dt.temperature))
            
        return data
    
    def get_recent_temperature(self, limit=10, minmax_date = False):
        """ 
        Parameters
        ----------
        limit : TYPE, int
            DESCRIPTION. The default is 10.

        Returns list of tuple (date_time, temperature)
        -------
        None.

        """
        
        if minmax_date == False:
            # Query the db for the last by def 10 temperature
            recent_temperatures = self.query.order_by(Temperatures.date_time.desc()).limit(limit).all()
        else:
            print(minmax_date)
            #min_date = datetime.strptime(minmax_date[0], '%Y-%m-%dT%H:%M')
            #max_date = datetime.strptime(minmax_date[1], '%Y-%m-%dT%H:%M')
            
            min_date, max_date = minmax_date
            recent_temperatures = self.query.filter(Temperatures.date_time >= min_date, Temperatures.date_time <= max_date).order_by(Temperatures.date_time.desc()).limit(limit).all()
        # Create a list of tuples containing the date-time and temperature values
        temperature_data = [((temperature.date_time.strftime('%d-%m-%Y %H:%M:%S')), temperature.temperature) for temperature in recent_temperatures]
        
        return temperature_data
    
    def clean_db(self):
        """ 
        Parameters
        ----------
        compress : TYPE, bool
            DESCRIPTION. The default is False.

        if False
        Remove temperature data points with no variation.
        if True !!! not implemented yet !!!
        Remove temperature data points with variation bellow 0.3
        -------
        None.

        """
        temperature_data = self.get_data()
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
            
    def round_temp(self):
        new_data = self.get_data()
        self.purge()
        
        for data in new_data:
                tmp = Temperatures(date_time=data.date_time, temperature=round(data.temperature, 1))
                tmp.commit()
            
    def get_temp_and_datetime_array(self, minmax_date = False):
        """
        return datetime and temperature array
        """
        if not minmax_date :
            datas = self.get_data()
            
        else:
            datas = self.get_data(minmax_date)

        temperature = []
        date_time = []
        
        for data in datas:
            temperature.append(data.temperature)
            date_time.append(data.date_time)
        return date_time, temperature        
       
    def graph_data(self, minmax_date = False):
        # Create the figure and plot the data
        
        if not minmax_date :
            y, x = self.get_temp_and_datetime_array()
        else:
            y, x = self.get_temp_and_datetime_array(minmax_date)
            
        fig, ax = plt.subplots()
        
        ax.plot(y, x)
    
        # Save the figure to a buffer
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
    
        # Embed the image data in the HTML output
        return base64.b64encode(buf.getbuffer()).decode('ascii')
    
    def build_from_arr(self, data):
        self.purge()
        
        for i in range(len(data[0])):
            tmp = Temperatures(date_time=data[0][i], temperature=data[1][i])
            tmp.commit()

    def remove(self, temperature=False, date_time=False):
        #remove data from db
        if temperature :
            d, t = self.get_temp_and_datetime_array()
            if temperature in t:
                for i in range(len(t)):
                    if t[i] == temperature:
                        d.pop(i)
                        t.pop(i)
                        break
        data = (d, t)
        self.build_from_arr(data)
        
    def minmax(self, minmax = False):
        """
        

        Returns tuple of the tuple minimum and maximum date and temperature ((min date, max date), (min temp, max temp))
        -------
        TYPE
            tuple

        """
        
        if not minmax:
            d, t = self.get_temp_and_datetime_array()
        else:
            d, t = self.get_temp_and_datetime_array(minmax)
        
        if len(d) and len(t):
            return ((min(d), max(d)), (min(t), max(t)))
        else:
            return ((datetime(2000, 1, 1), datetime(2000, 1, 1)),(0, 0))
        
    def set_period(self, minmax_date):
        return 0

                
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
    temperature=round(data['temperature'], 1)
    
    # Create a new Temperature object and add it to the database
    tmp = Temperatures(date_time=date_time, temperature=temperature)
    tmp.commit()
    
    # Return a response indicating that the temperature was added, with an HTTP status code of 201 Created
    return jsonify(message='Temperature added'), 201

def display_code(txt):
    content = ""
    with open(txt, "r") as file:
        content = file.read()

    return render_template('layout.html', content=content)

@app.route("/application")
def application():
    return display_code(txt = "app.py")

@app.route("/styles")
def styles():
    return display_code(txt = "static/styles.css")

@app.route("/", methods=['GET', 'POST'])
def homepage():
   
    db.create_all() 
     
    dt = Temperatures()
    dt.clean_db()
    minmax = dt.minmax()
    min_date = minmax[0][0].strftime('%Y-%m-%dT%H:%M')
    max_date = minmax[0][1].strftime('%Y-%m-%dT%H:%M')
    minmax = ((min_date, max_date),(minmax[1][0], minmax[1][1]))
    
    if request.method == "POST":
        
        
        request_data = request.get_json()
        
        if request_data['button_text'] == 'Set date':
        
            min_date = request_data['min_date']
            max_date = request_data['max_date']
            
            min_date = datetime.strptime(min_date, '%Y-%m-%dT%H:%M')
            max_date = datetime.strptime(max_date, '%Y-%m-%dT%H:%M')
            minmax_date = (min_date, max_date)
            
            minmax = dt.minmax(minmax_date)
            temperatures=dt.get_recent_temperature(minmax_date = minmax_date, limit = 100)
            data=dt.graph_data(minmax_date = minmax_date)
            
            return jsonify({'minmax': minmax, 'temperatures':temperatures, 'data':data})
            
    else:            
        #prin = dt.set_period(minmax[0])
        
        return render_template("index.html", temperatures=dt.get_recent_temperature(), data=dt.graph_data(), minmax=minmax)
   
    #return jsonify({'success': True})
    




if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
