//Import header
#include "simplerHeader.h"


int main()
{
	int * pixelPointer = FRAME_BUFFER_ADDRESS;
	int columns = COLUMNS;
	int rows = ROWS;

	
	int colorArray[8] = {
		16711680, //reg
		65280, //green
		255, //blue
		16776960, //yellow
		16711935, //magenta
		65535, //cyan
		13421772, //grey
		0 //black
	};

	for (int animateIter=0; animateIter<5; animateIter++)
	{
		for (int r=0; r<rows; r++)
		{
			for (int c=0; c<columns; c++)
			{
				*pixelPointer = colorArray[(r*columns + c + animateIter)%8];
				pixelPointer += 4;
			}
		}
		pixelPointer = FRAME_BUFFER_ADDRESS;
	}

	return 42;
}