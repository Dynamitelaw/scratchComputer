
int g_integerDeclare;

struct tempStruct
{
	int tertiaryInt;
};


struct dummyStruct
{
	char dummyString[10];
	int k;
	struct tempStruct subName;
};

struct Coordinate
{
	int x;
	int y;
	unsigned char c;
	int z;
	struct dummyStruct name;
};

// int getDistanceSquared(struct * p1, struct * p2)
// {

// }

int main()
{
	int temp = -5;
	struct Coordinate originPoint;
	originPoint.x = 0;
	originPoint.y = 0;
	originPoint.z = 0;

	struct Coordinate p1;
	p1.x = 3;
	p1.y = -4;
	p1.z = 5;

	int xDiff = p1.x - originPoint.x;
	int yDiff = p1.y - originPoint.y;
	int zDiff = p1.z - originPoint.z;
	int distanceSquared = xDiff*xDiff + yDiff*yDiff + zDiff*zDiff;

	if (distanceSquared != 50) return -1;

	p1.name.subName.tertiaryInt = 73;
	p1.name.subName.tertiaryInt += 2;
	int k = p1.name.subName.tertiaryInt / 3;
	if (k != 25) return -1;

	return 42;
}