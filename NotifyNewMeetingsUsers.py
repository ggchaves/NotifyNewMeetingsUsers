import requests
import sys
import xml.etree.ElementTree as ET
from webexteamssdk import WebexTeamsAPI

# this scripts expects to receive a WebexID, password and sitename for the admin account for the site where it will check for new users to send notifications
if len(sys.argv) == 4:
    WEBEXID = sys.argv[1]
    WIDPASSWORD= sys.argv[2]
    SITENAME =sys.argv[3]
    TEAMSBOTTOKEN=sys.argv[4]
else:
    WEBEXID = "admin@sample.webex.com"
    WIDPASSWORD= "password"
    SITENAME ="sample-site"
    TEAMSBOTTOKEN="webexteamsbotoken"

print("===== webexID:",WEBEXID)
print("===== sitename:",SITENAME)
print("===== teamsbottoken:",TEAMSBOTTOKEN)


previousUsers=[]
activatedUsers=[]
newUsers=[]

#TODO: read file with old list of active users into a variable
try:
    usersfile=open("webexusers.txt", 'r') 
    previousUsers = [line.strip() for line in usersfile]
    usersfile.close()
except FileNotFoundError:
    previousUsers=[]

print("======================> List of users for "+SITENAME+": ")
#script to check existing meetings users in site and send any new ones a welcome message via Webex Teams
# right now it can only list all users who have activated their account after receiving the email from the admin. 

url = "https://gchaves-sandbox.webex.com/WBXService/XMLService"

#TODO re-introduce variables in assigning payload, for some reason stopped working
#payload = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<serv:message xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">\n  <header>\n    <securityContext>\n      <webExID>"+WEBEXID+"</webExID>\n      <password>"+WIDPASSWORD+"</password>\n      <siteName>"+SITENAME+"</siteName>\n    </securityContext>\n  </header>\n  <body>\n        <bodyContent\n            xsi:type=\"java:com.webex.service.binding.user.LstsummaryUser\">\n            <listControl>\n                <serv:startFrom>1</serv:startFrom>\n                <serv:maximumNum>50</serv:maximumNum>\n                <serv:listMethod>AND</serv:listMethod>\n            </listControl>\n            <order>\n                <orderBy>UID</orderBy>\n                <orderAD>ASC</orderAD>\n            </order>\n            <dataScope>\n                <regDateStart>06/23/2004 01:00:00</regDateStart>\n                <regDateEnd>06/23/2020 10:00:00</regDateEnd>\n            </dataScope>\n        </bodyContent>\n  </body>\n</serv:message>"
payload = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<serv:message xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">\n  <header>\n    <securityContext>\n      <webExID>admin@gchaves.webexsandbox.co</webExID>\n      <password>LaArenaM0vediza!</password>\n      <siteName>gchaves-sandbox</siteName>\n    </securityContext>\n  </header>\n  <body>\n        <bodyContent\n            xsi:type=\"java:com.webex.service.binding.user.LstsummaryUser\">\n            <listControl>\n                <serv:startFrom>1</serv:startFrom>\n                <serv:maximumNum>10</serv:maximumNum>\n                <serv:listMethod>AND</serv:listMethod>\n            </listControl>\n            <order>\n                <orderBy>UID</orderBy>\n                <orderAD>ASC</orderAD>\n            </order>\n            <dataScope>\n                <regDateStart>06/23/2004 01:00:00</regDateStart>\n                <regDateEnd>06/23/2020 10:00:00</regDateEnd>\n            </dataScope>\n        </bodyContent>\n  </body>\n</serv:message>"

headers = {
    'cache-control': "no-cache",
    'Postman-Token': "967b5f98-4dbd-48f3-9b4e-6ed820989c12"
    }



response = requests.request("POST", url, data=payload, headers=headers)
print("======returned XML: ",response.text)

root = ET.fromstring(response.text)
print("======root: ",root)

#define namespaces to extract information from XML data returned
ns = {'use': 'http://www.webex.com/schemas/2002/06/service/user', 
      'serv': 'http://www.webex.com/schemas/2002/06/service'}

body=root.find('serv:body',ns)
print("======body: ",body)

bodycontent=body.find('serv:bodyContent',ns)
print("======bodycontent: ",bodycontent)

#iterate through all users in the body of the XML response
for user in bodycontent.findall('use:user',ns):
    email = user.find('use:email',ns)
    status = user.find('use:active',ns)
    print(email.text,"  ",status.text)
    if status.text=='ACTIVATED':
        activatedUsers.append(email.text)

print("Current active users: ",activatedUsers)

#TODO figure out the delta between old and new list
newUsers=list(set(activatedUsers).difference(previousUsers))
print("======= New users:",newUsers)

#TODO send message via Teams to all new users using a bot credential

#TODO save new list of active users back into file
usersfile=open("webexusers.txt", 'w')
for item in activatedUsers:
        usersfile.write("%s\n" % item)
usersfile.close()