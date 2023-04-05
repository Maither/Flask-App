from datetime import datetime
from flask import Flask, render_template, request, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import matplotlib.pyplot as plt
import io
import base64 

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
       
    def purge(self):
    # Remove all temperature data points from the database
        self.query.delete()
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
    
    def load(self):
        return self.query.order_by(Temperature.date_time.desc()).all()
    
    def get_odd_temperature(self, limit=10):
        recent_temperatures = self.query.order_by(Temperature.date_time.desc()).all()
        temperatures = [((temperature.date_time.strftime('%d-%m-%Y %H:%M:%S')), temperature.temperature) for temperature in recent_temperatures]
        buffer_temp = 300000
        new_temp = []
        
        for t in temperatures:
            if (t[1] > buffer_temp + 0.3) or (t[1] < buffer_temp - 0.3):
                buffer_temp = t[1]
                new_temp.append(t)
        
        return new_temp[:limit]
    
    def clean(self, mutate=True):
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
        temperature_data = self.load()
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

        
        if mutate:
            # Remove all temperature data points from the database
            self.purge()
            
            for data in new_data:
                tmp = Temperature(date_time=data.date_time, temperature=data.temperature)
                tmp.commit()
                    
            return tmp
        else:
            return new_data
        
    def copy(self):
            temperature_data = Temperature.load(self)
            new_data = []
            for temperature in temperature_data:
                new_data.append(temperature)
            return new_data
    
    def round_temp(self):
        new_data = self.copy()
        self.purge()
        
        for data in new_data:
                tmp = Temperature(date_time=data.date_time, temperature=round(data.temperature, 1))
                tmp.commit()
                
    def get_temp_and_datetime_array(self):
        """
        return datetime and temperature array
        """
        temperature = []
        date_time = []
        new_data = self.copy()
        
        for data in new_data:
            temperature.append(data.temperature)
            date_time.append(data.date_time)
        return date_time, temperature
    
    def minmax(self):
        """
        

        Returns tuple of the tuple minimum and maximum date and temperature ((min date, max date), (min temp, max temp))
        -------
        TYPE
            tuple

        """
        d, t = self.get_temp_and_datetime_array()
        return ((min(d), max(d)), (min(t), max(t)))
    
    def build_from_arr(self, data):
        self.purge()
        
        for i in range(len(data[0])):
            tmp = Temperature(date_time=data[0][i], temperature=data[1][i])
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
            
    def graph_data(self):
        # Create the figure and plot the data
        fig, ax = plt.subplots()
        
        y, x = self.get_temp_and_datetime_array()
        
        ax.plot(y, x)
    
        # Save the figure to a buffer
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
    
        # Embed the image data in the HTML output
        return base64.b64encode(buf.getbuffer()).decode('ascii')
                
        
            
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


@app.route("/", methods=['GET', 'POST'])
def homepage():
    db.create_all()
    temperatures = Temperature()
    minmax = temperatures.minmax()
    min_date = minmax[0][0].strftime('%Y-%m-%dT%H:%M')
    max_date = minmax[0][1].strftime('%Y-%m-%dT%H:%M')
    minmax = ((min_date, max_date),(minmax[1][0], minmax[1][1]))
    
    if request.is_json:
        if request.args['button_text'] == 'Clean':
            temperatures.clean()
        elif request.args['button_text'] == 'Round':
            temperatures.round_temp()
        elif request.args['button_text'] == 'Remove':
            temperatures.remove(temperature=float(request.args['value']))
        
        
    return render_template("index.html", temperatures=temperatures.get_recent_temperature(limit=100), data=temperatures.graph_data(), minmax=minmax)
    
    

@app.route("/clean", methods=['GET', 'POST'])
def clean():
    tmp = Temperature()
    tmp.round_temp()
    tmp.clean()
    
    return render_template("index.html", temperatures=tmp.get_recent_temperature(limit=100))




if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
