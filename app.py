from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import schedule
import datetime
import geocoder
import time

exclude_day = ['Saturday','Sunday']
start_time  = "10:00"
end_time    = "18:00"

organization_name = 'XYZ'
 
class AutoZohoAttendence:

    __URL__     = 'https://peopleplus.zoho.in/{}/zp#attendance/entry/listview'.format(organization_name)
    __PROFILE__ = '/app/profile' # firefox profile

    def __init__(self):
        self.driver  = None
        self.waiting = 20 

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
            print(str(datetime.datetime.now()),": Invoke time at")
            self.driver.get(AutoZohoAttendence.__URL__)
            web_obj = self.driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/div/div[2]/div/button[3]/div/div[3]')
            val = web_obj.text
            _status, _time = val.split("\n")
            print('entry_type:', entry_type, 'init:', _status, _time)
            time.sleep(10)
            web_obj.click()
            self.web_driver_quit()
            self.web_driver_load()
            self.driver.get(AutoZohoAttendence.__URL__)
            web_obj = self.driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/div/div[2]/div/button[3]/div/div[3]')
            val = web_obj.text
            _status, _time = val.split("\n")
            print('entry_type:', entry_type, 'after:', _status, _time)
        except NoSuchElementException:
            print("Session Expire Need to Login in Profile")
    
    def attendence(self,entry_type):
        self.web_driver_load()
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