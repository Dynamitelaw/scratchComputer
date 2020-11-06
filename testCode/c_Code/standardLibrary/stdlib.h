/*
Allocates size bytes of uninitialized storage.
If allocation succeeds, returns a pointer that is suitably aligned for any object type with fundamental alignment. 
*/
void * malloc(int size)
{
	//Ensure current gp is suitably aligned
	asm("rem t0, gp, a0"); //t0 = gp%size = alignmentOffset
	asm("add gp, gp, t0"); //gp = gp+alignmentOffset

	//Save current gp and increment next gp
	asm("mv t0, gp");  //t0 = address to return
	asm("add gp, gp, a0");  //increment gp by size
	asm("mv a0, t0");  //a0 = address to return
	asm("jr ra");  //return to caller
}