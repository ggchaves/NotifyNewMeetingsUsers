"""
Copyright (c) 2019 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

import requests
import sys
import time
import xml.etree.ElementTree as ET
from webexteamssdk import WebexTeamsAPI



# this scripts expects to receive a WebexID, password and sitename for the admin account for the site where it will check for new users to send notifications
if ( (len(sys.argv) == 6) and (sys.argv[1]=="INIT" or sys.argv[1]=="CHECK") ) :
    REQACTION=sys.argv[1]
    WEBEXID = sys.argv[2]
    WIDPASSWORD= sys.argv[3]
    SITENAME =sys.argv[4]
    WEBEX_TEAMS_ACCESS_TOKEN=sys.argv[5]
else:
    print("NotifyNewMeetingsUsers Arguments: <INIT|CHECK> admin_userid admin_password site_name access_token")
    exit()


WELCOME_MESSAGE = u"Welcome to Webex Meetings!  \ud83d\ude0e Your administrator has provided you with the ability to host meetings in webex and configure your personal meeting room. Please follow these [instructions](https://collaborationhelp.cisco.com/article/en-us/nul0wut) to get started."

# print("===== webexID:",WEBEXID)
# print("===== sitename:",SITENAME)
# print("===== pwd:",WIDPASSWORD)
# print("===== token:",WEBEX_TEAMS_ACCESS_TOKEN)


previousUsers=[]
activatedUsers=[]
newUsers=[]

#print("======================> List of users for "+SITENAME+": ")
#script to check existing meetings users in site and send any new ones a welcome message via Webex Teams
# right now it can only list all users who have activated their account after receiving the email from the admin. 

url = "https://"+SITENAME+".webex.com/WBXService/XMLService"

#TODO re-introduce variables in assigning payload, for some reason stopped working
payload = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<serv:message xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">\n  <header>\n    <securityContext>\n      <webExID>"+WEBEXID+"</webExID>\n      <password>"+WIDPASSWORD+"</password>\n      <siteName>"+SITENAME+"</siteName>\n    </securityContext>\n  </header>\n  <body>\n        <bodyContent\n            xsi:type=\"java:com.webex.service.binding.user.LstsummaryUser\">\n            <listControl>\n                <serv:startFrom>1</serv:startFrom>\n                <serv:maximumNum>300</serv:maximumNum>\n                <serv:listMethod>AND</serv:listMethod>\n            </listControl>\n            <order>\n                <orderBy>UID</orderBy>\n                <orderAD>ASC</orderAD>\n            </order>\n            <dataScope>\n                <regDateStart>06/23/2004 01:00:00</regDateStart>\n                <regDateEnd>06/23/2020 10:00:00</regDateEnd>\n            </dataScope>\n        </bodyContent>\n  </body>\n</serv:message>"

headers = {
    'cache-control': "no-cache",
    'Postman-Token': "967b5f98-4dbd-48f3-9b4e-6ed820989c12"
    }

def retrieveUsers(): 
    global activatedUsers
    # retrieve list of USERS
    response = requests.request("POST", url, data=payload, headers=headers)
    #print("======returned XML: ",response.text)
    root = ET.fromstring(response.text)
    #print("======root: ",root)
    #define namespaces to extract information from XML data returned
    ns = {'use': 'http://www.webex.com/schemas/2002/06/service/user', 
        'serv': 'http://www.webex.com/schemas/2002/06/service'}
    body=root.find('serv:body',ns)
    #print("======body: ",body)
    bodycontent=body.find('serv:bodyContent',ns)
    #print("======bodycontent: ",bodycontent)
    #iterate through all users in the body of the XML response
    for user in bodycontent.findall('use:user',ns):
        email = user.find('use:email',ns)
        status = user.find('use:active',ns)
        print(email.text,"  ",status.text)
        if status.text=='ACTIVATED':
            activatedUsers.append(email.text)
    print("Current active users: ",activatedUsers)

# if just requesting init file, just retrieve users and generate it
if REQACTION=="INIT":
    print("Just initalizing...")
    #retrieve users 
    retrieveUsers()
    #just create and save them into the file
    usersfile=open("webexusers.txt", 'w')
    for item in activatedUsers:
            usersfile.write("%s\n" % item)
    usersfile.close()
elif REQACTION=="CHECK":
    #read file with old list of active users into a variable, if there
    try:
        usersfile=open("webexusers.txt", 'r') 
        previousUsers = [line.strip() for line in usersfile]
        usersfile.close()
    except FileNotFoundError:
        previousUsers=[]
    #retrieve current users from the site 
    retrieveUsers()
    #figure out the delta between old and new list
    newUsers=list(set(activatedUsers).difference(previousUsers))
    print("======= New users:",newUsers)

    #send message via Teams to all new users using a bot credential
    if newUsers!=[]:
        # Create a WebexTeamsAPI connection object; uses your WEBEX_TEAMS_ACCESS_TOKEN
        api = WebexTeamsAPI(access_token=WEBEX_TEAMS_ACCESS_TOKEN)
        for newUser in newUsers:
            # Send a message to new users
            message = api.messages.create(toPersonEmail=newUser, markdown=WELCOME_MESSAGE)
            # Print the message details (formatted JSON)
            print(message)

    #save new list of active users back into file
    usersfile=open("webexusers.txt", 'w')
    for item in activatedUsers:
            usersfile.write("%s\n" % item)
    usersfile.close()