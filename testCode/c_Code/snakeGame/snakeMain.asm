.text
lui sp, 1 #Loading val 5120
addi sp, sp, 1024
la ra, PROGRAM_END
la gp, HEAP_START
main:
	mv a0, zero
	addi sp, sp, -4
	sw ra, 0(sp)
	addi sp, sp, -4
	sw s0, 0(sp)
	mv s0, ra
	jal clearScreen
	addi sp, sp, -8
	addi t0, zero, 3
	addi t1, sp, 0
	addi t1, t1, 4
	lw t2, 0(t1)
	mv t2, t0
	sw t2, 0(t1)
	addi t0, zero, 1
	addi t1, sp, 0
	lw t2, 0(t1)
	mv t2, t0
	sw t2, 0(t1)
	addi t0, sp, 0
	addi t0, t0, 4
	lw a0, 0(t0)
	addi t0, sp, 0
	lw a1, 0(t0)
	lui a2, 4080 #Loading val 16711680
	addi a2, a2, 0
	addi sp, sp, -4
	sw s1, 0(sp)
	mv s1, a0
	addi sp, sp, -4
	sw s10, 0(sp)
	mv s10, a1
	addi sp, sp, -4
	sw s11, 0(sp)
	mv s11, a2
	jal updatePixel
	lui s1, 1 #Loading val 6008
	addi s1, s1, 1912
	addi sp, sp, -4
	sw s1, 0(sp)
	addi sp, sp, -16
	addi a0, zero, 16
	mv s10, a0
	jal malloc
	addi sp, sp, -4
	sw a0, 0(sp)
	addi t0, zero, 2
	addi t1, sp, 4
	addi t1, t1, 4
	lw t2, 0(t1)
	mv t2, t0
	sw t2, 0(t1)
	addi t0, zero, 1
	addi t1, sp, 4
	lw t2, 0(t1)
	mv t2, t0
	sw t2, 0(t1)
	addi t0, sp, 4
	addi t0, t0, 8
	lw t1, 0(t0)
	mv t1, zero
	sw t1, 0(t0)
	addi t0, sp, 4
	addi t0, t0, 12
	lw t1, 0(t0)
	mv t1, a0
	sw t1, 0(t0)
	addi t0, zero, 2
	mv t1, a0
	addi t1, t1, 4
	lw t2, 0(t1)
	mv t2, t0
	sw t2, 0(t1)
	mv t0, a0
	lw t1, 0(t0)
	mv t1, zero
	sw t1, 0(t0)
	addi t0, sp, 4
	mv t1, a0
	addi t1, t1, 8
	lw t2, 0(t1)
	mv t2, t0
	sw t2, 0(t1)
	mv t1, a0
	addi t1, t1, 12
	lw t2, 0(t1)
	mv t2, zero
	sw t2, 0(t1)
	addi s10, zero, 1
	addi sp, sp, -4
	sw s10, 0(sp)
	addi s11, zero, 0
	addi sp, sp, -4
	sw s11, 0(sp)
	addi sp, sp, -4
	sw s2, 0(sp)
	addi s2, zero, 2
	addi sp, sp, -4
	sw s2, 0(sp)
	addi sp, sp, -4
	sw s3, 0(sp)
	addi s3, zero, 100
	addi sp, sp, -4
	sw s3, 0(sp)
	addi sp, sp, -4
	sw s4, 0(sp)
	addi s4, zero, 0
	addi sp, sp, -4
	sw s4, 0(sp)
	whileLoopStart_0:
		j whileLoopBody_0
		whileLoopBody_0:
			mv t1, s1
			addi t2, zero, 16
			addi t3, zero, 1
			mul t3, t2, t3
			add t1, t1, t3
			lb t3, 0(t1)
			bne t3, zero, true_0
			j false_0
			true_0:
				addi a0, zero, 0
				mv ra, s0
				lw s0, 76(sp)
				sw s1, 52(sp)
				lw s1, 64(sp)
				sw s10, 28(sp)
				lw s10, 60(sp)
				sw s11, 24(sp)
				lw s11, 56(sp)
				sw s2, 16(sp)
				lw s2, 20(sp)
				sw s3, 8(sp)
				lw s3, 12(sp)
				sw s4, 0(sp)
				lw s4, 4(sp)
				addi sp, sp, 84
				jr ra
				addi sp, sp, -4
				sw s0, 0(sp)
				mv s0, ra
				addi sp, sp, -4
				sw s1, 0(sp)
				addi sp, sp, -4
				sw s10, 0(sp)
				addi sp, sp, -4
				sw s11, 0(sp)
				addi sp, sp, -4
				sw s2, 0(sp)
				addi sp, sp, -4
				sw s3, 0(sp)
				addi sp, sp, -4
				sw s4, 0(sp)
				addi sp, sp, 0
			j ifElseExit_0
			false_0:
			ifElseExit_0:
			mv t1, s1
			addi t4, zero, 106
			addi t5, zero, 1
			mul t5, t4, t5
			add t1, t1, t5
			lb t5, 0(t1)
			bne t5, zero, true_1
			j false_1
			true_1:
				mv s10, zero
				sw s10, 28(sp)
				addi t1, zero, 1
				addi a1, zero, -1
				mul t6, t1, a1
				mv s11, t6
				sw s11, 24(sp)
			j ifElseExit_1
			false_1:
			ifElseExit_1:
			mv t1, s1
			addi t6, zero, 107
			addi a1, zero, 1
			mul a1, t6, a1
			add t1, t1, a1
			lb a1, 0(t1)
			bne a1, zero, true_2
			j false_2
			true_2:
				mv s10, zero
				sw s10, 28(sp)
				addi t1, zero, 1
				mv s11, t1
				sw s11, 24(sp)
			j ifElseExit_2
			false_2:
			ifElseExit_2:
			mv t1, s1
			addi a2, zero, 108
			addi a3, zero, 1
			mul a3, a2, a3
			add t1, t1, a3
			lb a3, 0(t1)
			bne a3, zero, true_3
			j false_3
			true_3:
				addi t1, zero, 1
				addi a5, zero, -1
				mul a4, t1, a5
				mv s10, a4
				sw s10, 28(sp)
				mv s11, zero
				sw s11, 24(sp)
			j ifElseExit_3
			false_3:
			ifElseExit_3:
			mv t1, s1
			addi a4, zero, 109
			addi a5, zero, 1
			mul a5, a4, a5
			add t1, t1, a5
			lb a5, 0(t1)
			bne a5, zero, true_4
			j false_4
			true_4:
				addi t1, zero, 1
				mv s10, t1
				sw s10, 28(sp)
				mv s11, zero
				sw s11, 24(sp)
			j ifElseExit_4
			false_4:
			ifElseExit_4:
			addi sp, sp, -4
			sw s5, 0(sp)
			addi t1, sp, 40
			addi t1, t1, 4
			lw s5, 0(t1)
			addi sp, sp, -4
			sw s5, 0(sp)
			addi sp, sp, -4
			sw s6, 0(sp)
			addi a6, sp, 48
			lw s6, 0(a6)
			addi sp, sp, -4
			sw s6, 0(sp)
			addi sp, sp, -4
			sw s7, 0(sp)
			addi sp, sp, -4
			sw s8, 0(sp)
			addi s8, sp, 60
			addi s8, s8, 4
			addi sp, sp, -4
			sw s9, 0(sp)
			lw s9, 0(s8)
			add s7, s9, s10
			addi s8, zero, 32
			rem a7, s7, s8
			addi s8, sp, 64
			addi s8, s8, 4
			sw s0, 108(sp)
			lw s0, 0(s8)
			mv s0, a7
			sw s0, 0(s8)
			addi s0, sp, 64
			addi s0, s0, 4
			lw s8, 0(s0)
			blt s8, zero, true_5
			j false_5
			true_5:
				addi s0, zero, 32
				sw s1, 80(sp)
				addi s1, sp, 64
				addi s1, s1, 4
				sw a0, 60(sp)
				lw a0, 0(s1)
				mv a0, s0
				sw a0, 0(s1)
				lw s1, 80(sp)
				lw a0, 60(sp)
			j ifElseExit_5
			false_5:
			ifElseExit_5:
			sw s1, 80(sp)
			sw a0, 60(sp)
			addi a0, sp, 64
			lw t0, 0(a0)
			add s1, t0, s11
			addi a0, zero, 24
			rem s0, s1, a0
			addi a0, sp, 64
			sw s10, 56(sp)
			lw s10, 0(a0)
			mv s10, s0
			sw s10, 0(a0)
			addi a0, sp, 64
			lw s10, 0(a0)
			blt s10, zero, true_6
			j false_6
			true_6:
				addi a0, zero, 24
				sw s11, 52(sp)
				addi s11, sp, 64
				sw s2, 44(sp)
				lw s2, 0(s11)
				mv s2, a0
				sw s2, 0(s11)
				lw s11, 52(sp)
				lw s2, 44(sp)
			j ifElseExit_6
			false_6:
			ifElseExit_6:
			sw s11, 52(sp)
			addi s11, sp, 64
			addi s11, s11, 12
			lw a0, 0(s11)
			addi sp, sp, -4
			sw a0, 0(sp)
			sw s2, 48(sp)
			sw s3, 40(sp)
			addi s3, sp, 68
			addi s3, s3, 4
			lw s2, 0(s3)
			addi sp, sp, -4
			sw s2, 0(sp)
			sw s4, 36(sp)
			addi t2, sp, 72
			lw s4, 0(t2)
			addi sp, sp, -4
			sw s4, 0(sp)
			whileLoopStart_1:
			bne a0, zero, whileLoopBody_1
				j whileLoopEnd_1
				whileLoopBody_1:
					mv t4, a0
					addi t4, t4, 4
					lw t5, 0(t4)
					slt t3, s2, t5
					slt t4, t5, s2
					add t3, t3, t4
					slti t3, t3, 1
					mv t6, a0
					lw a1, 0(t6)
					slt t4, s4, a1
					slt t6, a1, s4
					add t4, t4, t6
					slti t4, t4, 1
					mul t6, t3, t4
					bne t6, zero, true_7
					j false_7
					true_7:
						sw a0, 8(sp)
						mv a0, s2
						mv a1, s4
						lui a2, 1  #Loading val 16776960
						addi a2, a2, 3840
						lui t6, 4095
						add a2, a2, t6
						mv s2, a3
						mv s4, a4
						addi sp, sp, -4
						sw a7, 0(sp)
						addi sp, sp, -4
						sw t3, 0(sp)
						addi sp, sp, -4
						sw t4, 0(sp)
						sw a0, 16(sp)
						sw a1, 12(sp)
						jal updatePixel
						lw a0, 16(sp)
						lw a1, 12(sp)
						lui a2, 1  #Loading val 16776960
						addi a2, a2, 3840
						lui t0, 4095
						add a2, a2, t0
						sw a0, 16(sp)
						sw a1, 12(sp)
						jal updatePixel
						addi a0, zero, 500
						jal delay
						addi t0, zero, 1
						addi t1, zero, -1
						mul a0, t0, t1
						lw ra, 132(sp)
						addi sp, sp, -4
						sw s0, 0(sp)
						lw s0, 132(sp)
						addi sp, sp, -4
						sw s1, 0(sp)
						lw s1, 124(sp)
						lw s10, 120(sp)
						lw s11, 116(sp)
						lw s2, 80(sp)
						lw s3, 72(sp)
						lw s4, 64(sp)
						sw s5, 52(sp)
						lw s5, 56(sp)
						sw s6, 44(sp)
						lw s6, 48(sp)
						addi sp, sp, -4
						sw s7, 0(sp)
						lw s7, 44(sp)
						lw s8, 40(sp)
						lw s9, 36(sp)
						addi sp, sp, 148
						jr ra
						addi sp, sp, -4
						sw ra, 0(sp)
						addi sp, sp, -4
						sw s0, 0(sp)
						addi sp, sp, -4
						sw s1, 0(sp)
						addi sp, sp, -4
						sw s10, 0(sp)
						addi sp, sp, -4
						sw s11, 0(sp)
						addi sp, sp, -4
						sw s2, 0(sp)
						addi sp, sp, -4
						sw s3, 0(sp)
						addi sp, sp, -4
						sw s4, 0(sp)
						addi sp, sp, -4
						sw s5, 0(sp)
						addi sp, sp, -4
						sw s6, 0(sp)
						addi sp, sp, -4
						sw s7, 0(sp)
						addi sp, sp, -4
						sw s8, 0(sp)
						addi sp, sp, -4
						sw s9, 0(sp)
						addi sp, sp, -4
						sw a0, 0(sp)
						addi sp, sp, 0
					j ifElseExit_7
					false_7:
					ifElseExit_7:
					mv t6, a0
					addi t6, t6, 12
					lw a2, 0(t6)
					mv a0, a2
					sw a0, 8(sp)
				j whileLoopStart_1
			whileLoopEnd_1:
			addi t4, sp, 76
			addi t4, t4, 4
			lw t5, 0(t4)
			addi t4, sp, 108
			addi t4, t4, 4
			lw t6, 0(t4)
			slt t3, t5, t6
			slt t4, t6, t5
			add t3, t3, t4
			slti t3, t3, 1
			addi a1, sp, 76
			lw a2, 0(a1)
			addi a1, sp, 108
			lw a3, 0(a1)
			slt t4, a2, a3
			slt a1, a3, a2
			add t4, t4, a1
			slti t4, t4, 1
			mul a1, t3, t4
			bne a1, zero, true_8
			j false_8
			true_8:
				sw a0, 8(sp)
				addi a0, sp, 108
				lw a1, 40(sp)
				addi sp, sp, -4
				sw a7, 0(sp)
				addi sp, sp, -4
				sw t3, 0(sp)
				addi sp, sp, -4
				sw t4, 0(sp)
				sw a1, 52(sp)
				jal iterateFoodPosition
				lw t0, 68(sp)
				addi t0, t0, 1
				sw t0, 68(sp)
				addi t1, zero, 4
				lw t2, 60(sp)
				sub t2, t2, t1
				sw t2, 60(sp)
				addi a0, zero, 16
				sw t0, 68(sp)
				sw t2, 60(sp)
				jal malloc
				addi sp, sp, -4
				sw a0, 0(sp)
				mv t0, a0
				addi t0, t0, 4
				lw t1, 0(t0)
				mv t1, s5
				sw t1, 0(t0)
				mv t0, a0
				lw t1, 0(t0)
				mv t1, s6
				sw t1, 0(t0)
				addi t0, sp, 92
				mv t1, a0
				addi t1, t1, 8
				lw t2, 0(t1)
				mv t2, t0
				sw t2, 0(t1)
				addi t1, sp, 92
				addi t1, t1, 12
				lw t2, 0(t1)
				mv t1, a0
				addi t1, t1, 12
				lw t3, 0(t1)
				mv t3, t2
				sw t3, 0(t1)
				addi t3, sp, 92
				addi t3, t3, 12
				lw t1, 0(t3)
				addi sp, sp, -4
				sw t1, 0(sp)
				mv t4, t1
				addi t4, t4, 8
				lw t5, 0(t4)
				mv t5, a0
				sw t5, 0(t4)
				addi t4, sp, 96
				addi t4, t4, 12
				lw t5, 0(t4)
				mv t5, a0
				sw t5, 0(t4)
				addi t4, sp, 96
				addi t4, t4, 4
				sw a0, 4(sp)
				lw a0, 0(t4)
				addi t4, sp, 96
				lw a1, 0(t4)
				lui a2, 1  #Loading val 65280
				addi a2, a2, 3840
				lui t4, 15
				add a2, a2, t4
				sw t1, 0(sp)
				jal updatePixel
				lw a7, 16(sp)
				lw a0, 28(sp)
				lw t3, 12(sp)
				lw t4, 8(sp)
				addi sp, sp, 20
			j ifElseExit_8
			false_8:
				lw a1, 72(sp)
				mv a4, a1
				addi a4, a4, 4
				sw a0, 8(sp)
				lw a0, 0(a4)
				mv a4, a1
				sw a1, 72(sp)
				lw a1, 0(a4)
				mv a2, zero
				addi sp, sp, -4
				sw a7, 0(sp)
				addi sp, sp, -4
				sw t3, 0(sp)
				addi sp, sp, -4
				sw t4, 0(sp)
				jal updatePixel
				addi t0, sp, 88
				addi t0, t0, 4
				lw a0, 0(t0)
				addi t0, sp, 88
				lw a1, 0(t0)
				lui a2, 1  #Loading val 65280
				addi a2, a2, 3840
				lui t0, 15
				add a2, a2, t0
				jal updatePixel
				lw t1, 84(sp)
				mv t2, t1
				addi t2, t2, 8
				lw t0, 0(t2)
				addi sp, sp, -4
				sw t0, 0(sp)
				mv t3, t1
				addi t3, t3, 4
				lw t4, 0(t3)
				mv t4, s5
				sw t4, 0(t3)
				mv t3, t1
				lw t4, 0(t3)
				mv t4, s6
				sw t4, 0(t3)
				addi t3, sp, 92
				mv t4, t1
				addi t4, t4, 8
				lw t5, 0(t4)
				mv t5, t3
				sw t5, 0(t4)
				addi t4, sp, 92
				addi t4, t4, 12
				lw t5, 0(t4)
				mv t4, t1
				addi t4, t4, 12
				lw t6, 0(t4)
				mv t6, t5
				sw t6, 0(t4)
				addi t6, sp, 92
				addi t6, t6, 12
				lw t4, 0(t6)
				addi sp, sp, -4
				sw t4, 0(sp)
				mv a0, t4
				addi a0, a0, 8
				lw a1, 0(a0)
				mv a1, t1
				sw a1, 0(a0)
				mv a0, t0
				addi a0, a0, 12
				lw a1, 0(a0)
				mv a1, zero
				sw a1, 0(a0)
				addi a0, sp, 96
				addi a0, a0, 12
				lw a1, 0(a0)
				mv a1, t1
				sw a1, 0(a0)
				mv t1, t0
				sw t1, 92(sp)
				sw t1, 92(sp)
				lw a7, 16(sp)
				lw a0, 28(sp)
				lw t3, 12(sp)
				sw t4, 0(sp)
				lw t4, 8(sp)
				addi sp, sp, 20
			ifElseExit_8:
			addi a1, sp, 108
			addi a1, a1, 4
			sw a0, 8(sp)
			lw a0, 0(a1)
			addi a1, sp, 108
			lw a1, 0(a1)
			lui a2, 4080 #Loading val 16711680
			addi a2, a2, 0
			addi sp, sp, -4
			sw a7, 0(sp)
			addi sp, sp, -4
			sw t3, 0(sp)
			addi sp, sp, -4
			sw t4, 0(sp)
			jal updatePixel
			lw t0, 60(sp)
			blt zero, t0, true_9
			j false_9
			true_9:
				mv a0, t0
				sw a0, 60(sp)
				jal delay
				lw t0, 60(sp)
			j ifElseExit_9
			false_9:
			ifElseExit_9:
			lw t1, 52(sp)
			addi t1, t1, 1
			sw t1, 52(sp)
		addi sp, sp, -4
		sw s0, 0(sp)
		lw s0, 136(sp)
		addi sp, sp, -4
		sw s1, 0(sp)
		lw s1, 112(sp)
		lw a0, 92(sp)
		lw s10, 88(sp)
		lw s11, 84(sp)
		sw s2, 24(sp)
		lw s2, 76(sp)
		mv s3, t0
		sw s4, 20(sp)
		mv s4, t1
		sw s5, 52(sp)
		lw s5, 56(sp)
		sw s6, 44(sp)
		lw s6, 48(sp)
		addi sp, sp, -4
		sw s7, 0(sp)
		lw s7, 44(sp)
		lw s8, 40(sp)
		lw s9, 36(sp)
		addi sp, sp, 64
		j whileLoopStart_0
	whileLoopEnd_0:
	mv ra, s0
	lw s0, 76(sp)
	sw s1, 52(sp)
	lw s1, 64(sp)
	sw s10, 28(sp)
	lw s10, 60(sp)
	sw s11, 24(sp)
	lw s11, 56(sp)
	sw s2, 16(sp)
	lw s2, 20(sp)
	sw s3, 8(sp)
	lw s3, 12(sp)
	sw s4, 0(sp)
	lw s4, 4(sp)
	addi sp, sp, 84
	jr ra

