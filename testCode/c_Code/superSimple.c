
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

	int i = 0;
	while (i < 3)
	{
		i ++;
	}

	if (k == 84)
	{
		if (i == 3)	return 42;
	}

	return -1;
}