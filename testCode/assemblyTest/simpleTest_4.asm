######
# This code tests all supported instructions
# If test passes, all registers should store either 42 or 0
######

begin:
#Add, addi (negative numbers)
addi t0, zero, 73	# pc = 0
addi t1, zero, -31	# pc = 1
add t3, t1, t0 		# pc = 2
mv a0,t3			# pc = 3

jal clearTemps		# pc = 4,16

addi a0, zero, -1  	# pc = 5

clearTemps:
#Clear out temps
mv t0, zero			# pc = 6, 24
mv t1, zero			# pc = 7
mv t2, zero			# pc = 8
mv t3, zero			# pc = 9
mv t4, zero			# pc = 10
mv t5, zero			# pc = 11
mv t6, zero			# pc = 12