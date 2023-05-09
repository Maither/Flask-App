import glob
from datetime import datetime
import time
import requests

# Define the Temperature model
class Temperature:
    def __init__(self, date_time, temperature):
        self.date_time = date_time
        self.temperature = temperature
        
    def post(self, url='http://mether.fr/add_temperature'):

        while True:
            data = {'date_time': self.date_time.isoformat(), 'temperature': self.temperature}
            while True:
                try:
                    response = requests.post(url, json=data)
                    break
                except :
                    time.sleep(1)
            if response.status_code == 201:
                print('Temperature posted successfully')
                break
            else:
                print(response.status_code, 'Error posting temperature')
                time.sleep(1)
                


def main():
    while True:
        temperature = get_temperature()
        
        if temperature == False:
            time.sleep(1)
        else:
            post_temperature(temperature)
            time.sleep(599)
	
	
def get_temperature(route="/sys/bus/w1/devices/28*/w1_slave"):
    """
    return a float if expected beavior else false
    """
    #get a list of file route more than one element if more than one sensor
    route_capteurs=glob.glob(route)
    #if there is a file else return false
    if len(route_capteurs) > 0:
        with open(route_capteurs[0]) as f:
            file = f.read()
            try:
                return float(file[file.rfind("=") + 1:])/1000
            except ValueError:
                return False
    return False


def post_temperature(temperature):
    now = datetime.now()

    tmp = Temperature(date_time=now, temperature=temperature)
    #tmp.commit()
    #url='http://127.0.0.1:5000/add_temperature' for testing
    #tmp.post(url='http://127.0.0.1:5000/add_temperature')
    while True:
        time.sleep(1)
        try:
            tmp.post()
            break
        except:
            pass
    


if __name__ == "__main__":
    main()
