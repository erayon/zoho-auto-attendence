from urllib.parse import parse_qs
from requests.api import head
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import schedule
from quoters import Quote
import datetime, configparser
import geocoder, json
import time, requests

exclude_day = ['Saturday','Sunday']
start_time  = "10:00"
end_time    = "18:00"

organization = 'xyz'

class Base:

    __FILE__ = 'config.ini'

    def __init__(self):
        self.cfg = self.setup_config(Base.__FILE__)

    def setup_config(self, config_filename):
        configParser   = configparser.RawConfigParser()   
        configParser.read(config_filename)
        return configParser

class AutoZohoAttendence(Base):

    __URL__     = 'https://peopleplus.zoho.in/{}/zp#attendance/entry/listview'.format(organization)
    __PROFILE__ = '/app/profile'

    def __init__(self):
        Base.__init__(self)
        self.driver  = None
        self.waiting = 20 
        self.__notification_url__ = self.cfg['flask_notification_systemd']['ip']
    
    def notification(self,urgency,title,message):
        payload = {
            "urgency":urgency,
            "title":title,
            "message":message
        }
        payload = json.dumps(payload)
        headers = {'Content-Type': 'application/json'}
        response = requests.request("POST", self.__notification_url__, headers=headers, data=payload)
        print(response)

    def web_driver_load(self):
        lat, lng = self.get_latlng()
        geo = webdriver.FirefoxOptions()
        geo.headless = True
        geo.set_preference("geo.enabled", True)
        geo.set_preference('geo.prompt.testing', True)
        geo.set_preference('geo.prompt.testing.allow', True)
        location = 'data:application/json,{"location": {"lat": %s, "lng": %s}, "accuracy": 100.0}'
        location = (location)%(lat,lng)
        geo.set_preference('geo.provider.network.url', location)
        self.driver = webdriver.Firefox(AutoZohoAttendence.__PROFILE__, options=geo)
    
    def web_driver_quit(self):
        self.driver.quit()

    def get_latlng(self):
        g = geocoder.ip('me')
        val = g.latlng
        lat, lng = val[0], val[1]
        return lat, lng

    def open_zoho__attendence_page(self,entry_type):
        try:
            self.web_driver_load()
            if entry_type == 'Check-in':
                quote = Quote.print()
                self.notification("normal","Good Morning! Have a good day ahead", quote )            
            self.driver.get(AutoZohoAttendence.__URL__)
            web_obj = self.driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/div/div[2]/div/button[3]/div/div[3]')
            val = web_obj.text
            _status, _ = val.split("\n")
            if _status == entry_type:
                self.notification("normal","Attendence {} Done".format(entry_type), "You have missed your {} attendence! I have done for you".format(entry_type) )    
                web_obj.click()
                time.sleep(10)
                self.web_driver_quit()
            else:
                self.notification("normal","Good work!! for your Attendence", "You have already marked your {}".format(entry_type))
                time.sleep(10)
        except NoSuchElementException:
            self.notification("critical","Login Failed!"," Session has Expired Need to Login in Zoho Attendence page in firefox Profile! ")
        except Exception as e:
            self.notification("critical","Attendence Failed",e)
    
    def attendence(self,entry_type):
        self.open_zoho__attendence_page(entry_type)

az = AutoZohoAttendence()

def job(entry_type):
    if datetime.datetime.today().strftime('%A') not in exclude_day:
        az.attendence(entry_type)
    
if __name__ == "__main__":
    print("Working......................................................", str(datetime.datetime.now()))
    schedule.every().day.at(start_time).do(job,'Check-in')
    schedule.every().day.at(end_time).do(job,'Check-out')
    while True:
        schedule.run_pending()
        time.sleep(1)