.text
lw sp, stackPointerStart
addi ra, zero, PROGRAM_END
main:
	addi sp, sp, -32
	addi t0, sp, 0
	lw t1, data_int_16711680
	sw t1, 0(t0)
	lw t1, data_int_65280
	sw t1, 4(t0)
	addi t1, zero, 255
	sw t1, 8(t0)
	lw t1, data_int_16776960
	sw t1, 12(t0)
	lw t1, data_int_16711935
	sw t1, 16(t0)
	lw t1, data_int_65535
	sw t1, 20(t0)
	lw t1, data_int_13421772
	sw t1, 24(t0)
	sw zero, 28(t0)
	addi sp, sp, -4
	sw s0, 0(sp)
	addi s0, zero, 0
	addi sp, sp, -4
	sw s0, 0(sp)
	sw s0, 0(sp)
	forLoopStart_2:
		addi t0, zero, 8
		blt s0, t0, forLoopBody_2
		j forLoopEnd_2
		forLoopBody_2:
			addi t0, sp, 8
			addi t1, zero, 4
			mul t1, s0, t1
			add t0, t0, t1
			lw a0, 0(t0)
			addi sp, sp, -4
			sw ra, 0(sp)
			addi sp, sp, -4
			sw s1, 0(sp)
			mv s1, a0
			addi sp, sp, -4
			sw s10, 0(sp)
			mv s10, ra
			jal clearScreen
		mv ra, s10
		lw s1, 4(sp)
		lw s10, 0(sp)
		addi sp, sp, 12
		addi s0, s0, 1
		sw s0, 0(sp)
		j forLoopStart_2
	forLoopEnd_2:
	addi a0, zero, 42
	sw s0, 0(sp)
	lw s0, 4(sp)
	addi sp, sp, 40
	jr ra
	jr ra

updatePixel:
	lw t2, data_int_4096
	addi t4, zero, 4
	mul t3, a1, t4
	add t1, t2, t3
	add t0, t1, a0
	addi sp, sp, -4
	sw t0, 0(sp)
	lw t2, 0(t0)
	mv t2, a2
	sw t2, 0(t0)
	addi sp, sp, -4
	sw t2, 0(sp)
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
		addi t0, zero, 3
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
				addi t0, zero, 4
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

PROGRAM_END:
add zero, zero, zero
.data
data_int_4096: .word 4096
data_int_16711680: .word 16711680
data_int_65280: .word 65280
data_int_16776960: .word 16776960
data_int_16711935: .word 16711935
data_int_65535: .word 65535
data_int_13421772: .word 13421772
stackPointerStart: .word 4096
