
int g_integerDeclare;

struct dummyStruct
{
	char dummyString[10];
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
	int temp = 5;
	struct Coordinate originPoint;
	originPoint.x = 0;
	originPoint.y = 0;
	originPoint.z = 0;

	struct Coordinate p1;
	p1.x = 3;
	p1.y = -4;
	p1.z = 5;

	int distanceSquared = (p1.x - originPoint.x)*(p1.x - originPoint.x) + (p1.y - originPoint.y)*(p1.y - originPoint.y) + (p1.z - originPoint.z)*(p1.z - originPoint.z);

	if (distanceSquared != 50) return -1;


	return 42;
}