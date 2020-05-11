import sys


###################################################################
###################################################################
# this variable will be set when an exception is caught in this handler
exception_occured = 0 

def show_exc_info ( logfile = None, stop_on_except = 0   ) :
#----------------------------
  
    exception_occured   = 1 

    exception_info      = sys.exc_info() # retrieve exception info

    exception_type      = exception_info[0]             # exception type
    exception_value     = exception_info[1]             # exception value
    exception_at_line   = exception_info[2].tb_lineno   # traceback item

    print ' *** exception_type    :', exception_type
    print ' *** exception_value   :', exception_value
    print ' *** exception_at_line :', exception_at_line

    if ( logfile != None ):
      logfile.flush ( )
      logfile.write ( ' *** exception_type    :' + str(exception_type)    + '\n' )
      logfile.flush ( )
      logfile.write ( ' *** exception_value   :' + str(exception_value)   + '\n' )
      logfile.flush ( )
      logfile.write ( ' *** exception_at_line :' + str(exception_at_line) + '\n' )
      logfile.flush ( )

    # del statement is executed left to right
    # We need to drop reference to traceback
    # This must be done explicitely (as below) when directly inside except clause
    # but it would be done implictely when returning from a function like here
    del [ exception_at_line,
          exception_value,
          exception_type,
          exception_info ]
          
    if stop_on_except : raise  # stop and get a trace
