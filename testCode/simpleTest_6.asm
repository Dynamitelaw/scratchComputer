######
# This code tests load and store instructions
# If test passes, a0 register should store 42
######

begin:
#Store values into a0,a1
addi a0, zero, 21	# a0 = 21
addi a1, zero, 2	# a1 = 2

#Set stack pointer to starting value
addi sp, zero, 32

#Allocate 8 bytes for the 2 integers
addi sp, sp, -8

#Store a0 and a1
sw a0, -4(sp)
sw a1, 0(sp)

#Load stored values into a2 and a3
lw a2, -4(sp)
lw a3, 0(sp)

#Multiply them, then store result in a0
mul a0, a2, a3  #a0 = 42

#Clear other registers
addi a1, zero, 0
addi a2, zero, 0
addi a3, zero, 0

####
# Test sub-word instructions by concatenating four bytes of 1s
####
addi t0, zero, 255

sb t0, 0(sp)
sb t0, 1(sp)
sb t0, 2(sp)
sb t0, 3(sp)
#-1 should now be in 0(sp)

lw a1, 0(sp)
addi t1, zero, -1

beq a1, t1, a1_make42
j clearTemps

a1_make42:
addi a1, zero, 42

clearTemps:
addi t0, zero, 0
addi t1, zero, 0

####
# Test signed/unsigned load instructions
####

signedBytedTest:
#Replace upper 2 bytes of word with 0s
sb zero, 2(sp)
sb zero, 3(sp)

#Load byte, and make sure result is sign extended to -1
lb t0, 0(sp)
addi t1, zero, -1

beq t0, t1, a2_make20
j unsignedByteTest

a2_make20:
addi a2, zero, 20

unsignedByteTest:
#Load unsigned byte, and make sure result is not sign extended
lbu t0, 0(sp)

#Load 255^2 -1 into t1
addi t1, zero, 256
mul t1, t1, t1
addi t1, t1, -1

beq t0, t1, a2_add22
j halfwordTest

a2_add22:
addi a2, a2, 22

#Load halfword, and make sure result is sign extended to -1
halfwordTest:
lh t0, 0(sp)
addi t1, zero, -1

beq t0, t1, a3_make20
j unsignedHalfwordTest

a3_make20:
addi a3, zero, 20

unsignedHalfwordTest:
#Load unsigned byte, and make sure result is not sign extended
lhu t0, 0(sp)

#Load 255^2 -1 into t1
addi t1, zero, 256
mul t1, t1, t1
addi t1, t1, -1

beq t0, t1, a3_add22
j exit

a3_add22:
addi a3, a3, 22

exit:
addi zero, zero, 0