.text
lui sp, 1 #Loading val 3072
addi sp, sp, 3072
la ra, PROGRAM_END
la gp, HEAP_START
main:
	addi sp, sp, -8
	addi t0, zero, 8
	addi t1, sp, 0
	addi t1, t1, 4
	lw t2, 0(t1)
	mv t2, t0
	sw t2, 0(t1)
	addi t0, zero, 4
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
	sw ra, 0(sp)
	addi sp, sp, -4
	sw s0, 0(sp)
	mv s0, a0
	addi sp, sp, -4
	sw s1, 0(sp)
	mv s1, a1
	addi sp, sp, -4
	sw s10, 0(sp)
	mv s10, a2
	addi sp, sp, -4
	sw s11, 0(sp)
	mv s11, ra
	jal updatePixel
	lui s0, 1  #Loading val 3960
	addi s0, s0, 3960
	addi sp, sp, -4
	sw s0, 0(sp)
	addi sp, sp, -16
	addi sp, sp, -16
	addi t0, zero, 2
	addi t1, sp, 16
	addi t1, t1, 4
	lw t2, 0(t1)
	mv t2, t0
	sw t2, 0(t1)
	addi t0, zero, 1
	addi t1, sp, 16
	lw t2, 0(t1)
	mv t2, t0
	sw t2, 0(t1)
	addi t0, sp, 16
	addi t0, t0, 8
	lw t1, 0(t0)
	mv t1, zero
	sw t1, 0(t0)
	addi t0, sp, 0
	addi t1, sp, 16
	addi t1, t1, 12
	lw t2, 0(t1)
	mv t2, t0
	sw t2, 0(t1)
	addi t1, zero, 2
	addi t2, sp, 0
	addi t2, t2, 4
	lw t3, 0(t2)
	mv t3, t1
	sw t3, 0(t2)
	addi t1, zero, 1
	addi t2, sp, 0
	lw t3, 0(t2)
	mv t3, t1
	sw t3, 0(t2)
	addi t1, sp, 16
	addi t2, sp, 0
	addi t2, t2, 8
	lw t3, 0(t2)
	mv t3, t1
	sw t3, 0(t2)
	addi t2, sp, 0
	addi t2, t2, 12
	lw t3, 0(t2)
	mv t3, zero
	sw t3, 0(t2)
	addi s1, zero, 0
	addi sp, sp, -4
	sw s1, 0(sp)
	addi s10, zero, 0
	addi sp, sp, -4
	sw s10, 0(sp)
	addi sp, sp, -4
	sw s2, 0(sp)
	addi s2, zero, 0
	addi sp, sp, -4
	sw s2, 0(sp)
	addi sp, sp, -4
	sw s3, 0(sp)
	addi s3, zero, 0
	addi sp, sp, -4
	sw s3, 0(sp)
	sw s3, 0(sp)
	forLoopStart_3:
		addi t2, zero, 60
		blt s3, t2, forLoopBody_3
		j forLoopEnd_3
		forLoopBody_3:
			mv t2, s0
			addi t3, zero, 106
			addi t4, zero, 1
			mul t4, t3, t4
			add t2, t2, t4
			lb t4, 0(t2)
			bne t4, zero, true_0
			j false_0
			true_0:
				mv s1, zero
				sw s1, 20(sp)
				addi t2, zero, 1
				addi t6, zero, -1
				mul t5, t2, t6
				mv s10, t5
				sw s10, 16(sp)
			j ifElseExit_0
			false_0:
			ifElseExit_0:
			mv t2, s0
			addi t5, zero, 107
			addi t6, zero, 1
			mul t6, t5, t6
			add t2, t2, t6
			lb t6, 0(t2)
			bne t6, zero, true_1
			j false_1
			true_1:
				mv s1, zero
				sw s1, 20(sp)
				addi t2, zero, 1
				mv s10, t2
				sw s10, 16(sp)
			j ifElseExit_1
			false_1:
			ifElseExit_1:
			mv t2, s0
			addi a0, zero, 108
			addi a1, zero, 1
			mul a1, a0, a1
			add t2, t2, a1
			lb a1, 0(t2)
			bne a1, zero, true_2
			j false_2
			true_2:
				addi t2, zero, 1
				addi a3, zero, -1
				mul a2, t2, a3
				mv s1, a2
				sw s1, 20(sp)
				mv s10, zero
				sw s10, 16(sp)
			j ifElseExit_2
			false_2:
			ifElseExit_2:
			mv t2, s0
			addi a2, zero, 109
			addi a3, zero, 1
			mul a3, a2, a3
			add t2, t2, a3
			lb a3, 0(t2)
			bne a3, zero, true_3
			j false_3
			true_3:
				addi t2, zero, 1
				mv s1, t2
				sw s1, 20(sp)
				mv s10, zero
				sw s10, 16(sp)
			j ifElseExit_3
			false_3:
			ifElseExit_3:
			addi a5, sp, 40
			addi a5, a5, 4
			lw a6, 0(a5)
			add a4, a6, s1
			addi a5, zero, 16
			rem t2, a4, a5
			addi a5, sp, 40
			addi a5, a5, 4
			lw a7, 0(a5)
			mv a7, t2
			sw a7, 0(a5)
			addi a5, sp, 40
			addi a5, a5, 4
			lw a7, 0(a5)
			blt a7, zero, true_4
			j false_4
			true_4:
				addi a5, zero, 16
				addi sp, sp, -4
				sw s4, 0(sp)
				addi s4, sp, 44
				addi s4, s4, 4
				addi sp, sp, -4
				sw s5, 0(sp)
				lw s5, 0(s4)
				mv s5, a5
				sw s5, 0(s4)
				lw s4, 4(sp)
				lw s5, 0(sp)
				addi sp, sp, 8
			j ifElseExit_4
			false_4:
			ifElseExit_4:
			addi sp, sp, -4
			sw s4, 0(sp)
			addi sp, sp, -4
			sw s5, 0(sp)
			addi s5, sp, 48
			addi sp, sp, -4
			sw s6, 0(sp)
			lw s6, 0(s5)
			add s4, s6, s10
			addi s5, zero, 12
			rem a5, s4, s5
			addi s5, sp, 52
			addi sp, sp, -4
			sw s7, 0(sp)
			lw s7, 0(s5)
			mv s7, a5
			sw s7, 0(s5)
			addi s5, sp, 56
			lw s7, 0(s5)
			blt s7, zero, true_5
			j false_5
			true_5:
				addi s5, zero, 12
				addi sp, sp, -4
				sw s8, 0(sp)
				addi s8, sp, 60
				addi sp, sp, -4
				sw s9, 0(sp)
				lw s9, 0(s8)
				mv s9, s5
				sw s9, 0(s8)
				lw s8, 4(sp)
				lw s9, 0(sp)
				addi sp, sp, 8
			j ifElseExit_5
			false_5:
			ifElseExit_5:
			addi s5, sp, 40
			addi s5, s5, 4
			lw a0, 0(s5)
			addi s5, sp, 40
			lw a1, 0(s5)
			mv a2, zero
			mv s5, t0
			addi sp, sp, -4
			sw s8, 0(sp)
			mv s8, t1
			addi sp, sp, -4
			sw s9, 0(sp)
			mv s9, t3
			addi sp, sp, -4
			sw t2, 0(sp)
			addi sp, sp, -4
			sw a4, 0(sp)
			addi sp, sp, -4
			sw a5, 0(sp)
			jal updatePixel
			addi t0, sp, 76
			addi t0, t0, 4
			lw a0, 0(t0)
			addi t0, sp, 76
			lw a1, 0(t0)
			lui a2, 1  #Loading val 65280
			addi a2, a2, 3840
			lui t0, 15
			add a2, a2, t0
			jal updatePixel
			addi t0, sp, 76
			addi t0, t0, 4
			lw t1, 0(t0)
			addi t0, sp, 60
			addi t0, t0, 4
			lw t2, 0(t0)
			mv t2, t1
			sw t2, 0(t0)
			addi t0, sp, 76
			lw t2, 0(t0)
			addi t0, sp, 60
			lw t3, 0(t0)
			mv t3, t2
			sw t3, 0(t0)
			addi t3, sp, 76
			addi t3, t3, 4
			lw t4, 0(t3)
			addi t3, sp, 116
			addi t3, t3, 4
			lw t5, 0(t3)
			slt t0, t4, t5
			slt t3, t5, t4
			add t0, t0, t3
			slti t0, t0, 1
			addi t6, sp, 76
			lw a0, 0(t6)
			addi t6, sp, 116
			lw a1, 0(t6)
			slt t3, a0, a1
			slt t6, a1, a0
			add t3, t3, t6
			slti t3, t3, 1
			mul t6, t0, t3
			bne t6, zero, true_6
			j false_6
			true_6:
				addi a0, sp, 116
				mv a1, s3
				mv s3, t1
				addi sp, sp, -4
				sw t0, 0(sp)
				addi sp, sp, -4
				sw t3, 0(sp)
				sw a1, 44(sp)
				jal iterateFoodPosition
				addi s2, s2, 1
				sw s2, 52(sp)
				lw s3, 44(sp)
				lw t0, 4(sp)
				lw t3, 0(sp)
				addi sp, sp, 8
			j ifElseExit_6
			false_6:
			ifElseExit_6:
			addi t6, sp, 116
			addi t6, t6, 4
			lw a0, 0(t6)
			addi t6, sp, 116
			lw a1, 0(t6)
			lui a2, 4080 #Loading val 16711680
			addi a2, a2, 0
			addi sp, sp, -4
			sw t0, 0(sp)
			addi sp, sp, -4
			sw t3, 0(sp)
			jal updatePixel
			addi a0, zero, 400
			jal delay
		mv t0, s5
		mv t1, s8
		addi sp, sp, -4
		sw s4, 0(sp)
		lw s4, 44(sp)
		lw s5, 40(sp)
		lw s6, 36(sp)
		lw s7, 32(sp)
		lw s8, 28(sp)
		lw s9, 24(sp)
		addi sp, sp, 48
		addi s3, s3, 1
		sw s3, 0(sp)
		j forLoopStart_3
	forLoopEnd_3:
	mv ra, s11
	sw s0, 56(sp)
	lw s0, 72(sp)
	sw s1, 20(sp)
	lw s1, 68(sp)
	sw s10, 16(sp)
	lw s10, 64(sp)
	lw s11, 60(sp)
	sw s2, 8(sp)
	lw s2, 12(sp)
	sw s3, 0(sp)
	lw s3, 4(sp)
	addi sp, sp, 88
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
	lui t1, 1 #Loading val 4096
	addi t1, t1, 0
	addi t3, zero, 4
	addi t6, zero, 16
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
	lui s0, 1 #Loading val 4096
	addi s0, s0, 0
	addi sp, sp, -4
	sw s0, 0(sp)
	addi sp, sp, -4
	sw s1, 0(sp)
	addi s1, zero, 0
	addi sp, sp, -4
	sw s1, 0(sp)
	sw s1, 0(sp)
	forLoopStart_0:
		addi t0, zero, 12
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
				addi t0, zero, 16
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
	addi t6, zero, 16
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
	addi a7, zero, 12
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
