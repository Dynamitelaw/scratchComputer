// Jose Rubianes (jer2201)
// CS3157 Advanced Programming
// Lab 1: Part 1

/*
Here is long comment
Bing bing bong bong
*/

// \desc	Finds the Greatest Common Denominator of x and y
// 			via Euclid's algorithm

int globalInteger = 0;  //<TODO> Implement global variables

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

bool isPrime(int x)
{
	int k;
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


bool areCoprime(int x, int y)
{
	int gcd = greatestCommonDenominator(x, y);
	bool areCoprime;
	if (gcd == 1)
		areCoprime = true;
	else
		areCoprime = false;

	return areCoprime;
}

int addThreeInts(int x, int y, int z)
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
	*/ bool fakeVariable;
	bool isPrime_x;
	isPrime_x = isPrime(x);

	bool isPrime_y = isPrime(y);

	//Are x and y coprime?
	bool xYcoprime = areCoprime(x, y);

	if ((average == 42) && (isPrime_x))
	{
		if (!(isPrime_y))
		{
			//if (addThreeInts(21, 25, -4) == 42) return 42;  //<TODO> fix this
			return 42;
		}
	}

	return -1;
}