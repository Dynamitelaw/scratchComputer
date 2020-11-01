//Screen size and memory location
#define DISPLAY_WIDTH 16 //64
#define DISPLAY_HEIGHT 12 //48
#define FRAME_BUFFER_ADDRESS 4096

//Primary colors
#define RED 16711680
#define GREEN 65280
#define BLUE 255
#define YELLOW 16776960
#define MAGENTA 16711935
#define CYAN 65535
#define GREY 13421772
#define BLACK 0

void updatePixel(int column, int row, int colorValue)
{
	int * pixelPointer = FRAME_BUFFER_ADDRESS + 4*((row*DISPLAY_WIDTH) + column);
	*pixelPointer = colorValue;
}

void clearScreen(int colorValue)
{
	int * pixelPointer = FRAME_BUFFER_ADDRESS;

	for (int r=0; r<DISPLAY_HEIGHT; r++)
	{
		for (int c=0; c<DISPLAY_WIDTH; c++)
		{
			*pixelPointer = colorValue;
			pixelPointer += 4;
		}
	}
}