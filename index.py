# This program is made possible by Graham Smith and Krushil Amrutiya
# We do not hold any liability if it causes any problems 

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta, date
import todoist

class SchoologyScraper:
    def __init__(self, url: str, username: str, password: str) -> None:
        self.url = url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.login()

    def login(self): 
        """
        Login to schoology.
        This method is run on the creation of a SchoologyScraper object.
        """
        # initial login page           
        res = self.session.get(self.url)
        soup = BeautifulSoup(res.content, "html.parser")
        url = soup.find(id="options").attrs["action"]

        # login in
        res = self.session.post(
            url,
            data={
                "UserName": self.username,
                "Password": self.password,
                "AuthMethod": "FormsAuthentication",
            },
        )
        soup = BeautifulSoup(res.content, "html.parser")
        form = soup.find("form")
        url = form.attrs["action"]
        saml = form.find("input", {"name": "SAMLResponse"}).attrs["value"]
        relayState = form.find("input", {"name": "RelayState"}).attrs["value"]

        # log in again through the redirect
        res = self.session.post(
            url,
            data={"SAMLResponse": saml, "RelayState": relayState},
        )

        return res.url == self.url + "home"

    def get_assignments(self, t_from: int, t_to: int):
        """
        Returns a list of assignments within the given timeframe.
        All time is in seconds from epoch.
        Keyword arguments:
        t_from -- The time that the calendar will start at
        t_to -- The time that the calendar will end at
        """
        res = self.session.get(self.url + "user-calendar")
        res = self.session.get(
            f"{res.url}?ajax=1&start={t_from}&end={t_to}&_=1623553551138"
        )
        data = json.loads(res.content)
        return data


# date component for the program to run on
presentday = datetime.now() 
tomorrow = presentday + timedelta(1) 
today = date.today()
todaysDate = today.strftime("%d.%m.%Y")
tomorrowsDate = tomorrow.strftime("%d.%m.%Y")
todayDate = todaysDate + ' 08:00:00'
tomorrowDate = tomorrowsDate + ' 08:00:00'
pattern = '%d.%m.%Y %H:%M:%S'
epochTodaysDate = int(time.mktime(time.strptime(todayDate, pattern)))
epochTomorrowsDate = int(time.mktime(time.strptime(tomorrowDate, pattern)))

# To get your school's schoology's URL, simple login into schoology and then get that URL remove the /home from the end
# Like https://schoolname.schoology.com/home to https://schoolname.schoology.com/ 

# So, with the username part, it might restrict you from using this program depending on if your school
# uses Microsoft services, if your school does your Microsoft services, then you might be able to use this program
# So for the username, enter your school's URL with 2 backslashes and then your username, 
# like schooldistrict.org\\123456

# For the password part, simple enter your schoology password
scraper = SchoologyScraper("Enter your school's schoology URL", "Enter your schoology username", "Enter your schoology password")
assignments = scraper.get_assignments(epochTodaysDate, epochTomorrowsDate)


# To access your Todoist API key, go to Todoist, then click on your profile and look for the option called Integrations
# Click on the Integrations link, and scroll all the way down and there should be section called API token
# Get the API Token and paste it below! ↧↧↧↧↧
api = todoist.TodoistAPI("Enter your Todoist API Key") #enter your Todoist API Key
api.sync()


for i in range(80): #runs the for loop 80 times
   

    try: #runs for how many assignments the user has
        name = assignments[i]['titleText']

        # Create a new project on Todoist of your choice, for example school work and get the ID of that project!
        # If not sure how to get your project ID, click on your project, and the URL should change above, 
        # For example, https://todoist.com/app/project/4910539201 Take the last 10 digit number and that's your Project ID
        #                                           ↧↧↧↧↧    
        uploadAssignmentToTodoist = api.items.add(name, project_id="Project ID", due={"string": "today"}) #enter your Project Id from Todoist
        api.commit()

    except: #runs after there are no more assignments to get
        print("DONE!")
        break
        

'''
If you want to test if the program works, then simply fire up your preferred terminal and cd into the directory
of this program and type python3 index.py and it the terminal returns DONE between 5 to 15 seconds, then the program 
works!!!

If you want to deploy this program on the cloud to run everyday and do this process automatically, then first add
this program all the files of this program to Github and make sure to save the visibilty as Private, because if you 
leave it as Public, then anyone on Github will be able to see your login credentials as well as your Todoist API 
Credentials. After having it on Github with the Private Visibility set, go to https://www.heroku.com, Heroku is
a neat plateform for hosting your files and executing them from the cloud. After getting logged in, click on 
create on the new button and click create app, after that, simply link your Github with Heroku and choose
the directory from github to deloy, and then click on deploy branch to deploy the files from github, once the 
deployment has been successful, it will say branch deployed, then headover to resources and heroku scheduler, it might
ask you to add payment details to verify that its you, but you won't get charged if you don't exceed the free
tier limit and then head over to heroku scheduler's page and set it up!

Open up a issue ticket if you are confused or need any further assistance with setting up the program!
'''