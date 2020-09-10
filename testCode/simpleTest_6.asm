######
# This code tests load and store instructions
# If test passes, a0 register should store 42
######

begin:
#Store values into a0,a1
addi a0, zero, 21	# a0 = 21
addi a1, zero, 2	# a1 = 2

#Set stack pointer to starting value?
addi sp, zero, 255

#Allocate 8 bytes for the 2 integers
addi sp, sp, -8

#Store a0 and a1
sw a0, -4(sp)
addi sp, sp, 4
sw a0, 0(sp)

#Load stored values into a2 and a3
lw a2, -4(sp)
addi sp, sp, -4
lw a3, 0(sp)

#Multiply them, then store result in a0
mul a0, a2, a3
