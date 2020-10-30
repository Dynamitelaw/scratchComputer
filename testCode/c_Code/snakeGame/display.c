#define COLUMNS 4 //64
#define ROWS 3 //48
#define FRAME_BUFFER_ADDRESS 4096

void updatePixel(int column, int row, int colorValue)
{
	int * pixelPointer = FRAME_BUFFER_ADDRESS + (row*COLUMNS) + column;
	*pixelPointer = colorValue;
}

void clearScreen(int colorValue)
{
	int * pixelPointer = FRAME_BUFFER_ADDRESS;

	for (int r=0; r<ROWS; r++)
	{
		for (int c=0; c<COLUMNS; c++)
		{
			*pixelPointer = colorValue;
			pixelPointer += 4;
		}
	}
}