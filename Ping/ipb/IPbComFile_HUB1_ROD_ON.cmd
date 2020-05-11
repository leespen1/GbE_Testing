

print " Hub1 address 0x00000000 = control     RW reg"
read_value_control_hex = ipb_read ( ipb_card_dict, ( "HUB1", "csr",   "control",  "HUB1:csr:control" ) )


print " Hub1 address 0x00000006 = status      RO reg "
read_value_status_hex = ipb_read ( ipb_card_dict, ( "HUB1", "csr",   "status",     "HUB1:csr:status" ) )

mask_ROD_power_ON_en     = 0x00000600

write_control_value_tmp = eval ( read_value_control_hex )
write_control_value_dec = write_control_value_tmp | mask_ROD_power_ON_en
write_control_value_hex = hex(write_control_value_dec)

print " Try to Power ROD  ON "
ipb_write             ( ipb_card_dict,     ( "HUB1", "csr", "control", "HUB1:csr:control" ) ,              write_control_value_hex )

sleep (2)

print " Hub1 address 0x00000000 = control     RW reg"
read_value = ipb_read ( ipb_card_dict, ( "HUB1", "csr",   "control",  "HUB1:csr:control" ) )


print " Hub1 address 0x00000006 = status      RO reg "
read_value = ipb_read ( ipb_card_dict, ( "HUB1", "csr",   "status",     "HUB1:csr:status" ) )


