FuncCall(name=ID(name='greatestCommonDenominator'
                 ),
         args=ExprList(exprs=[BinaryOp(op='%',
                                       left=ID(name='y'
                                               ),
                                       right=ID(name='x'
                                                )
                                       ),
                              ID(name='x'
                                 )
                             ]
                       )
         )
greatestCommonDenominator:
	beq a0, zero, true_0
	j false_0
	true_0:
		addi sp, sp, -4
		sw a0, 0(sp)
		mv a0, a1
		j ra
		addi sp, sp, -4
		sw a0, 0(sp)
		lw a0, 4(sp)
		lw a1, 0(sp)
		addi sp, sp, 8
	j ifElseExit_0
	false_0:
		addi sp, sp, -4
		sw a0, 0(sp)
		lw t6, 0(sp)
		rem a0, a1, t6
		addi sp, sp, -4
		sw a1, 0(sp)
		mv a1, t6
		addi sp, sp, -4
		sw ra, 0(sp)
		j greatestCommonDenominator
		lw ra, 0(sp)
		j ra
		mv a0, a1
		lw a1, 4(sp)
		addi sp, sp, 12
	ifElseExit_0:
	j ra

