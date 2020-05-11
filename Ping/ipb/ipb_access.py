##############################################################################
#
# ipb_access.py
#
#   IPbus Register access
#
# 16-Aug-2018 : V1.0 first stable version handling single node level
# 16-Aug-2018 : V2.0 add multi node level
# 16-Aug-2018 : V2.1 rename debug option to verbose
#
##############################################################################

ipb_access_version = "V2.1"

##################################################################

import uhal

##################################################################

idx_ipb_card    = 0
idx_ipb_node_1  = 1
idx_ipb_node_2  = 2
idx_ipb_descr   = 3

ipb_read_count  = 0
ipb_write_count = 0

ipb_verbose     = 0

##################################################################
def ipb_access_init ( verbose = 0 ) :

  global ipb_read_count
  global ipb_write_count
  global ipb_verbose

  ipb_read_count  = 0
  ipb_write_count = 0

  ipb_verbose     = verbose

  return ipb_access_version, "Ok"


##################################################################

def   ipb_read    ( ipb_card_dict,
                    ipb_reg_entry,
                    verbose = ipb_verbose ) :

  # needs to be declared because we modify it
  global ipb_read_count

  ipb_read_count += 1

  card_hw = ipb_card_dict [ ipb_reg_entry[ idx_ipb_card ] ]

  if ( ipb_reg_entry[ idx_ipb_node_2 ] == "" ) :
    data_read = card_hw.getNode ( ipb_reg_entry[ idx_ipb_node_1 ] ).read()
  else :
    data_read = card_hw.getNode ( ipb_reg_entry[ idx_ipb_node_1 ] ).getNode( ipb_reg_entry[ idx_ipb_node_2 ] ).read()

  card_hw.dispatch()

  # data read is already in hex but we pad to fixed length with zeroes after the leading "0x"
  data_hex = "0x%s"  %  hex(data_read)[2:].rjust( 8, '0' )

  if verbose or ipb_verbose :
    print "ipb_read#%d: read %s = %s"  % \
              ( ipb_read_count,
                ipb_reg_entry[ idx_ipb_descr ],
                data_hex )


  return data_hex

##################################################################

def   ipb_write   ( ipb_card_dict,
                    ipb_reg_entry,
                    data_hex,
                    verbose = ipb_verbose ) :

  # needs to be declared because we modify it
  global ipb_write_count

  ipb_write_count += 1

  if ( data_hex[:2] != "0x" ) :
    print "ipb_write#%d: incorrect data parameter <%s> does not start with 0x"  %  \
              ( ipb_write_count,
                data_hex )
  if ( len(data_hex) != 10 ) :
    print "ipb_write#%d: incorrect data parameter <%s> expected 8 digits after 0x"  %  \
              ( ipb_write_count,
                data_hex )

  card_hw = ipb_card_dict [ ipb_reg_entry[ idx_ipb_card ] ]

  data_write = eval( data_hex )

  if ( ipb_reg_entry[ idx_ipb_node_2 ] == "" ) :
    card_hw.getNode( ipb_reg_entry[ idx_ipb_node_1 ] ).write( data_write )
  else :
    card_hw.getNode( ipb_reg_entry[ idx_ipb_node_1 ] ).getNode( ipb_reg_entry[ idx_ipb_node_2 ] ).write( data_write )

  card_hw.dispatch()

  if verbose or ipb_verbose :
    print "ipb_write#%d: write %s = %s"  % \
              ( ipb_write_count,
                ipb_reg_entry[ idx_ipb_descr ],
                data_hex )

  return


##################################################################

def ipb_tot_read_count ( ) :

 return ipb_read_count

def ipb_tot_write_count ( ) :

 return ipb_write_count
