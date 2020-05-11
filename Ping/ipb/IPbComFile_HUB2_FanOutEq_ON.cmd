

print " HUB2 address 0x00000000 = control     RW reg"
read_value_control_hex = ipb_read ( ipb_card_dict, ( "HUB2", "csr",   "control",  "HUB2:csr:control" ) )


print " HUB2 address 0x00000006 = status      RO reg "
read_value_status_hex = ipb_read ( ipb_card_dict, ( "HUB2", "csr",   "status",     "HUB2:csr:status" ) )

# mgt_equ_en      [29:17]  Enable equalization in MGT Fanout chips

mask_ROD_FanOut_EQ_en     = 0x3FFE0000

write_control_value_tmp = eval ( read_value_control_hex )
write_control_value_dec = write_control_value_tmp | mask_ROD_FanOut_EQ_en
write_control_value_hex = hex(write_control_value_dec)

print " Enable FanOut Equalizer "
ipb_write             ( ipb_card_dict,     ( "HUB2", "csr", "control", "HUB2:csr:control" ) ,              write_control_value_hex )


sleep (2)

print " HUB2 address 0x00000000 = control     RW reg"
read_value = ipb_read ( ipb_card_dict, ( "HUB2", "csr",   "control",  "HUB2:csr:control" ) )


print " HUB2 address 0x00000006 = status      RO reg "
read_value = ipb_read ( ipb_card_dict, ( "HUB2", "csr",   "status",     "HUB2:csr:status" ) )


