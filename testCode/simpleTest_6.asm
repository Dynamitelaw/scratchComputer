######
# This code tests load and store instructions
# If test passes, a0 register should store 42
######

begin:
#Store values into a0,a1
addi a0, zero, 21	# a0 = 21
addi a1, zero, 2	# a1 = 2

#Set stack pointer to ?
addi sp, zero, startSp

#Store a0 and a1
sw a0, sp, offset
addi sp, sp, 4
sw a0, sp, offset

#Load stored values into a2 and a3
lw a2, sp, offset
addi sp, sp, -4
lw a3, sp, offset

#Multiply them, then store result in a0
mul a0, a2, a3


#Dummy labels
offset:
startSp:
