.text
lw sp, stackPointerStart
addi ra, zero, PROGRAM_END
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
	lw a2, data_int_16711680
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
	lw s0, data_int_3960
	addi sp, sp, -4
	sw s0, 0(sp)
	addi sp, sp, -20
	addi t0, zero, 2
	addi t1, sp, 0
	addi t1, t1, 12
	lw t2, 0(t1)
	mv t2, t0
	sw t2, 0(t1)
	addi t0, zero, 1
	addi t1, sp, 0
	addi t1, t1, 8
	lw t2, 0(t1)
	mv t2, t0
	sw t2, 0(t1)
	addi t0, zero, 2
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
	addi t0, t0, 17
	lb t1, 0(t0)
	mv t1, zero
	sb t1, 0(t0)
	addi t0, sp, 0
	addi t0, t0, 16
	lb t1, 0(t0)
	mv t1, zero
	sb t1, 0(t0)
	addi sp, sp, -4
	addi sp, sp, -4
	addi s1, zero, 0
	addi sp, sp, -4
	sw s1, 0(sp)
	addi s10, zero, 0
	addi sp, sp, -4
	sw s10, 0(sp)
	sw s10, 0(sp)
	forLoopStart_3:
		addi t0, zero, 6
		blt s10, t0, forLoopBody_3
		j forLoopEnd_3
		forLoopBody_3:
			addi t0, sp, 60
			addi t0, t0, 4
			lw t1, 0(t0)
			addi sp, sp, -4
			sw s2, 0(sp)
			lw s2, 16(sp)
			mv s2, t1
			sw s2, 16(sp)
			addi t0, sp, 64
			lw t2, 0(t0)
			addi sp, sp, -4
			sw s3, 0(sp)
			lw s3, 16(sp)
			mv s3, t2
			sw s3, 16(sp)
			mv t0, s0
			addi t3, zero, 106
			addi t4, zero, 1
			mul t4, t3, t4
			add t0, t0, t4
			lb t4, 0(t0)
			bne t4, zero, true_0
			j false_0
			true_0:
				addi t0, sp, 24
				addi t0, t0, 17
				lb t5, 0(t0)
				mv t5, zero
				sb t5, 0(t0)
				addi t0, zero, 1
				addi t6, zero, -1
				mul t5, t0, t6
				addi t6, sp, 24
				addi t6, t6, 16
				lb a0, 0(t6)
				mv a0, t5
				sb a0, 0(t6)
			j ifElseExit_0
			false_0:
			ifElseExit_0:
			mv t0, s0
			addi t5, zero, 107
			addi t6, zero, 1
			mul t6, t5, t6
			add t0, t0, t6
			lb t6, 0(t0)
			bne t6, zero, true_1
			j false_1
			true_1:
				addi t0, sp, 24
				addi t0, t0, 17
				lb a0, 0(t0)
				mv a0, zero
				sb a0, 0(t0)
				addi t0, zero, 1
				addi a0, sp, 24
				addi a0, a0, 16
				lb a1, 0(a0)
				mv a1, t0
				sb a1, 0(a0)
			j ifElseExit_1
			false_1:
			ifElseExit_1:
			mv t0, s0
			addi a0, zero, 108
			addi a1, zero, 1
			mul a1, a0, a1
			add t0, t0, a1
			lb a1, 0(t0)
			bne a1, zero, true_2
			j false_2
			true_2:
				addi t0, zero, 1
				addi a3, zero, -1
				mul a2, t0, a3
				addi a3, sp, 24
				addi a3, a3, 17
				lb a4, 0(a3)
				mv a4, a2
				sb a4, 0(a3)
				addi a3, sp, 24
				addi a3, a3, 16
				lb a4, 0(a3)
				mv a4, zero
				sb a4, 0(a3)
			j ifElseExit_2
			false_2:
			ifElseExit_2:
			mv t0, s0
			addi a2, zero, 109
			addi a3, zero, 1
			mul a3, a2, a3
			add t0, t0, a3
			lb a3, 0(t0)
			bne a3, zero, true_3
			j false_3
			true_3:
				addi t0, zero, 1
				addi a4, sp, 24
				addi a4, a4, 17
				lb a5, 0(a4)
				mv a5, t0
				sb a5, 0(a4)
				addi a4, sp, 24
				addi a4, a4, 16
				lb a5, 0(a4)
				mv a5, zero
				sb a5, 0(a4)
			j ifElseExit_3
			false_3:
			ifElseExit_3:
			addi a5, sp, 24
			addi a5, a5, 12
			lw a6, 0(a5)
			addi a5, sp, 24
			addi a5, a5, 17
			lb a7, 0(a5)
			add a4, a6, a7
			addi a5, zero, 16
			rem t0, a4, a5
			addi a5, sp, 24
			addi a5, a5, 12
			addi sp, sp, -4
			sw s4, 0(sp)
			lw s4, 0(a5)
			mv s4, t0
			sw s4, 0(a5)
			addi a5, zero, 8
			addi s4, sp, 28
			addi s4, s4, 12
			addi sp, sp, -4
			sw s5, 0(sp)
			lw s5, 0(s4)
			mv s5, a5
			sw s5, 0(s4)
			addi sp, sp, -4
			sw s6, 0(sp)
			addi s6, sp, 36
			addi s6, s6, 8
			addi sp, sp, -4
			sw s7, 0(sp)
			lw s7, 0(s6)
			addi s6, sp, 40
			addi s6, s6, 16
			addi sp, sp, -4
			sw s8, 0(sp)
			lb s8, 0(s6)
			add s5, s7, s8
			addi s6, zero, 12
			rem s4, s5, s6
			addi s6, sp, 44
			addi s6, s6, 8
			addi sp, sp, -4
			sw s9, 0(sp)
			lw s9, 0(s6)
			mv s9, s4
			sw s9, 0(s6)
			addi s6, sp, 48
			addi s6, s6, 8
			lw s9, 0(s6)
			blt s9, zero, true_4
			j false_4
			true_4:
				addi s6, zero, 12
				sw s11, 88(sp)
				addi s11, sp, 48
				addi s11, s11, 8
				sw s0, 68(sp)
				lw s0, 0(s11)
				mv s0, s6
				sw s0, 0(s11)
				lw s11, 88(sp)
				lw s0, 68(sp)
			j ifElseExit_4
			false_4:
			ifElseExit_4:
			addi s6, sp, 48
			addi s6, s6, 4
			lw a0, 0(s6)
			addi s6, sp, 48
			lw a1, 0(s6)
			mv a2, zero
			mv s6, t1
			addi sp, sp, -4
			sw t0, 0(sp)
			addi sp, sp, -4
			sw a4, 0(sp)
			jal updatePixel
			addi t0, sp, 56
			addi t0, t0, 12
			lw a0, 0(t0)
			addi t0, sp, 56
			addi t0, t0, 8
			lw a1, 0(t0)
			lw a2, data_int_65280
			jal updatePixel
			addi t0, sp, 56
			addi t0, t0, 12
			lw t1, 0(t0)
			addi t0, sp, 56
			addi t0, t0, 4
			lw t2, 0(t0)
			mv t2, t1
			sw t2, 0(t0)
			addi t0, sp, 56
			addi t0, t0, 8
			lw t2, 0(t0)
			addi t0, sp, 56
			lw t3, 0(t0)
			mv t3, t2
			sw t3, 0(t0)
			addi t3, sp, 56
			addi t3, t3, 12
			lw t4, 0(t3)
			addi t3, sp, 100
			addi t3, t3, 4
			lw t5, 0(t3)
			slt t0, t4, t5
			slt t3, t5, t4
			add t0, t0, t3
			slti t0, t0, 1
			addi t6, sp, 56
			addi t6, t6, 8
			lw a0, 0(t6)
			addi t6, sp, 100
			lw a1, 0(t6)
			slt t3, a0, a1
			slt t6, a1, a0
			add t3, t3, t6
			slti t3, t3, 1
			mul t6, t0, t3
			bne t6, zero, true_5
			j false_5
			true_5:
				addi a0, sp, 100
				mv a1, s10
				mv s10, t1
				addi sp, sp, -4
				sw t0, 0(sp)
				addi sp, sp, -4
				sw t3, 0(sp)
				sw a1, 48(sp)
				jal iterateFoodPosition
				addi s1, s1, 1
				sw s1, 52(sp)
				lw s10, 48(sp)
				lw t0, 4(sp)
				lw t3, 0(sp)
				addi sp, sp, 8
			j ifElseExit_5
			false_5:
			ifElseExit_5:
			addi t6, sp, 100
			addi t6, t6, 4
			lw a0, 0(t6)
			addi t6, sp, 100
			lw a1, 0(t6)
			lw a2, data_int_16711680
			addi sp, sp, -4
			sw t0, 0(sp)
			addi sp, sp, -4
			sw t3, 0(sp)
			jal updatePixel
			addi a0, zero, 4
			jal delay
		sw s2, 60(sp)
		sw s3, 56(sp)
		lw s2, 44(sp)
		lw s3, 40(sp)
		addi sp, sp, -4
		sw s4, 0(sp)
		lw s4, 40(sp)
		addi sp, sp, -4
		sw s5, 0(sp)
		lw s5, 40(sp)
		lw s6, 36(sp)
		lw s7, 32(sp)
		lw s8, 28(sp)
		lw s9, 24(sp)
		addi sp, sp, 56
		addi s10, s10, 1
		sw s10, 0(sp)
		j forLoopStart_3
	forLoopEnd_3:
	mv ra, s11
	sw s0, 36(sp)
	lw s0, 52(sp)
	sw s1, 4(sp)
	lw s1, 48(sp)
	sw s10, 0(sp)
	lw s10, 44(sp)
	lw s11, 40(sp)
	addi sp, sp, 68
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
data_int_65280: .word 65280
stackPointerStart: .word 3072
