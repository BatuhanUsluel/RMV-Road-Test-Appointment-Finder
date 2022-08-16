
# RMV-Road-Test-Appointment-Finder
Searches/finds road test appointments for the massachusets rmv and notifies user when a appointment becomes available

## Instructions to setup:
  Log into https://atlas-myrmv.massdot.state.ma.us/myrmv/_/  
  Open developer tools (Can right click anywhere on page and click inspect)  
  **tap-session:**  
  Go under application  
  Go under cookies and atlas-myrmv.massdot.state.ma.us  
  Copy the tap-session value. Paste that into config.ini  
  **FAST_CLIENT_WINDOW:**  
  Go under network  
  Go under any request (may have to click a button on the page to get a new request)  
  Go under payload and copy the FAST_CLIENT_WINDOW__ value into config.ini  
  **Config User Options:**  
  before_date - only search/notify for appointments that are before this date  
  locations_wanted - list of locations that you want to be searching  
  wait_between_search_minute = number of minutes to wait in-between every search.  
  **Requirements:**  
  Go into the RMV-Road-Test-Appointment-Finder folder.    
  Run: `pip install -r requirements.txt`  
## Running:  
Run the scraper.py file.  `python scraper.py`  
Needs python 3.  
  
  
