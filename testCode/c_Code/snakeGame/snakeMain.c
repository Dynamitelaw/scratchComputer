//Import header
#include "../standardLibrary/stdlib.h"

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
	int * previousNode;
	int * nextNode;
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

	//Initialize food
	struct food foodPosition;
	foodPosition.xPos = 8;
	foodPosition.yPos = 4;
	updatePixel(foodPosition.xPos, foodPosition.yPos, RED);

	//Get pointer to memory mapped io (keyboard)
	bool * keyboard = INPUT_BUFFER_ADDRESS;

	//Instantiate snake
	struct snakeNode snakeHead;
	struct snakeNode snakeTail;

	snakeHead.xPos = 2;
	snakeHead.yPos = 1;
	snakeHead.previousNode = 0;
	snakeHead.nextNode = &snakeTail;

	snakeTail.xPos = 2;
	snakeTail.yPos = 1;
	snakeTail.previousNode = &snakeHead;
	snakeTail.nextNode = 0;

	int snake_xVelocity = 0;
	int snake_yVelocity = 0;

	//Main game loop
	for (int i=0; i<60; i++)
	{
		//Update snake velocity by checking for arrow key status
		if (keyboard[KEY_UP_OFFSET]) 
		{
			snake_xVelocity = 0;
			snake_yVelocity = -1;
		}
		if (keyboard[KEY_DOWN_OFFSET])
		{
			snake_xVelocity = 0;
			snake_yVelocity = 1;
		}
		if (keyboard[KEY_LEFT_OFFSET])
		{
			snake_xVelocity = -1;
			snake_yVelocity = 0;
		}
		if (keyboard[KEY_RIGHT_OFFSET])
		{
			snake_xVelocity = 1;
			snake_yVelocity = 0;
		}

		//Update snake position
		snakeHead.xPos = (snakeHead.xPos + snake_xVelocity)%DISPLAY_WIDTH;
		if (snakeHead.xPos < 0) snakeHead.xPos = DISPLAY_WIDTH;

		snakeHead.yPos = (snakeHead.yPos + snake_yVelocity)%DISPLAY_HEIGHT;
		if (snakeHead.yPos < 0) snakeHead.yPos = DISPLAY_HEIGHT;

		updatePixel(snakeTail.xPos, snakeTail.yPos, BLACK);
		updatePixel(snakeHead.xPos, snakeHead.yPos, GREEN);
		snakeTail.xPos = snakeHead.xPos;
		snakeTail.yPos = snakeHead.yPos;
		
		
		//Move food if snake has reached current food
		if ((snakeHead.xPos == foodPosition.xPos) && (snakeHead.yPos == foodPosition.yPos))
		{
			iterateFoodPosition(&foodPosition, i);
		}
		
		updatePixel(foodPosition.xPos, foodPosition.yPos, RED);
		
		delay(400);
		
		//Clear previous food position
		//updatePixel(oldX, oldY, BLACK);
	}
	
}