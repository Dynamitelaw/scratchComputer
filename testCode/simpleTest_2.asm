######
# This code tests all supported instructions
# If test passes, all registers should store either 42 or 0
######

#Add, addi
addi t0, zero, 18	# t0 = 18 + 0
addi t1, zero, 24	# t1 = 24 + 0
add t3, t1, t0 		# t3 = 18 + 24 = 42
mv a0,t3			# a0 = t3 = 42

#Addi, Sub
addi t0, zero, 93
addi t1, zero, 51
sub t0, t0, t1
mv a1, t0

#Addi, Mul, Div
addi t0, zero, 7
addi t1, zero, 3
mul t2, t0, t1  #21
addi t3, zero, 14
div t4, t3, t0  #2
mul t5, t2, t4  #42
mv a2, t5

#Addi, Rem, Mul
addi t0, zero, 13
addi t1, zero, 5
rem t2, t0, t1  #3
addi t3, zero, 14
mul t4, t3, t2
mv a3, t4

#Addi, Slt, Slti 
addi t0, zero, 3
addi t1, zero, 4
addi t2, zero, 5
addi t3, zero, 42

slt t4, t0, t1  #1
slti t5, t2, 1  #0

mul t6, t3, t4  #42
add a4, t6, t5

#Clear out temps
mv t0, zero
mv t1, zero
mv t2, zero
mv t3, zero
mv t4, zero
mv t5, zero
mv t6, zero