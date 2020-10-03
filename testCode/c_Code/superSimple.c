
int addThreeInts(int x, int y, int z)
{
	return x + y + z;  //comment here
}


int main()
{
	int twoD_array[5][3];
	
	int arrayLength = 10;
	int x_array[10];
	int y_array[10] = {0,1,2,3,4,5,6,7,8,9};


	for (int i=0; i<arrayLength; i++)
	{
		x[i] = i;
	}

	int xElement;
	int yElement;
	int sumArray[10];
	for (int i=0; i<arrayLength; i++)
	{
		xElement = x[i];
		yElement = y[i];

		if (xElement != i) return -1;
		if (yElement != i) return -1;
		sumArray[i] = xElement + yElement;
	}

	int sumElement;
	for (int i=0; i<arrayLength; i++)
	{
		sumElement = sumArray[i];

		if (sumElement != i*i) return -1;
	}


	return 42;
}