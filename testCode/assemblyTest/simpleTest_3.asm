######
# This code tests all supported instructions
# If test passes, all registers should store either 42 or 0
######

#Add, addi (negative numbers)
addi t0, zero, 73	# t0 = 18 + 0
addi t1, zero, -31	# t1 = 24 + 0
add t3, t1, t0 		# t3 = 18 + 24 = 42
mv a0,t3			# a0 = t3 = 42


#Clear out temps
mv t0, zero
mv t1, zero
mv t2, zero
mv t3, zero
mv t4, zero
mv t5, zero
mv t6, zero