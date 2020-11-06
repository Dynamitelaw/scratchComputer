.text
lui t0, 1 #t0 should have 1<<12 = 2^12 = 4096
addi zero, zero, 0
addi zero, zero, 0
#Test la
la ra, exit  #t1 should have PC + 1<<12 = 12 + 4096 = 4108
jr ra
addi t0, t0, 1
addi t0, t0, 1
addi t0, t0, 1
addi t0, t0, 1
addi t0, t0, 1
addi t0, t0, 1

rem 
exit:  
addi zero, zero, 0