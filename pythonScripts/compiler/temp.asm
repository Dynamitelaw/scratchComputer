greatestCommonDenominator:
	#Input arg handling
	addi sp, sp, -8
	sw s0, -4(sp)
	sw s1, 0(sp)
	mv s0, a0
	mv s1, a1

	#Function body
	beq s0, zero, true_0
	j false_0
	true_0:
		#Do true stuff here
	j ifElseExit_0
	false_0:
		#Do false stuff here
	j ifElseExit_0
	ifElseExit_0:

	#Restore save registers from stack
	lw s0, -4(sp)
	lw s1, 0(sp)

	j ra

isPrime:
	#Input arg handling
	addi sp, sp, -8
	sw s0, -4(sp)
	sw s1, 0(sp)
	mv s0, a0
	mv s1, a1

	#Function body

	#Restore save registers from stack
	lw s0, -4(sp)
	lw s1, 0(sp)

	j ra

getAverage:
	#Input arg handling
	addi sp, sp, -8
	sw s0, -4(sp)
	sw s1, 0(sp)
	mv s0, a0
	mv s1, a1

	#Function body

	#Restore save registers from stack
	lw s0, -4(sp)
	lw s1, 0(sp)

	j ra

