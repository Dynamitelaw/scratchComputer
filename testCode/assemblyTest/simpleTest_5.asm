######
# This code tests branch and jump instructions
# If test passes, a0 register should store 42
######

begin:
#Store 0 into a0
addi a0, zero, 0	# pc = 0

###
# Loop a0 +=1 42 times
###
addi t0, zero, 0  #counting variable
addi t1, zero, 42  #counterLimit

for_loopStart:
	addi a0, a0, 1  #a0 ++
	addi t0, t0, 1  #t0 ++

	beq t0, t1, for_loopExit
	j for_loopStart
for_loopExit:


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