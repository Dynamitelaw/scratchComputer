//Import header
#include "display.c"
#include "keyboard.c"

struct food
{
	int xPos;
	int yPos;
};

struct snakeNode
{
	int xPos;
	int yPos;
};

struct snake
{
	struct snakeNode head;
	struct snakeNode tail;
};

int delay(int iterations)
{
	int counter=0;
	for (int i=0; i<iterations; i++)
	{
		counter++;
	}

	return counter;
}

void iterateFoodPosition(struct food * foodPosition, int iterator)
{
	int currentX = foodPosition->xPos;
	int currentY = foodPosition->yPos;

	int nextX = (currentX*3 + currentY*7 + iterator*5)%COLUMNS;
	int nextY = (currentX*2 + currentY*11 + iterator*3)%ROWS;

	foodPosition->xPos = nextX;
	foodPosition->yPos = nextY;
}


int main()
{
	//Clear screen to black
	//clearScreen(BLACK);

	/*
	//Initialize food
	struct food foodPosition;
	foodPosition.xPos = 8;
	foodPosition.yPos = 4;
	updatePixel(foodPosition.xPos, foodPosition.yPos, RED);

	//Iterate food position 
	int oldX;
	int oldY;

	for (int i=0; i<10; i++)
	{
		//Get current position
		oldX = foodPosition.xPos;
		oldY = foodPosition.yPos;

		//Set color of new food position
		iterateFoodPosition(&foodPosition, i);
		updatePixel(foodPosition.xPos, foodPosition.yPos, RED);

		delay(400);
		
		//Clear previous food position
		updatePixel(oldX, oldY, BLACK);
	}

	return 42;
	*/

	/*
	int colorArray[6] = {
		16711680, //reg
		65280, //green
		255, //blue
		16776960, //yellow
		16711935, //magenta
		65535 //cyan
	};

	bool * keyboard = INPUT_BUFFER_ADDRESS;
	int colorIndex = 0;

	for (int i=0; i<30; i++)
	{
		for (int keyIndex=0; keyIndex<INPUT_BUFFER_SIZE; keyIndex++)
		{
			if(keyboard[keyIndex])
			{
				//colorIndex = keyIndex%6;
				updatePixel(keyIndex, 0, RED);
			}
			else
			{
				updatePixel(keyIndex, 0, BLACK);
			}
		}
		delay(100);
	}
	*/
	/*
	bool * keyboard = INPUT_BUFFER_ADDRESS;
	int colorIndex = 0;

	for (int i=0; i<4; i++)
	{
		for (int keyIndex=0; keyIndex<INPUT_BUFFER_SIZE; keyIndex++)
		{
			if(keyboard[KEY_w_OFFSET])
			{
				//colorIndex = keyIndex%6;
				updatePixel(keyIndex, 0, RED);
			}
			else
			{
				updatePixel(keyIndex, 0, BLACK);
			}
		}
		//delay(100);
	}
	*/
	
	//Clear screen to black
	clearScreen(BLACK);

	//Initialize food
	struct food foodPosition;
	foodPosition.xPos = 8;
	foodPosition.yPos = 4;
	updatePixel(foodPosition.xPos, foodPosition.yPos, RED);

	bool * keyboard = INPUT_BUFFER_ADDRESS;
	int oldX;
	int oldY;

	for (int i=0; i<30; i++)
	{
		//Get current position
		oldX = foodPosition.xPos;
		oldY = foodPosition.yPos;

		//Move food by checking for WASD key status
		if (keyboard[KEY_UP_OFFSET]) foodPosition.yPos = (oldY-1)%ROWS;
		if (keyboard[KEY_DOWN_OFFSET]) foodPosition.yPos = (oldY+1)%ROWS;
		if (keyboard[KEY_LEFT_OFFSET]) foodPosition.xPos = (oldX-1)%COLUMNS;
		if (keyboard[KEY_RIGHT_OFFSET]) foodPosition.xPos = (oldX+1)%COLUMNS;
		
		//Set color of new food position
		updatePixel(foodPosition.xPos, foodPosition.yPos, RED);

		delay(400);
		
		//Clear previous food position
		updatePixel(oldX, oldY, BLACK);
	}
	
}