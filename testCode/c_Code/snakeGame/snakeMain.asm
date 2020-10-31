.text
lw sp, stackPointerStart
addi ra, zero, PROGRAM_END
main:
	mv a0, zero
	addi sp, sp, -4
	sw ra, 0(sp)
	addi sp, sp, -4
	sw s0, 0(sp)
	mv s0, ra
	jal clearScreen
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
	lw a2, data_int_16711680
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
	lw s1, data_int_3960
	addi sp, sp, -4
	sw s1, 0(sp)
	addi sp, sp, -4
	addi sp, sp, -4
	addi s10, zero, 0
	addi sp, sp, -4
	sw s10, 0(sp)
	sw s10, 0(sp)
	forLoopStart_3:
		addi t0, zero, 30
		blt s10, t0, forLoopBody_3
		j forLoopEnd_3
		forLoopBody_3:
			addi t0, sp, 28
			addi t0, t0, 4
			lw t1, 0(t0)
			lw s11, 8(sp)
			mv s11, t1
			sw s11, 8(sp)
			addi t0, sp, 28
			lw t2, 0(t0)
			addi sp, sp, -4
			sw s2, 0(sp)
			lw s2, 8(sp)
			mv s2, t2
			sw s2, 8(sp)
			mv t0, s1
			addi t3, zero, 106
			addi t4, zero, 1
			mul t4, t3, t4
			add t0, t0, t4
			lb t4, 0(t0)
			bne t4, zero, true_0
			j false_0
			true_0:
				addi t6, zero, 1
				sub t5, s2, t6
				addi t6, zero, 12
				rem t0, t5, t6
				addi t6, sp, 32
				lw a0, 0(t6)
				mv a0, t0
				sw a0, 0(t6)
			j ifElseExit_0
			false_0:
			ifElseExit_0:
			mv t0, s1
			addi t5, zero, 107
			addi t6, zero, 1
			mul t6, t5, t6
			add t0, t0, t6
			lb t6, 0(t0)
			bne t6, zero, true_1
			j false_1
			true_1:
				addi a1, zero, 1
				add a0, s2, a1
				addi a1, zero, 12
				rem t0, a0, a1
				addi a1, sp, 32
				lw a2, 0(a1)
				mv a2, t0
				sw a2, 0(a1)
			j ifElseExit_1
			false_1:
			ifElseExit_1:
			mv t0, s1
			addi a0, zero, 108
			addi a1, zero, 1
			mul a1, a0, a1
			add t0, t0, a1
			lb a1, 0(t0)
			bne a1, zero, true_2
			j false_2
			true_2:
				addi a3, zero, 1
				sub a2, s11, a3
				addi a3, zero, 16
				rem t0, a2, a3
				addi a3, sp, 32
				addi a3, a3, 4
				lw a4, 0(a3)
				mv a4, t0
				sw a4, 0(a3)
			j ifElseExit_2
			false_2:
			ifElseExit_2:
			mv t0, s1
			addi a2, zero, 109
			addi a3, zero, 1
			mul a3, a2, a3
			add t0, t0, a3
			lb a3, 0(t0)
			bne a3, zero, true_3
			j false_3
			true_3:
				addi a5, zero, 1
				add a4, s11, a5
				addi a5, zero, 16
				rem t0, a4, a5
				addi a5, sp, 32
				addi a5, a5, 4
				lw a6, 0(a5)
				mv a6, t0
				sw a6, 0(a5)
			j ifElseExit_3
			false_3:
			ifElseExit_3:
			addi t0, sp, 32
			addi t0, t0, 4
			lw a0, 0(t0)
			addi t0, sp, 32
			lw a1, 0(t0)
			lw a2, data_int_16711680
			addi sp, sp, -4
			sw s3, 0(sp)
			mv s3, t1
			addi sp, sp, -4
			sw s4, 0(sp)
			mv s4, t2
			addi sp, sp, -4
			sw s5, 0(sp)
			mv s5, t3
			addi sp, sp, -4
			sw s6, 0(sp)
			mv s6, t4
			addi sp, sp, -4
			sw s7, 0(sp)
			mv s7, t5
			addi sp, sp, -4
			sw s8, 0(sp)
			mv s8, t6
			addi sp, sp, -4
			sw s9, 0(sp)
			mv s9, a3
			jal updatePixel
			addi a0, zero, 400
			jal delay
			mv a0, s11
			mv a1, s2
			mv a2, zero
			mv s11, a0
			mv s2, a1
			jal updatePixel
		sw s11, 40(sp)
		sw s2, 36(sp)
		lw s2, 28(sp)
		lw s3, 24(sp)
		lw s4, 20(sp)
		lw s5, 16(sp)
		lw s6, 12(sp)
		lw s7, 8(sp)
		lw s8, 4(sp)
		lw s9, 0(sp)
		addi sp, sp, 32
		addi s10, s10, 1
		sw s10, 0(sp)
		j forLoopStart_3
	forLoopEnd_3:
	mv ra, s0
	lw s0, 36(sp)
	sw s1, 12(sp)
	lw s1, 24(sp)
	sw s10, 0(sp)
	lw s10, 20(sp)
	lw s11, 16(sp)
	addi sp, sp, 44
	jr ra

updatePixel:
	lw t1, data_int_4096
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
	lw s0, data_int_4096
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
data_int_4096: .word 4096
data_int_16711680: .word 16711680
data_int_3960: .word 3960
stackPointerStart: .word 3072