malloc:
	addi t5, zero, 5
	bge a0, t5, ALIGN_WORD
	ALIGN_SUBWORD:
	rem t0, gp, a0
	add gp, gp, t0
	j INCREMENT_GP
	ALIGN_WORD:
	addi t4, zero, 4
	rem t0, gp, t4
	add gp, gp, t0
	INCREMENT_GP:
	mv t0, gp
	add gp, gp, a0
	mv a0, t0
	jr ra
	jr ra

updatePixel:
	lui t1, 1  #Loading val 6144
	addi t1, t1, 2048
	lui t2, 1
	add t1, t1, t2
	addi t3, zero, 4
	addi t6, zero, 32
	mul t5, a1, t6
	add t4, t5, a0
	mul t2, t3, t4
	add t0, t1, t2
	addi sp, sp, -4
	sw t0, 0(sp)
	lw t1, 0(t0)
	mv t1, a2
	sw t1, 0(t0)
	addi sp, sp, -4
	sw t1, 0(sp)
	sw t0, 4(sp)
	addi sp, sp, 8
	jr ra

clearScreen:
	addi sp, sp, -4
	sw s0, 0(sp)
	lui s0, 1  #Loading val 6144
	addi s0, s0, 2048
	lui t0, 1
	add s0, s0, t0
	addi sp, sp, -4
	sw s0, 0(sp)
	addi sp, sp, -4
	sw s1, 0(sp)
	addi s1, zero, 0
	addi sp, sp, -4
	sw s1, 0(sp)
	sw s1, 0(sp)
	forLoopStart_0:
		addi t0, zero, 24
		blt s1, t0, forLoopBody_0
		j forLoopEnd_0
		forLoopBody_0:
			addi sp, sp, -4
			sw s10, 0(sp)
			addi s10, zero, 0
			addi sp, sp, -4
			sw s10, 0(sp)
			sw s10, 0(sp)
			forLoopStart_1:
				addi t0, zero, 32
				blt s10, t0, forLoopBody_1
				j forLoopEnd_1
				forLoopBody_1:
					lw t0, 0(s0)
					mv t0, a0
					sw t0, 0(s0)
					addi sp, sp, -4
					sw t0, 0(sp)
					sw s0, 20(sp)
					addi t0, zero, 4
					lw s0, 20(sp)
					add s0, s0, t0
					sw s0, 20(sp)
				addi sp, sp, 4
				addi s10, s10, 1
				sw s10, 0(sp)
				j forLoopStart_1
			forLoopEnd_1:
		sw s10, 0(sp)
		lw s10, 4(sp)
		addi sp, sp, 8
		addi s1, s1, 1
		sw s1, 0(sp)
		j forLoopStart_0
	forLoopEnd_0:
	sw s0, 8(sp)
	lw s0, 12(sp)
	sw s1, 0(sp)
	lw s1, 4(sp)
	addi sp, sp, 16
	jr ra

