#
# Last edited: 18:00  October 18, 2018
#
import sys
from subprocess import PIPE, Popen, call
import tempfile
import json
import time
import OWAMP_classes as master
import os


#Other command line options to consider: host clean-up, schedule clears (with time to clear), mesh to use (with default route), whether or not to change json loaded to include all members 


# Show command line options
def Show_Usage():
#----------
  print """
Usage: python OWAMP_test_v1p1.py [options] -c|--config_file
                                           -p|--packet_padding
                                           -i|--packet_interval
                                           -s|--schedule_clear
                                           -r|--check_routes
                                           -d|--restart_pscheduler_daemons 
                                           -o|--output_filename
Options:

 -h, --help                               Display this message and exit
 -c FILENAME, --config_file     FILENAME  Name of configuration file to read
 -p PADDING,  --packet_padding  PADDING   Size of packets to be sent in bytes, not including packet headers
 -i INTERVAL, --packet_interval INTERVAL  Time interval between sent packets in seconds
 -s, --schedule_clear                     Clear schedules on all hosts before uploading new central mesh 
 -r, --check_routes                       Check whether each host can be reached and pscheduler can be found
                                          Only restart meshconfig for those hosts on which pscheduler can be found
 -d, --restart_pscheduler_daemons         Restart pscheduler runner, archiver, ticker, and scheudler daemons on each host
 --serial_no SERIAL_NUMBER                Serial Number of Hub. Will be used for MadDash display
    """
  return



hosts_list    = ["hubps03",
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
#                 "hubps17",
                 "hubps18"]


#Default Command Line Parameters

clear_schedules = False
check_routes = False
restart_pscheduler_daemons = False
config_filename = ""
output_filename = ""
serial_no = ""
packet_padding = "1450"
packet_interval = "0.1"
version = "v1p4"




# Get command line options
cmd_line_arg = sys.argv[1:]

if ( len (cmd_line_arg) >= 1 ) :

  # build explicit do loop (instead of "for i in range...") to allow "i=i+1"
  i = 0

  #Configuration File; Loop over to set parameters based on config file,
  #Then do another loop to override with command line arguments
  while ( i < len(cmd_line_arg)):

    if ((cmd_line_arg[i] == "-c")
         or (cmd_line_arg[i] == "--config_file")):

      try:
        i += 1
        config_filename = cmd_line_arg[i]
        i += 1
        continue

      except:
        print(" ** Argument for config_file not given; Using defaults ** ")
        config_filename = ""
        i += 1
        continue

    else:
      i += 1

  if config_filename != "":
    try:
      execfile (config_filename)
    except:
      print ("** Failure executing <%s> **"%(config_filename))
      Show_Usage()


  # Begin second loop for non-config-file command line arguments
  i = 0
  while ( i < len(cmd_line_arg) ) :


    #Help
    if ((cmd_line_arg[i] == "-h" )
         or (cmd_line_arg[i] == "--help")):

      Show_Usage()
      sys.exit()

    #Output Filename
    elif ((cmd_line_arg[i] == "-o")
           or (cmd_line_arg[i] == "--output_filename")):

      try:
        i += 1
        output_filename = cmd_line_arg[i]
        i += 1
        continue

      except:
        print(" ** Argument for output_filename not given; Prompting user for log name ** ")
        i += 1
        continue

    #Packet Padding
    elif ((cmd_line_arg[i] == "-p")
           or (cmd_line_arg[i] == "--packet_padding")):

      try:
        i += 1
        packet_padding = cmd_line_arg[i]
        i += 1
        continue

      except:
        print(" ** Argument for packet_padding not given; Using default of 1450 ** ")
        packet_padding = "1450"
        i += 1
        continue

    #Packet Interval
    elif ((cmd_line_arg[i] == "-i")
           or (cmd_line_arg[i] == "--packet_interval")):

      try:
        i += 1
        packet_interval = cmd_line_arg[i]
        i += 1
        continue

      except:
        print(" ** Argument for packet_interval not given; Using default of 0.1 seconds ** ")
        packet_interval = "0.1"
        i += 1
        continue


    #Schedule Clear
    elif ((cmd_line_arg[i] == "-s" )
           or (cmd_line_arg[i] == "--clear_schedules")):

      clear_schedules = True
      i += 1
      continue     

    #Check Routes    
    elif ((cmd_line_arg[i] == "-r")
           or (cmd_line_arg[i] == "--check_routes")):

      check_routes = True
      i += 1
      continue

    #Restart Pscheduler Daemons
    elif ((cmd_line_arg[i] == "-d")
         or (cmd_line_arg[i] == "--restart_pscheduler_daemons")):
        
      restart_pscheduler_daemons = True
      i += 1
      continue

    #Serial Number of Hub
    elif (cmd_line_arg[i] == "--serial_no"):
      
      try:
        i += 1
        serial_no = cmd_line_arg[i]
        i += 1
        continue

      except:
        print(" ** Argument for serial_no  not given; ** ")
        serial_no = ""
        i += 1
        continue

    #Catch config_file arguement
    elif ((cmd_line_arg[i] == "-c")
         or (cmd_line_arg[i] == "--config_file")):

      try:
        i += 1
        config_filename = cmd_line_arg[i]
        i += 1
        continue

      except:
        print(" ** Argument for config_file not given; Using defaults ** ")
        config_filename = ""
        i += 1
        continue


    else:
        print(" ** Illegal arguement '%s' ** "%(cmd_line_arg[i]))
        i += 1
        continue
    


