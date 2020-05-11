
print(htm)
print " %s address 0x00000010 = pkt_ctr/r_count      read counter" % (htm)
read_value_hex = ipb_read ( ipb_card_dict, ( htm, "pkt_ctr",   "r_count",  "%s:pkt_ctr:r_count" % (htm) ) )
print(read_value_hex)


print " %s address 0x00000010 = pkt_ctr/w_count      write counter" % (htm)
write_value_hex = ipb_read ( ipb_card_dict, ( htm, "pkt_ctr",   "w_count",  "%s:pkt_ctr:w_count" % (htm) ) )
print(write_value_hex)

