from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.orm import declarative_base
import sqlalchemy
import glob
from datetime import datetime
import time
import requests

engine = sqlalchemy.create_engine('sqlite:///temperature.db')
Base = declarative_base()
Session = sqlalchemy.orm.sessionmaker(bind=engine)

# Define the Temperature model
class Temperature(Base):
    __tablename__ = 'temperature'
    
    id = Column(Integer, primary_key=True)
    date_time = Column(DateTime, nullable=False)
    temperature = Column(Float, nullable=False)
    
    
    def commit(self):
        session = Session()
        session.add(self)
        session.commit()
        session.close()
        
    def post(self, url='http://mether.fr/add_temperature'):
        session = Session()
        session.add(self)
        while True:
            data = {'date_time': self.date_time.isoformat(), 'temperature': self.temperature}
            while True:
                try:
                    response = requests.post(url, json=data)
                    break
                except :
                    time.sleep(2)
            if response.status_code == 201:
                print('Temperature posted successfully')
                session.close()
                break
            else:
                print(response.status_code, 'Error posting temperature')
                time.sleep(1)
                


def main():
    Base.metadata.create_all(engine)
    
    while True:
        temperature = get_temperature()
        if temperature:
            now = datetime.now()
            print(now, temperature)
            
            tmp = Temperature(date_time=now, temperature=temperature)
            tmp.commit()
            #url='http://127.0.0.1:5000/add_temperature' for testing
            tmp.post(url='http://127.0.0.1:5000/add_temperature')
            
            time.sleep(0)
        else:
             time.sleep(1)
	
	
def get_temperature(route="/sys/bus/w1/devices/28*/w1_slave"):
    """
    return a float if expected beavior else false
    """
    return 56.0
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


if __name__ == "__main__":
    main()
