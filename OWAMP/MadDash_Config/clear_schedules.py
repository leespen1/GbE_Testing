import subprocess


#####Hosts whose schedules we want cleared
list_of_hosts = ["hubps05", "hubps06", "hubps07", "hubps08",
"hubps09", "hubps10", "hubps11", "hubps12", "hubps13", "hubps14", "hubps15", "hubps16", "hubps17",
"hubps18", "hubps19", "hubps20"]

#list_of_hosts = ["hubps05", "hubps06"]

#Clear central mesh
#open("/var/www/html/meshconfig/central_mesh.json", 'w').close()

######
#Restart meshconfig agents on all hosts (including this machine) to clear schedules
subprocess.call("systemctl restart perfsonar-meshconfig-agent.service", shell=True)
for host in list_of_hosts:
    subprocess.call("ssh root@{0} 'systemctl restart perfsonar-meshconfig-agent.service'".format(host), shell=True)

for host in list_of_hosts:  #Get schedule for next 24 hours
    pipe = subprocess.Popen("pscheduler schedule --host {0} +PT24H".format(host), shell=True, stdout=subprocess.PIPE).stdout
    schedule_string = pipe.read()
    schedule_lines = schedule_string.split('\n')

    for line in schedule_lines:
        if "https" in line: #Check if line contains a run URL
            task_url = line.split("/runs/")[0] #A run URL is just an extension of a task URL. We want to remove the run part
            subprocess.call("ssh root@{0} 'pscheduler cancel {1}'".format(host, task_url), shell=True) #Cancel Task