delay:
	addi sp, sp, -4
	sw s0, 0(sp)
	addi s0, zero, 0
	addi sp, sp, -4
	sw s0, 0(sp)
	addi sp, sp, -4
	sw s1, 0(sp)
	addi s1, zero, 0
	addi sp, sp, -4
	sw s1, 0(sp)
	sw s1, 0(sp)
	forLoopStart_2:
		blt s1, a0, forLoopBody_2
		j forLoopEnd_2
		forLoopBody_2:
			addi s0, s0, 1
			sw s0, 8(sp)
		addi s1, s1, 1
		sw s1, 0(sp)
		j forLoopStart_2
	forLoopEnd_2:
	addi sp, sp, -4
	sw a0, 0(sp)
	mv a0, s0
	lw s0, 16(sp)
	sw s1, 4(sp)
	lw s1, 8(sp)
	addi sp, sp, 20
	jr ra
	jr ra

iterateFoodPosition:
	addi sp, sp, -4
	sw s0, 0(sp)
	mv t0, a0
	addi t0, t0, 4
	lw s0, 0(t0)
	addi sp, sp, -4
	sw s0, 0(sp)
	addi sp, sp, -4
	sw s1, 0(sp)
	mv t0, a0
	lw s1, 0(t0)
	addi sp, sp, -4
	sw s1, 0(sp)
	addi t4, zero, 3
	mul t3, s0, t4
	addi t5, zero, 7
	mul t4, s1, t5
	add t2, t3, t4
	addi t6, zero, 5
	mul t5, a1, t6
	add t1, t2, t5
	addi t6, zero, 32
	rem t0, t1, t6
	addi sp, sp, -4
	sw t0, 0(sp)
	addi a5, zero, 2
	mul a4, s0, a5
	addi a6, zero, 11
	mul a5, s1, a6
	add a3, a4, a5
	addi a7, zero, 3
	mul a6, a1, a7
	add a2, a3, a6
	addi a7, zero, 24
	rem t6, a2, a7
	addi sp, sp, -4
	sw t6, 0(sp)
	mv a7, a0
	addi a7, a7, 4
	addi sp, sp, -4
	sw s10, 0(sp)
	lw s10, 0(a7)
	mv s10, t0
	sw s10, 0(a7)
	mv a7, a0
	lw s10, 0(a7)
	mv s10, t6
	sw s10, 0(a7)
	sw s0, 20(sp)
	lw s0, 24(sp)
	sw s1, 12(sp)
	lw s1, 16(sp)
	lw s10, 0(sp)
	addi sp, sp, 28
	jr ra

PROGRAM_END:
add zero, zero, zero
.data
HEAP_START: .word 0
