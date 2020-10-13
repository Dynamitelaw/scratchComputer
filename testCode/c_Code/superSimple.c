//Import header
#include "simplerHeader.h"


int main()
{
	int columns = COLUMNS;
	int rows = ROWS;
	int height = HEIGHT;

	struct arrayHolder holder;
	//int array[3][7][10];

	for (int h=0; h<height; h++)
	{
		for (int r=0; r<rows; r++)
		{
			for (int c=0; c<columns; c++)
			{
				holder.array[h][r][c] = addThreeInts(h, r, c);
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