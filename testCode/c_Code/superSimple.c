int addThreeInts(int x, int y, int z)
{
	return x + y + z;
}

int main()
{
	int x = 6;
	int y = 77;
	int z = 1;

	int k = addThreeInts(x, y, z);

	if (k == 84)
	{
		return 42;
	}

	return -1;
}