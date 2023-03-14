import requests
from dateutil import parser
from datetime import datetime
from bs4 import BeautifulSoup

# Page the has a list of all the nuclear reactors in the United States.
list_of_reactors = "https://www.nrc.gov/reactors/operating/list-power-reactor-units.html"
# Get the page
page = requests.get(list_of_reactors)
# Open in BS4
soup = BeautifulSoup(page.content, "html.parser")
table = soup.find("table")

def processReactorTableData(table):
    print("Processing table data...")
    rows = table.findAll("tr")
    reactors = []
    for row in rows:
        reactor_data = pullReactorData(row)
        print(reactor_data)
        reactors.append(reactor_data)
    for reactor in reactors:
        print("processing issued, renewal, and expirary...")
        if(reactor != None and "issued" in reactor):
            try:
                print(f"Issued: {reactor.issued}")
            except:
                continue       
        if(reactor != None and "renewal" in reactor):
            try:
                print(f"Renewal: {reactor.renewal}")
            except:
                continue
        if(reactor != None and "expires" in reactor):
            try:
                print(f"Expires: {reactor.expires}")
            except:
                continue 

def pullReactorData(row):
    print("Pulling reactor data...")
    reactor_link = row.find('a', href=True)
    if(reactor_link != None):
        reactor_page = requests.get('https://www.nrc.gov' + reactor_link['href'])
        reactor_page = BeautifulSoup(reactor_page.content, "html.parser")
        reactor_license_issued = reactor_page.find(
                lambda tag: tag.name == 'strong' and 'Operating License:' in tag.text
            )
        reactor_license_renewal = reactor_page.find(
                lambda tag: tag.name == 'strong' and 'Renewed License:' in tag.text
            )
        reactor_license_expires = reactor_page.find(
                lambda tag: tag.name == 'strong' and 'License Expires:' in tag.text
            )
        reactor_data = { "link": f"https://www.nrc.gov{reactor_link['href']}" }
        
        if(reactor_license_issued != None):
            temp_str = reactor_license_issued.next_sibling
            try:
                temp = parser.parse(temp_str.split(',')[0], fuzzy=True).strftime('%m/%d/%Y')

            except:
                temp = "error"
            reactor_data['issued'] = temp
        if(reactor_license_renewal != None):
            temp_str = reactor_license_renewal.next_sibling
            try:
                temp = parser.parse(temp_str.split(',')[0], fuzzy=True).strftime('%m/%d/%Y')

            except:
                temp = "error"
            reactor_data['renewal'] = temp
        if(reactor_license_expires != None):
            temp_str = reactor_license_expires.next_sibling
            try:
                temp = parser.parse(temp_str.split(',')[0], fuzzy=True).strftime('%m/%d/%Y')
            except:
                temp = "error"
            reactor_data['expires'] = temp
        return reactor_data
    else:
        return None

        
if(table != None):
    processReactorTableData(table)
else: 
    print("error finding table")
