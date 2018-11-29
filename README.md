Scrape ss.com category and collect data in Google Spreadsheet.  
Project as part of Python and BeautifulSoup learning process. 
Python files are served as base templates. Feel free to modify/adopt them as needed.

**How it works:**

1. Loads list(s) from ss.com categories. For example https://www.ss.com/lv/real-estate/flats/riga/agenskalns/sell/ 
2. Collects ad detail links from first page and writes these details and other vital information in Google Spreadsheet. 
3. On next run only new ads are added. 

**Requirements**

1. Python env. (tested with 2.7 only)
2. Libraries: requests, BeautifulSoup, sleep, datetime, gspread, ServiceAccountCredentials
3. Google Account and Sheets API enabled and access file.

**To get started**

`pip install -r requirements.txt` This should add all required libraries.

Enable Google Sheets API and generate credentials JSON. You can follow step 1 from this tutorial:  
https://developers.google.com/sheets/api/quickstart/python

Create Google Sheet and share it with e-mail from JSON file ("client_email").

Copy JSON file content in `data/creds.json`. 

Add five column names in top row: `Fetch date`, `URL`, `Price`, `Date`, `Description`. 
Everything else script should be able to add by itself.  

Add categories of interest in `target_list` in python file. Change `google_filename` and `google_sheet_name` accordingly.

Run `python base.py` (tested with real estate) or  `python base_cars.py` (tested with cars).

Check scraping process in Sheet. Add this task to scheduler if needed.

**Important notes**

Template `base.py` is written for real estate. Template `base_cars.py` is for cars. These may work well 
for other categories as well but do not hesitate to modify accordingly if needed.  

Google Sheet API has strict limits on read/write operation (https://developers.google.com/sheets/api/limits). 
That' s why process should be paused on each ad.

This is tested only for Selling ads. Renting, Buying and Exchange ads may not work out of the box. 