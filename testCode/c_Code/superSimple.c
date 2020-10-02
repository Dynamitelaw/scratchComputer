
int addThreeInts(int x, int y, int z)
{
	return x + y + z;  //comment here
}


int main()
{
	int x = 6;	//tabbed comment
	int y = 77;
	int z = 1;

	int k = addThreeInts(x, y, z);

	int i = 7;
	int * j;
	j = &i;
	if (*j != 7) return -1;

	*j = 1;
	if (*j != 1) return -1;

	*j += 7;
	if (*j != 8) return -1;

	//int k = *j;  //<TODO> fix this
	//if (k != 8) return -1;


	if (k == 84)
	{
		return 42;
	}

	return -1;
}