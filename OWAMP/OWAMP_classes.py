import subprocess
from subprocess import PIPE, Popen, call
import json
import time



class pScheduler_Testing():

    def __init__(self, log_path="", hosts_list = [], serial_no="XX"):
    ######
    # If check_routes is true, removes any hosts that cannot be reached or do not appear
    # to have pscheduler installed from the list of hosts
  
        if hosts_list == []:

            self.hosts = ["hubps03",
                          "hubps04",
                          "hubps05",
                          "hubps06",
                          "hubps07", 
                          "hubps08", 
                          "hubps09", 
                          "hubps10",
                          "hubps11",
                          "hubps12",
                          "hubps13",
                          "hubps14",
                          "hubps15", 
                          "hubps16",
                          "hubps17",
                          "hubps18"]
        else:
            self.hosts = hosts_list

        self.log = Log(log_path)
        self.serial_no = serial_no



    def check_routes(self, update_hosts=False):
    ######
    # Check whether pscheduler can be found on each host in the object's list of hosts.
    # Returns list of hosts which could not be found
      
        good_hosts_list = []
        bad_hosts_list = []
        for host in self.hosts:
            if self.ping(host) == True:
                good_hosts_list.append(host)
            else:
                bad_hosts_list.append(host)

        if update_hosts==True:
           self.hosts = good_hosts_list

        return bad_hosts_list



    def ping (self, host):
    ######
    #Check whether pscheduler can be found on host
    #Return True if it can be, False if not

        subp = Popen("pscheduler ping %s"%(host), shell=True, stdout=PIPE, stderr=PIPE)
        pscheduler_ping_stdout, pscheduler_ping_stderr = subp.communicate()

        if (pscheduler_ping_stderr.find("Connection aborted: No route to host") != -1):
            return False

    
        elif (pscheduler_ping_stdout == "%s: pScheduler is alive\n"%(host)):
            return True

        else:
            return False




    def tasks_scheduled (self, host, duration="+PT1H"):
    ######
    # Returns number of tasks scheduled for a given host during the given duration
        pipe = Popen("pscheduler schedule --host %s %s"%(host, duration),
                                                         shell=True, stdout=PIPE, stderr=PIPE)

        schedule_stdout, schedule_stderr = pipe.communicate()

        if schedule_stderr: 
            return -1
            # In the case of an error, since -1 is not a sensible value for number of tasks

        schedule_list = schedule_stdout.split("\n\n\n")

        # Check if nothing is scheduled
        if "Nothing scheduled" in schedule_stdout:
            return 0

        # There may be schedule entries for tasks that were scheduled to be performed in the
        # future, but were cancelled. This checks whether the schedule consists entirely of
        # cancelled tasks
        else:
            canceled_finished_tasks = 0
            for entry in schedule_list:
                entry_header = ((entry.split("\n"))[0]).strip()
                task_status = (entry_header.split(" "))[-1]
                if ((task_status == "(Canceled)") or (task_status == "(Finished)")
                                                  or (task_status == "(Non-Starter)")):
                    canceled_finished_tasks += 1

            return len(schedule_list) - canceled_finished_tasks




    def clear_schedule_single (self, host, duration="+PT24H"):
    ######
    # Clears scheduled tasks within the duration on the given host         
        pipe = Popen("pscheduler schedule --host %s %s"%(host, duration), shell=True, stdout=PIPE, stderr=PIPE)
        schedule_stdout, schedule_stderr = pipe.communicate()

        # Check if nothing is scheduled
        if "Nothing scheduled" in schedule_stdout:
            return True

        error_canceling_tasks = False

        schedule_list = schedule_stdout.split("\n\n\n")
            
        for entry in schedule_list:

            entry_header = ((entry.split("\n"))[0]).strip()
            task_status = (entry_header.split(" "))[-1]
            if ((task_status != "(Canceled)") and (task_status != "(Finished)")
                                              and (task_status != "(Non-Starter)")):

                run_URL = ((entry.split("\n"))[-1]).strip()
                task_url = run_URL.split("/runs/")[0] #A run URL is just an extension of a task URL. We want to remove the run part
           
                subp = Popen("ssh root@%s 'pscheduler cancel %s'"%(host, task_url), shell=True,
                             stdout=PIPE, stderr=PIPE) #Cancel Task
                cancel_task_stdout, cancel_task_stderr = subp.communicate()
                if cancel_task_stderr:
                    error_canceling_tasks = True

        if self.tasks_scheduled(host,duration) == 0:
          return True
        else:
          return False


    def clear_all_schedules (self, duration="+PT24H"):
    #####
    # Clear schedules on all hosts
        succesfully_cleared_hosts = []        

        for host in self.hosts:
            clear_succesful = self.clear_schedule_single(host, duration=duration)
            if clear_succesful:
              succesfully_cleared_hosts.append(host)

        return succesfully_cleared_hosts


    def clear_central_mesh(self):
    ######
    # Clear central mesh so that hosts do not schedule new tasks
    # Note: use of this function should be followed by use of the
    # restart_meshconfig_daemons function, in order to stop the 
    # scheduling of tasks immediately
        open("/var/www/html/meshconfig/central_mesh.json", 'w').close()
        return



    def restart_pscheduler_daemons_single(self, host):
    ######
    # Restarts pscheduler daemons on a single host
    # pscheduler daemons are: runner, archiver, ticker, and scheduler
    # Returns true if daemons restarted succesfully, false if not  
        subp = Popen(("ssh root@%s 'systemctl restart pscheduler-runner pscheduler-archiver "%(host) +
                          "pscheduler-ticker pscheduler-scheduler'"), shell=True, stdout=PIPE, stderr=PIPE)

        daemon_restart_stdout, daemon_restart_stderr = subp.communicate()

        if daemon_restart_stderr: #if string is not empty. That is, if there was some message in stderr
            return False

        else:
            return True

    def restart_pscheduler_daemons(self):
    ######
    # Restarts pscheduler daemons on all hosts
    # pscheduler daemons are: runner, archiver, ticker, and scheduler
    # Returns list of hosts which succesfully restarted daemons   

        succesfully_restarted_hosts = []

        for host in self.hosts:
            single_restart_succesful = self.restart_pscheduler_daemons_single(host)
            if single_restart_succesful == True:
                succesfully_restarted_hosts.append(host)
            
        return succesfully_restarted_hosts

    def restart_meshconfig_daemons_single(self, host):
    ######
    # Restarts perfsonar-meshconfig-agent on given host, which causes host to update which central
    # meshes it uses to schedule tasks
    # Returns true if meshconfig agents succesfully restarted, false if not
        subp = Popen("ssh root@%s 'systemctl restart perfsonar-meshconfig-agent'"%(host),
                      shell=True, stdout=PIPE, stderr=PIPE)

        daemon_restart_stdout, daemon_restart_stderr = subp.communicate()

        if daemon_restart_stderr: #if string is not empty. That is, if there was some message in stderr
            return False
        else:
            return True
        

    def restart_meshconfig_daemons(self):
    ######
    # Restarts perfsonar-meshconfig-agent on each host, which causes each host to update which central
    # meshes they are using to schedule tasks
    # Returns true if meshconfig agents succesfully restarted, false if not

        succesfully_restarted_hosts = []

        for host in self.hosts:
            single_restart_succesful = self.restart_meshconfig_daemons_single(host)
            if single_restart_succesful == True:
                succesfully_restarted_hosts.append(host)

        return succesfully_restarted_hosts


    def create_and_publish_mesh(self, packet_padding='1450', packet_interval='0.1', 
                                mesh_path = '/var/www/html/meshconfig/central_mesh.json'):
    ######
    # Create a mesh JSON file specifying an OWAMP test between all hosts (bidirectional) with the
    # specified packet padding and time interval between sending packets, and publishes the file 
    # in the given location 

      #Convert arguments to strings, in case user did not do so
      packet_interval = str(packet_interval)
      packet_padding  = str(packet_padding)

      mesh_dict = {
                    "organizations" : [
                      {
                        "sites" : [
                          {
                            "hosts" : [
                              {
                                "addresses" : ["hubpsma"],
                                "description" : "PSMA"
                              }  
                            ],
                            "measurement_archives" : [
                              {
                                "read_url" : "https://hubpsma/esmond/perfsonar/archive/",
                                "write_url" : "https://hubpsma/esmond/perfsonar/archive/",
                                "type" : "perfsonarbuoy/owamp"
                              },                      
                            ]
                          }
                        ],
                        "description" : "Hub Testing"
                      }
                    ],
  
                    "tests" : [
                      {
                        "members" : { 
                          "type" : "mesh",
                          "members" : []
                        },
                        "parameters" : {
                          "loss_threshold" : "60",
                          "bucket_width" : "0.0001",
                          "sample_count" : "6000",
                          "packet_interval" : packet_interval,
                          "force_bidirectional" : "1",
                          "packet_padding" : packet_padding,
                          "type" : "perfsonarbuoy/owamp",
                          "session_count" : "6000"
                        },
                        "description" : "OWAMP Testing"
                      }
                    ],
                    "description" : "HUBSN%s Mesh"%(self.serial_no)
                  }

      for host in self.hosts:
        for org in mesh_dict["organizations"]:
          for site in org["sites"]:
            site["hosts"].append(
                                  {
                                    "addresses" : [host],
                                    "description" : host[-4:].upper()
                                  }
                                )
   
        for test in mesh_dict["tests"]:
          test["members"]["members"].append(host)

      mesh_json_string = json.dumps(mesh_dict, indent = 3, separators = (',', ': '))
      central_mesh_file = open(mesh_path, 'w')
      central_mesh_file.write(mesh_json_string)

      return mesh_json_string
    

    ######
    # The following three functions are for taking an existing mesh, modifying to include all hosts of the current
    # object in the testing, and then publishing the mesh. They have been replaced in the OWAMP script with the above
    # function, which creates a mesh from scratch and publishes it. 
    def convert_central_mesh_config_to_json(self, config_file_directory = "MadDash_Config/script_mesh.conf",
                                                  output_directory = "MadDash_Config/script_mesh.json"):
    ######
    # Converts a central mesh configuration file into a JSON file, which can be read by a meshconfig agent

        call("/usr/lib/perfsonar/bin/build_json %s -o %s"%(config_file_directory, output_directory), shell=True)
        return

    def modify_central_mesh_template(self, template_location = "MadDash_Config/script_mesh.json", ):
    ######
    # Given a central mesh JSON file, returns a modified version so that all tests in the file occur between all hosts

        #Open central mesh template
        mesh_template_json = open(template_location, 'r').read()  #What would I do to close the file in this case?
        #Convert from JSON to python dictionary
        mesh_dict = json.loads(mesh_template_json)


        #Set each test to include all members in the list of hosts. 
        for test_dict in mesh_dict["tests"]:
            test_dict["members"]["members"] = self.hosts
        #Convert from dictionary back to JSON, with readable formatting
        central_mesh_json_string = json.dumps(mesh_dict, indent = 3, separators = (',', ': '))

        modified_mesh_file = open(template_location, 'w')
        modified_mesh_file.write(central_mesh_json_string)
        modified_mesh_file.close()
         
        return

    
    def publish_central_mesh(self, central_mesh_directory="MadDash_Config/script_mesh.json"):
    ######
    # Writes contents of a specified central mesh JSON file to a public location, to be read by hosts    

        central_mesh_json_string = open(central_mesh_directory, 'r').read()
        mesh_final = open('/var/www/html/meshconfig/central_mesh.json', 'w') #Real location
        mesh_final.write(central_mesh_json_string)
        mesh_final.close()
 
        return
    

    def configure_maddash(self):
    ######
    # Performs necessary steps to configure maddash

        ######
        #Prepare guiagent configurations. One that checks mesh for changes and updates maddash.yaml file, and one that does not.
        #(Could just have an empty file for the inactive configuration, but we might as well have a file that shows what the active
        #configuration will be)
        gui_agent_active_str = open('MadDash_Config/meshconfig-guiagent-active.conf', 'r').read()
        gui_agent_inactive_str = open('MadDash_Config/meshconfig-guiagent-inactive.conf', 'r').read()

        ######
        #Get maddash.yaml template
        maddash_template = open('MadDash_Config/maddash_template.yaml', 'r').read()

        ######
        #Write inactive configuration so we can write template to maddash.yaml without it being overwritten by the guiagent
        meshconfig_guiagent = open('/etc/perfsonar/meshconfig-guiagent.conf', 'w')
        meshconfig_guiagent.write(gui_agent_inactive_str)
        meshconfig_guiagent.close()
        #Write Template
        maddash_yaml = open('/etc/maddash/maddash-server/maddash.yaml', 'w')
        maddash_yaml.write(maddash_template)
        maddash_yaml.close()

        ######
        #Write active configuration and restart guiagent to update maddash.yaml
        meshconfig_guiagent = open('/etc/perfsonar/meshconfig-guiagent.conf', 'w')
        meshconfig_guiagent.write(gui_agent_active_str)
        meshconfig_guiagent.close()
        call("systemctl restart perfsonar-meshconfig-guiagent.service", shell=True)

        ######
        #Write inactive configuration so we can edit maddash.yaml to display graphs without being overwritten by guiagent
        meshconfig_guiagent = open('/etc/perfsonar/meshconfig-guiagent.conf', 'w')

        meshconfig_guiagent.write(gui_agent_inactive_str)
        meshconfig_guiagent.close()

        ######
        #Edit maddash.yaml so that graphs are displayed properly
        time.sleep(10) #There is a delay between when the guiagent is restarted and maddash.yaml is updated, so we wait before editing
        call("sed -i 's@/perfsonar-graphs@https://hubpsma.pa.msu.edu/perfsonar-graphs@g' /etc/maddash/maddash-server/maddash.yaml", shell=True)

        call("systemctl restart maddash-server", shell=True)

        return
                
    


class Log:

    def __init__(self, log_name):

        self.log_name = log_name
        self.write_buffer = ""

    def write(self, entry):

        self.write_buffer += entry


    def clear_write_buffer(self):

        self.write_buffer = ""        


    def flush(self, print_log=True):

        if self.write_buffer == "":
            return

        time_str = time.asctime()
        write_buffer_split = self.write_buffer.split("\n")
        write_str = ""
        i = 0
        while i < len(write_buffer_split):

            if i == 0:
                write_str += "[" + time_str + "] "
            elif (i == len(write_buffer_split) - 1) and write_buffer_split[i] == "":
                i += 1
                continue
            else:
                write_str += " "*(len(time_str) + 3)


            write_str += write_buffer_split[i] + "\n"
            i += 1

        if self.log_name:
            log = open(self.log_name, "a+")
            log.write(write_str)
            log.close()

        if print_log == True:
            print(write_str)

        self.clear_write_buffer()

    def flush_no_timestamp(self, print_log=True):

        if self.write_buffer == "":
            return

        if self.log_name:
            log = open(self.log_name, "a+")
            log.write(self.write_buffer)
            log.close()

        if print_log == True:
            print(self.write_buffer)

        self.clear_write_buffer()





