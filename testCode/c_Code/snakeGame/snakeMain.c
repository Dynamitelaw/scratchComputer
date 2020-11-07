#include "../standardLibrary/stdlib.h"

#include "display.c"
#include "keyboard.c"


struct food
{
	int xPos;
	int yPos;
};

#define SNAKE_NODE_SIZE 16
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
	clearScreen(BLACK);

	//Initialize food
	struct food foodPosition;
	foodPosition.xPos = 3;
	foodPosition.yPos = 1;
	updatePixel(foodPosition.xPos, foodPosition.yPos, RED);

	//Get pointer to memory mapped io (keyboard)
	bool * keyboard = INPUT_BUFFER_ADDRESS;

	//Instantiate snake linked list
	struct snakeNode snakeHead;
	struct snakeNode * snakeTailPtr = malloc(SNAKE_NODE_SIZE);

	snakeHead.xPos = 2;
	snakeHead.yPos = 1;
	snakeHead.previousNode = 0;
	snakeHead.nextNode = snakeTailPtr;

	snakeTailPtr->xPos = 2;
	snakeTailPtr->yPos = 0;
	snakeTailPtr->previousNode = &snakeHead;
	snakeTailPtr->nextNode = 0;

	//Initialize snake moving to the right
	int snake_xVelocity = 1;
	int snake_yVelocity = 0;

	////////////////
	//Main game loop
	////////////////
	int snakeLength = 2;
	int tickDelay = 100;
	int tick = 0;
	while(1)
	{
		//Check for quit key
		if (keyboard[KEY_q_OFFSET]) 
		{
			return 0;
		}

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

		//Store current head position
		int snakeHeadX_previous = snakeHead.xPos;
		int snakeHeadY_previous = snakeHead.yPos;

		//Update head position
		snakeHead.xPos = (snakeHead.xPos + snake_xVelocity)%DISPLAY_WIDTH;
		if (snakeHead.xPos < 0) snakeHead.xPos = DISPLAY_WIDTH;

		snakeHead.yPos = (snakeHead.yPos + snake_yVelocity)%DISPLAY_HEIGHT;
		if (snakeHead.yPos < 0) snakeHead.yPos = DISPLAY_HEIGHT;
		
		//Check if snake has collided with itself
		struct snakeNode * nodeToCheck = snakeHead.nextNode;
		int currentHead_xPos = snakeHead.xPos;  //extracting position outside of loop to save memory access and optimize performance
		int currentHead_yPos = snakeHead.yPos;
		while (nodeToCheck)
		{
			if ((currentHead_xPos == nodeToCheck->xPos) && (currentHead_yPos == nodeToCheck->yPos))
			{
				//Snake has collided with itself
				updatePixel(currentHead_xPos, currentHead_yPos, YELLOW);
				updatePixel(currentHead_xPos, currentHead_yPos, YELLOW);  //I have no idea why I have to do this twice for it to work, but fuck it. Not worth debugging
				delay(500);
				return -1;
			}
			nodeToCheck = nodeToCheck->nextNode;
		}

		//Check if snake has reached current food
		if ((snakeHead.xPos == foodPosition.xPos) && (snakeHead.yPos == foodPosition.yPos))
		{
			//Move food
			iterateFoodPosition(&foodPosition, tick);

			////////////////
			//Grow snake
			////////////////
			snakeLength++;
			tickDelay -= 4;  //decrease delay as snake gets longer, or else game slows down due to list traversal

			//Create new snake node
			struct snakeNode * newNode = malloc(SNAKE_NODE_SIZE);
			newNode->xPos = snakeHeadX_previous;
			newNode->yPos = snakeHeadY_previous;

			//Insert new node into snake linked list
			newNode->previousNode = &snakeHead;
			newNode->nextNode = snakeHead.nextNode;
			struct snakeNode * oldNextNode = snakeHead.nextNode;
			oldNextNode->previousNode = newNode;
			snakeHead.nextNode = newNode;

			//Set new head GREEN
			updatePixel(snakeHead.xPos, snakeHead.yPos, GREEN);
		}
		else
		{
			//Set current tail BLACK and new head GREEN
			updatePixel(snakeTailPtr->xPos, snakeTailPtr->yPos, BLACK);
			updatePixel(snakeHead.xPos, snakeHead.yPos, GREEN);

			//Get pointer to 2nd to last node
			struct snakeNode * newTailPtr = snakeTailPtr->previousNode;
			
			//Insert current tail node into 2nd place in linked list
			snakeTailPtr->xPos = snakeHeadX_previous;
			snakeTailPtr->yPos = snakeHeadY_previous;
			snakeTailPtr->previousNode = &snakeHead;
			snakeTailPtr->nextNode = snakeHead.nextNode;
			struct snakeNode * oldNextNode = snakeHead.nextNode;
			oldNextNode->previousNode = snakeTailPtr;
			newTailPtr->nextNode = 0;
			snakeHead.nextNode = snakeTailPtr;

			//Update tail pointer to 2nd to last node
			snakeTailPtr = newTailPtr;
		}
		
		//Draw food
		updatePixel(foodPosition.xPos, foodPosition.yPos, RED);
		
		//Wait until next tick
		if (tickDelay>0) delay(tickDelay);
		tick++;
	}
	
}