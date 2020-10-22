struct arrayHolder
{
	int array[3][7][10];
};

int addThreeInts(int x, int y, int z)
{
	return y * z * 50;
}

#define COLUMNS 64
#define ROWS 48

#define FRAME_BUFFER_ADDRESS 4096