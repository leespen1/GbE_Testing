##############################################################################
#
# IPbComFile.py
#
#   Execute IPbus register IO command file
#
# 14-Sep-2018 : V1.0
#
##############################################################################

IPbComFile_version = "V1.0"

###############################################################################
# intialize values for command line parameter
ipb_conf_file_name  = ""    # this argument is required
ipb_exec_file_name  = ""    # this argument is required

wait_on_error       = 0     # default is no wait


# Show command line options
def Show_Usage():
#----------
  print """
Usage: python IPbComFile.py    -r|--reg_addr register_definition_address_file
                               -e|--exec_file register_io_command_file
                              [-w|--wait_on_error seconds_before_2nd_try]

    -r register_definition_address_file
 or --reg_addr register_definition_address_file

      Specify the name of a file defining the set of registers to test.
      The content of this file should add members to the array "vme_addr_arr"
      e.g.:
        vme_addr_arr += ( "0x0070000c",
                          "0x0070000e" )
      This argument is required.

    -e register_io_command_file
 or --exec_file register_io_command_file

      Specify the name of a file defining the set of registers to test.
      The content of this file should add members to the array "vme_addr_arr"
      e.g.:
        vme_addr_arr += ( "0x0070000c",
                          "0x0070000e" )
      This argument is required.

    -w seconds
 or --wait_on_error seconds

      Specify an optional wait period after reading an incorrect value
      before attempting a second chance read.
      This argument is optional and the default is no waiting.


    """
  Done ()
###############################################################################

import sys
import os
from   time     import time
from   time     import localtime
from   time     import asctime
from   time     import sleep

import uhal

from   ipb_access   import idx_ipb_descr

from   ipb_access   import ipb_access_init
from   ipb_access   import ipb_read
from   ipb_access   import ipb_write
from   ipb_access   import ipb_tot_read_count
from   ipb_access   import ipb_tot_write_count

from   UtilException            import  show_exc_info

##################################################################

# general options
wait_on_exit = 0

###############################################################################
# Make exit actions a function so that we can use it for aborting from anywhere
def Done():
#----------

  end_time_flt = time()
  end_time_asc = asctime ( localtime( end_time_flt ) ) [:19]

  print "\nIPbExecFile %s Done at %s "  %  \
                ( IPbComFile_version,
                  end_time_asc )

  print "Elapsed Time %3.1f s"  %  \
                ( end_time_flt - start_time_flt )

  if ( wait_on_exit ) : raw_input ( '<CR>' )
  sys.exit()

###############################################################################
###############################################################################
if __name__ == '__main__':
#-------------------------

  start_time_flt = time()
  start_time_asc = asctime ( localtime( start_time_flt ) ) [:19]
  print "\nIPbExecFile %s Starting at %s "  %  \
                ( IPbComFile_version,
                  start_time_asc )

  #--------------------------------------------------------------------------------
  # read and parse command line arguments
  #--------------------------------------------------------------------------------
  cmd_line_arg = sys.argv[1:]

  if ( len (cmd_line_arg) >= 1 ) :

    # build explicit do loop (instead of "for i in range...") to allow "i=i+1"
    i = 0
    while ( i < len(cmd_line_arg) ) :

      if ( ( cmd_line_arg[i] == "-h" )
        or ( cmd_line_arg[i] == "-?" ) )  :
        Show_Usage ()

      # input file to define register addresses to be tested
      elif ( ( cmd_line_arg[i] == "--reg_addr" )
          or ( cmd_line_arg[i] == "-r" ) )  :
        try :
          i=i+1
          ipb_conf_file_name = cmd_line_arg[i]
        except :
          print ' ** Could not find register address file name on command line ** '
          Show_Usage ()

        # verify that this file exists
        if ( os.path.isfile (ipb_conf_file_name) != True ) :
          print ' ** file does not exist <%s> ** '  %  ipb_conf_file_name
          Show_Usage ()

      # input file to define register addresses to be tested
      elif ( ( cmd_line_arg[i] == "--exec_file" )
          or ( cmd_line_arg[i] == "-e" ) )  :
        try :
          i=i+1
          ipb_exec_file_name = cmd_line_arg[i]
        except :
          print ' ** Could not find register io command file name on command line ** '
          Show_Usage ()

        # verify that this file exists
        if ( os.path.isfile (ipb_exec_file_name) != True ) :
          print ' ** file does not exist <%s> ** '  %  ipb_exec_file_name
          Show_Usage ()

      # delay to wait before doing a second chance read
      elif ( ( cmd_line_arg[i] == "--wait_on_error" )
          or ( cmd_line_arg[i] == "-w" ) )  :
        try :
          i=i+1
          wait_on_error = eval ( cmd_line_arg[i] )
        except :
          print ' ** Could not find wait period on command line ** '
          Show_Usage ()

      else : # catch all other illegal options

        Show_Usage ()

      # switch to next argument
      i=i+1

  # verify that all required parameters were given
  #--------------------------------------------------------------------------------

  # verify that the file defining the set of registers was specified
  if ( ipb_conf_file_name == "" ) :
    print ' ** missing parameter: register address file name ** '
    Show_Usage ()

  # verify that the file defining the set of registers was specified
  if ( ipb_exec_file_name == "" ) :
    print ' ** missing parameter: register io command file name ** '
    Show_Usage ()


  # execute the configuration file
  #--------------------------------------------------------------------------------

  ipb_card_dict = {}

  try:
    execfile ( ipb_conf_file_name )

  except:
    print ' ** failure executing <%s> ** '  %  ipb_conf_file_name
    show_exc_info ( )

  # this is how many registers were defined
  tot_cards = len ( ipb_card_dict )
  print "tot cards = %d" % tot_cards

  # verify that it has filled the array expected
  if ( tot_cards == 0 ) :
    print ' ** <%s> did not fill expected array "ipb_card_dict" ** '  %  ipb_conf_file_name
    Show_Usage ()



  # initialize ipb access
  #------------------------------------------------------

  ipb_access_version, ipb_status = ipb_access_init ( verbose = 1 )

  if ( ipb_status != "Ok" ) :
    Done()

  print "\nUsing ipb_access %s"   %   ipb_access_version


  #--------------------------------------------------------------------------------
  # Ready to go
  #--------------------------------------------------------------------------------

  error_count = 0

  # execute the command file

  try:
    execfile ( ipb_exec_file_name )

  except:
    print ' ** failure executing <%s> ** '  %  ipb_exec_file_name
    show_exc_info ( )




  # Done
  #--------------------------------------------------------------------------------
  print "\n\n Found %d IPbus IO error(s) after %d ipb_read and %d ipb_write" % \
                ( error_count,
                  ipb_tot_read_count(),
                  ipb_tot_write_count() )
  Done()


