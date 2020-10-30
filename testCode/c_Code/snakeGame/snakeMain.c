//Import header
#include "display.c"

struct cursor
{
	int xPos;
	int yPos;
};


int main()
{
	int colorArray[8] = {
		16711680, //red
		65280, //green
		255, //blue
		16776960, //yellow
		16711935, //magenta
		65535, //cyan
		13421772, //grey
		0 //black
	};

	for (int animateIter=0; animateIter<8; animateIter++)
	{
		clearScreen(colorArray[animateIter]);
	}

	return 42;
}