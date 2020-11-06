/*
Allocates size bytes of uninitialized storage.
If allocation succeeds, returns a pointer that is suitably aligned for any object type with fundamental alignment. 
*/
void * malloc(int size)
{
	//Ensure current gp is suitably aligned
	asm("addi t5, zero, 5");  //t5 = 5
	asm("bge a0, t5, ALIGN_WORD");  //if size > 4, then we need to word align gp

	asm("ALIGN_SUBWORD:");
	asm("rem t0, gp, a0"); //t0 = gp%size = alignmentOffset
	asm("add gp, gp, t0"); //gp = gp+alignmentOffset
	asm("j INCREMENT_GP");

	asm("ALIGN_WORD:");
	asm("addi t4, zero, 4"); //t4 = 4
	asm("rem t0, gp, t4"); //t0 = gp%size = alignmentOffset
	asm("add gp, gp, t0"); //gp = gp+alignmentOffset

	//Save current gp and increment next gp
	asm("INCREMENT_GP:");
	asm("mv t0, gp");  //t0 = address to return
	asm("add gp, gp, a0");  //increment gp by size
	asm("mv a0, t0");  //a0 = address to return
	asm("jr ra");  //return to caller
}