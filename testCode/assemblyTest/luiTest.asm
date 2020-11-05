.text
lui t0, 1 #t0 should have 1<<12 = 2^12 = 4096
addi zero, zero, 0
addi zero, zero, 0
#Test auipc
auipc t1, 1  #t1 should have PC + 1<<12 = 12 + 4096 = 4108

exit:  
addi zero, zero, 0