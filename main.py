import requests
from dateutil import parser
from dateutil.relativedelta import relativedelta
from datetime import datetime, date
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

# Page the has a list of all the nuclear reactors in the United States.
list_of_reactors = "https://www.nrc.gov/reactors/operating/list-power-reactor-units.html"
# Get the page
page = requests.get(list_of_reactors)
# Open in BS4
soup = BeautifulSoup(page.content, "html.parser")
table = soup.find("table")

ages = []
today = date.today()

def processReactorTableData(table):
    print("Processing table data...")
    rows = table.findAll("tr")
    reactors = []
    for row in rows:
        reactor_data = pullReactorData(row)
        reactors.append(reactor_data)
    
def pullReactorData(row):        
    print("Pulling reactor data...")
    reactor_link = row.find('a', href=True)
    if(reactor_link != None):
        reactor_page = requests.get('https://www.nrc.gov' + reactor_link['href'])
        reactor_page = BeautifulSoup(reactor_page.content, "html.parser")
        reactor_license_issued = reactor_page.find(lambda tag: tag.name == 'strong' and 'Operating License:' in tag.text)
        reactor_license_renewal = reactor_page.find(lambda tag: tag.name == 'strong' and 'Renewed License:' in tag.text)
        reactor_license_expires = reactor_page.find(lambda tag: tag.name == 'strong' and 'License Expires:' in tag.text)
        reactor_data = { "link": f"https://www.nrc.gov{reactor_link['href']}" }
        
        if(reactor_license_issued != None):
            temp = reactor_license_issued.next_sibling
            try:
                temp = parser.parse(temp.split(',')[0], fuzzy=True)
                ages.append(relativedelta(today, temp).years)
                reactor_data['issued'] = temp.strftime('%m/%d/%Y')
            except:
                reactor_data['issued'] = None 

        if(reactor_license_renewal != None):
            temp = reactor_license_renewal.next_sibling
            try:
                reactor_data['renewal'] = parser.parse(temp.split(',')[0], fuzzy=True).strftime('%m/%d/%Y')
            except:
                reactor_data['renewal'] = None

        if(reactor_license_expires != None):
            temp = reactor_license_expires.next_sibling
            try:
                reactor_data['expires'] = parser.parse(temp.split(',')[0], fuzzy=True).strftime('%m/%d/%Y')
            except:
                reactor_data['expires'] = None

        return reactor_data
    else:
        return None

def generateChart():
    fig, chart = plt.subplots(1,1)
    chart.hist(ages, len(ages))
    chart.set_title("Nuclear Reactor Ages Histogram")
    chart.set_xlabel("Age (years)")
    chart.set_ylabel("Power Plants")
    plt.show()


if(table != None):
    processReactorTableData(table)
    generateChart()    
else: 
    print("error finding table")
