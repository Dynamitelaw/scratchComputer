// Jose Rubianes (jer2201)
// CS3157 Advanced Programming
// Lab 1: Part 1

/*
Here is long comment
Bing bing bong bong
*/

// \desc	Finds the Greatest Common Denominator of x and y
// 			via Euclid's algorithm

int globalInteger = 0;

int greatestCommonDenominator(int x, int y)
{
	if (x == 0)
	{
		//Remainder of modulo is 0 -> y is GCD
		return y;
	}

	else
	{
		return greatestCommonDenominator(y % x, x);
	}
}

unsigned char isPrime(int x)
{
	for (int i=2; i<x; i++)
	{
		if ((x % i) == 0)
			return false;
	}

	return true;
}


int getAverage(int x, int y)
{
	int average = (x + y) / 2;

	return average;
}


unsigned char areCoprime(int x, int y)
{
	int gcd = greatestCommonDenominator(x, y);
	unsigned char areCoprime;
	if (gcd == 1)
		areCoprime = true;
	else
		areCoprime = false;

	return areCoprime;
}

void addThreeInts(int x, int y, int z)
{
	return x + y + z;
}

int main()
{
	//Initialize x and y
	int x = 7;
	int y = 77;

	//Get average of x and y
	int average = getAverage(x,y);

	/*
	Find out if x and y are prime
	*/ unsigned char fakeVariable;
	unsigned char isPrime_x;
	isPrime_x = isPrime(x);

	unsigned char isPrime_y = isPrime(y);

	//Are x and y copime?
	unsigned char xYcoprime = areCoprime(x, y);

	if ((average == 42) && (isPrime_x))
	{
		if (!(isPrime_y)) return -1;
	}

	return 0;
}