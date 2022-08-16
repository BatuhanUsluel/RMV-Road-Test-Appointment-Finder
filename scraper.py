import requests
import time
import json
import datetime
from bs4 import BeautifulSoup
import configparser
import traceback
from notifypy import Notify

location_dict = {'Braintree': 1073741824,'Brockton': 1272971264,'Chicopee': 1173356544,'Dorchester': 636485632,'Easthampton': 1323827200,'Fall River': 736100352,'Greenfield': 1610612736,'Haverhill': 268435456,'Lawrence': 786956288,'Leominster': 1198784512,'Lowell': 1123549184,'Lynn': 1342177280,'Marthas Vineyard': 1222901760,'Milford': 1860698112,'Nantucket': 1809842176,'New Bedford': 1710227456,'North Adams': 518520832,'Pittsfield': 467664896,'Plymouth': 1541406720,'South Yarmouth': 368050176,'Southbridge': 1004535808,'Springfield': 586678272,'Taunton': 1660420096,'Watertown': 1441792000,'Westfield': 686030848,'Wilmington': 1592262656,'Worcester': 2078277632}

def main():
  config = configOptions()
  s = createSession(config)
  headers = createHeaders()
  while True:
    print(f'Looking for appointments. Time: {datetime.datetime.now().time()}')
    refreshOptions(config, s, headers)
    found_appointments = []
    for location_name in config.locations_wanted:
      checkAppointmentsForLocation(location_name, config, found_appointments, s, headers)
    notifyAndPrintAppointments(found_appointments)
    time.sleep(config.wait_between_search_minute * 60)

class configOptions():
    def __init__(self):
        Config = configparser.ConfigParser()
        Config.read("config.ini")
        self.before_date = datetime.datetime.strptime(Config.get('User_Options', 'before_date'), '%m/%d/%Y')
        self.locations_wanted = [x.strip() for x in Config.get('User_Options', 'locations_wanted').split(',')]
        self.wait_between_search_minute = Config.getint('User_Options', 'wait_between_search_minute')
        self.FAST_VERLAST = "" #Config.get('Request_Options', 'FAST_VERLAST')
        self.FAST_VERLAST_SOURCE = ""# Config.get('Request_Options', 'FAST_VERLAST_SOURCE')
        self.FAST_CLIENT_AJAX_ID = 0 #Config.getint('Request_Options', 'FAST_CLIENT_AJAX_ID')
        self.tap_session = Config.get('Request_Options', 'tap_session')
        self.FAST_CLIENT_WINDOW = Config.get('Request_Options', 'FAST_CLIENT_WINDOW')
        
class foundAppointment():
  def __init__(self, location, date):
    self.location = location
    self.date = date
  def __str__(self):
    return "Location: {0}, Date: {1}".format(self.location, self.date)

def checkAppointmentsForLocation(location_name, config, found_appointments, s, headers):
  print("Checking: " + location_name)
  data = createRequestData(location_dict[location_name], config)
  response = s.post('https://atlas-myrmv.massdot.state.ma.us/myrmv/_/Recalc', headers=headers, data=data)
  try:
    config.FAST_CLIENT_AJAX_ID += 1
    config.FAST_VERLAST = response.headers['Fast-Ver-Last']
    config.FAST_VERLAST_SOURCE = response.headers['Fast-Ver-Source']
    y = json.loads(response.content)
  except Exception:
    print(f'Error while parsing response. Most likely due to incorrect session values')
    print(traceback.format_exc())
    print(f'Response Headers: {response.headers}')
    print(f'Response Content: {response.content}')
    return
    
  for values in y['Updates']['FieldUpdates']:
    if values['field']=="Dc_1-q":
      month = values["value"]
    if values['field']=="Dc_1-01":
      html = values["value"]
      parsed_html = BeautifulSoup(html,  "html.parser")
      green_elements = parsed_html.find_all('td', attrs={'style':'color:#000000; background-color:#CBFFCC; '})
      green_numbers = [green.get_text() for green in green_elements]
      for green_number in green_numbers:
        green_date = datetime.datetime.strptime(str(green_number) + " " + month, '%d %B %Y')
        if green_date <= config.before_date:
          found_appointments.append(foundAppointment(location_name, green_date))
  
def notifyAndPrintAppointments(found_appointments):
  if len(found_appointments) != 0:
    notification = Notify()
    notification.title = "Found RMV road test appointment"
    notification.message = str(len(found_appointments)) + " days found that have appointments. More info in console output"
    notification.send()
  for appointment in found_appointments:
    print(appointment)

def createHeaders():
  return {
    'Connection': 'keep-alive',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'sec-ch-ua-platform': '"Windows"',
    'Origin': 'https://atlas-myrmv.massdot.state.ma.us',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://atlas-myrmv.massdot.state.ma.us/myrmv/_/',
    'Accept-Language': 'en-US,en;q=0.9',
}

def createSession(config):
    s = requests.session()
    s.cookies.set("tap-session", config.tap_session, domain="atlas-myrmv.massdot.state.ma.us", path="/myrmv/")
    return s

def createRequestData(location_id, config):
  return {
  'Dc_1-9': location_id,
  'Dc_1-31': '',
  'Dc_1-51': '',
  'Dc_1-71': '',
  'LASTFOCUSFIELD__': 'Dc_1-9',
  'DOC_MODAL_ID__': '0',
  'FAST_SCRIPT_VER__': '1',
  'FAST_VERLAST__': config.FAST_VERLAST,
  'FAST_VERLAST_SOURCE__': config.FAST_VERLAST_SOURCE,
  'FAST_CLIENT_WHEN__': time.time() * 1000,
  'FAST_CLIENT_WINDOW__': config.FAST_CLIENT_WINDOW,
  'FAST_CLIENT_AJAX_ID__': config.FAST_CLIENT_AJAX_ID,
  'FAST_CLIENT_TRIGGER__': 'Events.Field.selectchange',
  'FAST_CLIENT_SOURCE_ID__': 'Dc_1-9'
    }

def refreshOptions(config, s, headers):
  data = createRequestData(location_dict["Braintree"], config)
  response = s.post('https://atlas-myrmv.massdot.state.ma.us/myrmv/_/Recalc', headers=headers, data=data)
  try:
    config.FAST_CLIENT_AJAX_ID += 1
    config.FAST_VERLAST = response.headers['Fast-Ver-Last']
    config.FAST_VERLAST_SOURCE = response.headers['Fast-Ver-Source']
  except Exception:
    print(f'Error while parsing response. Most likely due to incorrect session values')
    print(traceback.format_exc())
    print(f'Response Headers: {response.headers}')
    print(f'Response Content: {response.content}')
    return

if __name__ == '__main__':
    main()