from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import schedule
from quoters import Quote
import datetime, configparser
import geocoder, json
import time, requests

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
        geo.add_argument("--headless")
        geo.set_preference("geo.enabled", True)
        geo.set_preference('geo.prompt.testing', True)
        geo.set_preference('geo.prompt.testing.allow', True)
        location = 'data:application/json,{"location": {"lat": %s, "lng": %s}, "accuracy": 100.0}'
        location = (location)%(lat,lng)
        geo.set_preference('geo.provider.network.url', location)
        self.driver = webdriver.Firefox(firefox_profile='/app/profile', options=geo)
    
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
               self.notification("normal",\
                                 "Good Morning! Have a good day ahead!", \
                                 quote )
            if entry_type == 'Check-out':
               quote = Quote.print()
               self.notification("normal",\
                                 "Hey there!! it is time to take rest", \
                                 quote )            
            self.driver.get(AutoZohoAttendence.__URL__)
            web_obj = self.driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/div/div[2]/div/button[3]/div/div[3]')
            val = web_obj.text
            _status, _ = val.split("\n")
            if _status == entry_type:  
                web_obj.click()
                self.notification("normal",\
                                  "Today's {} Done".format(entry_type), \
                                  "Thank me later..you have missed your {}! I have done for you".format(entry_type) )  
                time.sleep(10)
            elif (entry_type == 'Check-in') and (_status=='Check-out'):
                self.notification("critical",\
                                  "Attendence not done properly", \
                                  "You have missed your yesterday Check-out! Go and apply for yesterdays regularization")
                web_obj.click()   
                time.sleep(2)
                web_obj.click()
                self.notification("normal",\
                                  "Todays Check-in Done", 
                                  "Thank me later..you have missed your Check-in! I have done for you")
            elif (entry_type == 'Check-out') and (_status=='Check-in'):
                self.notification("critical",\
                                  "Bad status!! for your Attendence", \
                                  "You have missed your attendence go and apply for todays regularization")
                time.sleep(10)
            else:
                self.notification("normal",\
                                  "Good work!!", \
                                  "You have already marked your {}".format(entry_type))
                time.sleep(10)
        except NoSuchElementException:
            self.notification("critical",\
                              "Zoho Attendence Login Failed!",
                              "Session has Expired Need to Login in Zoho Attendence page in you firefox Profile!")
        except Exception as e:
            self.notification("critical", \
                              "Attendence Failed", \
                              "This profile was last used with a newer version of this application. Please create a new Firefox profile")
        finally:
            self.web_driver_quit()
    
    def attendence(self,entry_type):
        if self.driver!= None: self.driver.quit()
        self.open_zoho__attendence_page(entry_type)

az = AutoZohoAttendence()

def job(entry_type):
    if datetime.datetime.today().strftime('%A') not in exclude_day:
        az.attendence(entry_type)

def warm_up(start_time,end_time):
    machine_on_time = datetime.datetime.now().strftime('%H:%M')
    checkin_time    = datetime.strptime(start_time, '%H:%M').time()
    checkout_time   = datetime.strptime(end_time, '%H:%M').time()
    if ( machine_on_time < checkin_time ) and ( machine_on_time < checkout_time ):
        pass
    if ( machine_on_time > checkin_time ) and ( machine_on_time < checkout_time ):
        az.notification(urgency='critical', \
                        title='Late Check-in', \
                        message='Hey there!!....another late entry!!...dont worry let me mark your entry if you have not done yet')
        az.attendence(entry_type='Check-in')
    if ( machine_on_time > checkout_time ):
        az.notification(urgency='critical', \
                        title='Late Check-out', \
                        message='Hey there!!....another late entry!!...dont worry let me mark your entry if you have not done yet')
        az.attendence(entry_type='Check-out')


exclude_day = ['Saturday','Sunday']
start_time  = "10:00"
end_time    = "18:00"

if __name__ == "__main__":
    az.notification(urgency='normal', \
                    title='Automated attendance started! => {}'.format(str(datetime.datetime.now())), \
                    message="Hey there!! daemon automated attendance start! your Check-in and Check-out time is monitoring and mark accordingly!")
    warm_up(start_time,end_time)
    schedule.every().day.at(start_time).do(job,'Check-in')
    schedule.every().day.at(end_time).do(job,'Check-out')
    while True:
        schedule.run_pending()
        time.sleep(1)