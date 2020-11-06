//Import header
#include "standardLibrary/stdlib.h"


int main()
{
	int * pointer = malloc(4);

	*pointer = 42;

	return *pointer;
}