#############
#Get log path (if not already given) and hub serial no
month_day_year = time.strftime("%b %d, %Y", time.localtime())

if output_filename == "":

    output_filename = raw_input("Please input name of output log: ")

if serial_no == "":
  serial_no = raw_input("Please input serial no. of Hub: ")


log_path = "Results/" + output_filename

pscheduler_obj = master.pScheduler_Testing(log_path, hosts_list, serial_no)


log_header = ("##################################################################################\n" +
              "#                 OWAMP Test for %-12s                                    #\n"%(month_day_year) +
              "#                 Serial No. %-12s                                        #\n"%(serial_no) +
              "#                 Version: %-4s                                                  #\n"%(version) +
              "##################################################################################\n\n")



pscheduler_obj.log.write(log_header)

parameter_listing_string =  "Intiating OWAMP test with the following paramters\n"
parameter_listing_string += "  Clear schedules: %s\n"%clear_schedules 
parameter_listing_string += "  Restart pschdeuler daemons on each host: %s\n"%restart_pscheduler_daemons 
parameter_listing_string += "  Check routes: %s\n"%check_routes 
parameter_listing_string += "  Packet Padding: %s\n"%packet_padding 
parameter_listing_string += "  Packet Interval: %s\n"%packet_interval 
parameter_listing_string += "  Hosts: \n"
for host in hosts_list:
  parameter_listing_string += "    %s\n"%host
parameter_listing_string += "\n"


pscheduler_obj.log.write(parameter_listing_string)

pscheduler_obj.log.write("==================================================================================\n")

if check_routes == True:

  try:
    pscheduler_obj.log.flush_no_timestamp()
    pscheduler_obj.log.write("Checking host routes\n")
    pscheduler_obj.log.flush()

    bad_hosts_list = pscheduler_obj.check_routes(update_hosts=True)
    if bad_hosts_list == []:
      pscheduler_obj.log.write("All hosts can be reached and have pscheduler\n\n")
    else:
      pscheduler_obj.log.write("Pscheduler could not be found on the following hosts, removing from test: \n")
      for host in bad_hosts_list:
        pscheduler_obj.log.write("  %s\n"%(host))
      pscheduler_obj.log.write("\n")

  except Exception as e:
    pscheduler_obj.log.write("Exception while checking host routes\n\n")

# Clear current central mesh
try:
    pscheduler_obj.log.flush_no_timestamp()
    pscheduler_obj.log.write("Clearing central mesh\n")
    pscheduler_obj.log.flush()

    pscheduler_obj.clear_central_mesh()
    pscheduler_obj.log.write("Mesh succesfully cleared.\n\n")
except Exception as e:
    pscheduler_obj.log.write("Exception while clearing central mesh.\n\n")


# Restart pscheduler runner, archiver, scheduler, and ticker daemons on all hosts 
if restart_pscheduler_daemons == True:

  try:
    pscheduler_obj.log.flush_no_timestamp()
    pscheduler_obj.log.write("Restarting pscheduler daemons\n")
    pscheduler_obj.log.flush()

    succesfully_restarted_hosts = pscheduler_obj.restart_pscheduler_daemons()

    if len(succesfully_restarted_hosts) == len(pscheduler_obj.hosts):
      pscheduler_obj.log.write("Pscheduler runner, archiver, scheduler, and ticker daemons successfully restarted on all hosts.\n\n")

    else:
      pscheduler_obj.log.write("Pscheduler daemon restart unsuccessful on following hosts: \n")
      for host in pscheduler_obj.hosts:
        if host not in succesfully_restarted_hosts:
          pscheduler_obj.log.write("  %s\n"%(host))
      pscheduler_obj.log.write("\n")

  except Exception as e:
    pscheduler_obj.log.write("Exception while restarting pscheduler daemons\n\n")



