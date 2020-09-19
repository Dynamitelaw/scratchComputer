######
# This code tests the add and add_imediate instructions
# Will add 18+24, and move the answer 42 into t6(register31)
######

addi t0, zero, 18	# t0 = 18 + 0
addi t1, zero, 24	# t1 = 24 + 0
add t3, t1, t0 		# t3 = 18 + 24 = 42
mv t6,t3			# t6 = t3 = 42

