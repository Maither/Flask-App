# -*- coding: utf-8 -*-
"""
Created on Fri Apr  7 12:59:22 2023

@author: yohan.mestre
"""

from datetime import datetime
from flask import Flask, render_template, request, jsonify, request
import sqlite3
import matplotlib.pyplot as plt
import io
import base64 

con = sqlite3.connect("temperature.db")
cur = con.cursor()

print(cur.execute("schema"))


class dateTime_temperature:
    
    def __init__(self):
        temperatures = Temperature()
        temperatures.round_temp()
        temperatures.clean()
        DATA = temperatures.load()
        self.data = DATA
        self.display_data = DATA
        self.len_data = len(DATA)
        self.minmax = self.minmax()
        
        
    def get_temp_and_datetime_array(self):
        """
        return datetime and temperature array
        """
        temperature = []
        date_time = []
        
        for data in self.display_data:
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
    
    def update(self):
        self.__init__()
        
    def reset(self):
        self.display_data = self.data
        
    def get_formate_data(self):
        return [((temperature.date_time.strftime('%d-%m-%Y %H:%M:%S')), temperature.temperature) for temperature in self.display_data]
    
    def set_period(self, minmax):
        self.update()
        min_date = minmax[0][0]
        max_date = minmax[0][1]
        
        min_index = 0
        max_index = 0
        
        for i, data in enumerate(self.data):
            if data.date_time >= min_date:
                min_index = i
                break
            
        for i, data in enumerate(self.data[min_index:]):
            if data.date_time >= max_date:
                max_index = i
                break
            
        self.display_data = self.data[min_index:max_index]
        
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
    

        
    
    def round_temp(self):
        new_data = self.load()
        self.purge()
        
        for data in new_data:
                tmp = Temperature(date_time=data.date_time, temperature=round(data.temperature, 1))
                tmp.commit()
                
    
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
    
    
    
    
     minmax = tmp.minmax()

    min_date = minmax[0][0].strftime('%Y-%m-%dT%H:%M')
    max_date = minmax[0][1].strftime('%Y-%m-%dT%H:%M')
    minmax = ((min_date, max_date),(minmax[1][0], minmax[1][1]))
    
    minmax_date = (request.args['min_date'], request.args['max_date'])
            NdateTime_temperature.set_period((minmax_date,('/')))
            
    temperatures = Temperature()
        temperatures.round_temp()
        temperatures.clean_db()
        DATA = temperatures.db_to_array()
        
        
class DT_temperature :
    def __init__(self):
        temperatures = Temperature()
        temperatures.round_temp()
        temperatures.clean_db()
        DATA = temperatures.db_to_array()
        self.data = DATA
        self.len_data = len(DATA)
        
        
        
    def get_temp_and_datetime_array(self):
        """
        return datetime and temperature array
        """
        temperature = []
        date_time = []
        
        for data in display_data:
            temperature.append(data[1])
            date_time.append(data[0])
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
    
    def update(self):
        temperatures = Temperature()
        temperatures.round_temp()
        temperatures.clean_db()
        DATA = temperatures.db_to_array()
        
        self.data = DATA
        global display_data
        display_data = DATA
        self.len_data = len(DATA)
        
        
    def reset(self):
        global display_data
        display_data = self.data
        
    def get_formate_data(self):
        global display_data
        return [((temperature[0].strftime('%d-%m-%Y %H:%M:%S')), temperature[1]) for temperature in display_data]
    
    def set_period(self, minmax):
        
        self.update()
        global display_data
        
        min_date =  datetime.strptime(minmax[0], '%Y-%m-%dT%H:%M')
        max_date = datetime.strptime(minmax[1], '%Y-%m-%dT%H:%M')
        
        min_index = 0
        max_index = self.len_data
        
        data = self.data
        
        for i, dt in enumerate(data):
            
            if dt[0] >= min_date:
                min_index = i
                break
        
        for i, dt in enumerate(data[min_index:]):
            if dt[0] <= max_date:
                max_index = i + min_index
                break
            
        
        display_data = self.data[min_index:max_index-1]
        return display_data
        
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
    
    
    
        if request.is_json:
        if request.args['button_text'] == 'Set date':
            minmax_date = (request.args['min_date'], request.args['max_date'])
            display_data = dt.set_period(minmax_date)
            
            min_date = request.form['min_date']
            max_date = request.form['max_date']