# Restart mesh configuration daemon on all hosts so that they do not schedule new tasks based on the old mesh
try:
  pscheduler_obj.log.flush_no_timestamp()
  pscheduler_obj.log.write("Restarting mesh configuration daemons\n")
  pscheduler_obj.log.flush()

  succesfully_restarted_hosts = pscheduler_obj.restart_meshconfig_daemons()

  if len(succesfully_restarted_hosts) == len(pscheduler_obj.hosts):
    pscheduler_obj.log.write("Mesh Configuration daemons successfully restarted on all hosts.\n\n")

  else:
    pscheduler_obj.log.write("Mesh configuration daemon restart unsuccessful on following hosts: \n")
    for host in pscheduler_obj.hosts:
      if host not in succesfully_restarted_hosts:
        pscheduler_obj.log.write("  %s\n"%(host))
    pscheduler_obj.log.write("\n")

except Exception as e:
  pscheduler_obj.log.write("Exception while restarting mesh configuration daemons\n\n")



# Clear schedules on all hosts so that no tests remain from the old mesh
if clear_schedules == True:
  try:
    pscheduler_obj.log.flush_no_timestamp()
    pscheduler_obj.log.write("Clearing schedules\n")
    pscheduler_obj.log.flush()

    succesfully_cleared_hosts = pscheduler_obj.clear_all_schedules()
    if len(succesfully_cleared_hosts) == len(pscheduler_obj.hosts):
      pscheduler_obj.log.write("All schedules succesfully cleared\n")
    else:
      pscheduler_obj.log.write("Not all schedules succesfully cleared\n" +
                               "Hosts with unsuccesfully cleared schedules: \n")
      for host in pscheduler_obj.hosts:
        if host not in succesfully_restarted_hosts:
          pscheduler_obj.log.write("  %s\n"%host)
      pscheduler_obj.log.write("\n\n")

  except Exception as e:
    pscheduler_obj.log.write("Exception while clearing schedules\n\n")



# Create and publish a new mesh
try:
  pscheduler_obj.log.flush_no_timestamp()
  pscheduler_obj.log.write("Creating and publishing mesh\n")
  pscheduler_obj.log.flush()

  mesh_string = pscheduler_obj.create_and_publish_mesh(packet_padding, packet_interval)
  pscheduler_obj.log.write("Mesh succesfully created and published\n\n")
except Exception as e:
  pscheduler_obj.log.write("Exception while creating and publishing mesh\n")
    


# Configure MadDash
try:
  pscheduler_obj.log.flush_no_timestamp()
  pscheduler_obj.log.write("Configuring MadDash\n")
  pscheduler_obj.log.flush()

  pscheduler_obj.configure_maddash()
  pscheduler_obj.log.write("MadDash succesfully configured\n\n")
except Exception as e:
  pscheduler_obj.log.write("Exception while configuring maddash on hosts\n\n")



# Restart mesh configuration daemon on all hosts so that the new mesh is read 
try:
  pscheduler_obj.log.flush_no_timestamp()
  pscheduler_obj.log.write("Restarting mesh configuration daemons\n")
  pscheduler_obj.log.flush()

  pscheduler_obj.restart_meshconfig_daemons()

  if len(succesfully_restarted_hosts) == len(pscheduler_obj.hosts):
    pscheduler_obj.log.write("Mesh Configuration daemons successfully restarted on all hosts.\n\n")

  else:
    pscheduler_obj.log.write("Mesh configuration daemon restart unsuccessful on following hosts: \n")
    for host in pscheduler_obj.hosts:
      if host not in succesfully_restarted_hosts:
        pscheduler_obj.log.write("  %s\n"%(host))
    pscheduler_obj.log.write("\n")
except Exception as e:
  pscheduler_obj.log.write("Exception while restarting mesh configuration daemons\n\n")


try:
  pscheduler_obj.log.write("Mesh Published: \n\n%s\n\n"%(mesh_string))


except Exception as e:
  pscheduler_obj.log.write("Exception while writing published mesh to log\n\n")


pscheduler_obj.log.flush_no_timestamp()
