import OWAMP_classes as master
import time


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


pscheduler_obj = master.pScheduler_Testing(hosts_list=hosts_list)


# Clear current central mesh    
try:
    pscheduler_obj.log.write("Clearing central mesh\n")
    pscheduler_obj.log.flush()
    pscheduler_obj.clear_central_mesh()
except:
    pscheduler_obj.log.write("Error while clearing central mesh.\n")
pscheduler_obj.log.flush()


# Restart mesh configuration daemon on all hosts so that they do not schedule new tasks based on the old mesh
try:
  pscheduler_obj.log.write("Restarting mesh configuration daemons\n")
  pscheduler_obj.log.flush()
  succesfully_restarted_hosts = pscheduler_obj.restart_meshconfig_daemons()

  if len(succesfully_restarted_hosts) == len(pscheduler_obj.hosts):
    pscheduler_obj.log.write("Mesh Configuration daemons successfully restarted on all hosts.\n")

  else:
    pscheduler_obj.log.write("Mesh configuration daemon restart unsuccessful on following hosts: \n")
    for host in pscheduler_obj.hosts:
      if host not in succesfully_restarted_hosts:
        pscheduler_obj.log.write("  %s\n"%(host))
    pscheduler_obj.log.write("\n")

except:
  pscheduler_obj.log.write("Error while restarting mesh configuration daemons\n")
pscheduler_obj.log.flush()


# Clear schedules on all hosts so that no tests remain from the old mesh
#try:
if True:
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
                pscheduler_obj.log_write("  %s\n"%host)
        pscheduler_obj.log.write("\n")

pscheduler_obj.log.flush()

#except:
#    pscheduler_obj.log.write("Error while clearing schedules\n")



