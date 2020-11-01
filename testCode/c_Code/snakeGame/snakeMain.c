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

struct snakeStruct
{
	struct snakeNode head;
	struct snakeNode tail;
	char xVelocity;
	char yVelocity;
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

	int nextX = (currentX*3 + currentY*7 + iterator*5)%DISPLAY_WIDTH;
	int nextY = (currentX*2 + currentY*11 + iterator*3)%DISPLAY_HEIGHT;

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
	//clearScreen(BLACK);

	//Initialize food
	struct food foodPosition;
	foodPosition.xPos = 8;
	foodPosition.yPos = 4;
	updatePixel(foodPosition.xPos, foodPosition.yPos, RED);

	//Get pointer to moery mapped io (keyboard)
	bool * keyboard = INPUT_BUFFER_ADDRESS;

	//Instantiate snake
	struct snakeStruct snake;
	snake.head.xPos = 2;
	snake.head.yPos = 1;
	snake.tail.xPos = 2;
	snake.tail.yPos = 1;
	snake.xVelocity = 0;
	snake.yVelocity = 0;

	int foodCurrentX;
	int foodCurrentY;
	int foodIterator = 0;
	for (int i=0; i<6; i++)
	{
		//Get current food position
		foodCurrentX = foodPosition.xPos;
		foodCurrentY = foodPosition.yPos;

		//Update snake velocity by checking for arrow key status
		if (keyboard[KEY_UP_OFFSET]) 
		{
			snake.xVelocity = 0;
			snake.yVelocity = -1;
		}
		if (keyboard[KEY_DOWN_OFFSET])
		{
			snake.xVelocity = 0;
			snake.yVelocity = 1;
		}
		if (keyboard[KEY_LEFT_OFFSET])
		{
			snake.xVelocity = -1;
			snake.yVelocity = 0;
		}
		if (keyboard[KEY_RIGHT_OFFSET])
		{
			snake.xVelocity = 1;
			snake.yVelocity = 0;
		}

		//Update snake position
		snake.head.xPos = (snake.head.xPos + snake.xVelocity)%DISPLAY_WIDTH;
		//snake.head.xPos = 8;
		//if (snake.head.xPos < 0) snake.head.yPos = 10;
		snake.head.yPos = (snake.head.yPos + snake.yVelocity)%DISPLAY_HEIGHT;
		if (snake.head.yPos < 0) snake.head.yPos = DISPLAY_HEIGHT;
		//snake.head.yPos = 10;
		updatePixel(snake.tail.xPos, snake.tail.yPos, BLACK);
		//delay(400);
		updatePixel(snake.head.xPos, snake.head.yPos, GREEN);
		snake.tail.xPos = snake.head.xPos;
		snake.tail.yPos = snake.head.yPos;
		
		
		//Move food if snake has reached current food
		if ((snake.head.xPos == foodPosition.xPos) && (snake.head.yPos == foodPosition.yPos))
		{
			iterateFoodPosition(&foodPosition, i);
			foodIterator++;
		}
		
		updatePixel(foodPosition.xPos, foodPosition.yPos, RED);
		
		delay(4);
		
		//Clear previous food position
		//updatePixel(oldX, oldY, BLACK);
	}
	
}