
struct arrayHolder
{
	int array[3][7][10];
};

int main()
{
	int columns = 10;
	int rows = 7;
	int height = 3;

	struct arrayHolder holder;
	//int array[3][7][10];

	for (int h=0; h<height; h++)
	{
		for (int r=0; r<rows; r++)
		{
			for (int c=0; c<columns; c++)
			{
				holder.array[h][r][c] = h + r + c;
			}
		}
	}

	for (int h=0; h<height; h++)
	{
		for (int r=0; r<rows; r++)
		{
			for (int c=0; c<columns; c++)
			{
				int element = holder.array[h][r][c];
				if (element != h+r+c) return -1;
			}
		}	
	}

	return 42;
}