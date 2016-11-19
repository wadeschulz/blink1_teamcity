import untangle
import requests
from requests.auth import HTTPBasicAuth
import os

##############
# start config
##############

# blink1-tool path
blink = "/home/pi/blink1/commandline/blink1-tool "

# path to store last build status at
hist_path = "/home/pi"

# TeamCity base URL
tc_base = "http://TC_URL:8111"

# TeamCity credentials if projects are not publicly accessible
user = "TC_USERNAME"
password = "TC_PASSWORD"

############
# end config
############

build_config_url = tc_base + "/httpAuth/app/rest/buildTypes"
building_url = tc_base + "/httpAuth/app/rest/builds/?locator=running:true"
builds_url = tc_base + "/httpAuth/app/rest/buildQueue"
current_url = tc_base + "/httpAuth/app/rest/builds/?locator=running:false,count:1&buildType:(id:"

color = "green"
builds = 0
failed = 0
building = 0
project_ids = []

lastcmd = ""
with open(hist_path + '/lastblink.conf', 'r+') as lastblink:
  lastcmd = lastblink.readline().rstrip("\n")

try:
  build_config_xml = requests.get(build_config_url, auth=HTTPBasicAuth(user,password)).text
  build_configs = untangle.parse(build_config_xml).buildTypes.buildType
  for buildType in build_configs:
    project_ids.append(buildType["id"])

  building_xml = requests.get(building_url, auth=HTTPBasicAuth(user,password)).text
  building = int(untangle.parse(building_xml).builds["count"])

  builds_xml = requests.get(builds_url, auth=HTTPBasicAuth(user,password)).text
  builds = int(untangle.parse(builds_xml).builds["count"])

  for id in project_ids:
    project_url = current_url + "id)"
    current_xml = requests.get(project_url, auth=HTTPBasicAuth(user,password)).text
    current = untangle.parse(current_xml).builds.build["status"]
    if current == "FAILURE" or current == "ERROR":
      failed = failed + 1

  if builds > 0:
    color = "magenta"

  if failed > 0:
    color = "red"

  if building > 0:
    color = "blue"

  if building > 0 and failed > 0:
    color = "yellow"

  cmd = blink + "-q --" + color
  if cmd != lastcmd:
    os.system(cmd + " --blink 10")
    with open(hist_path + '/lastblink.conf', 'w') as lastblink:
      lastblink.write(cmd)

  os.system(cmd)
except:
  os.system(blink + "--off -q")
  exit()
