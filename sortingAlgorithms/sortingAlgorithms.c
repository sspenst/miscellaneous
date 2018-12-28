#define _CRT_SECRUE_NO_WARNINGS

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define MAX_NUM 30000
#define LENGTH 20000
#define ALGORITHMS 4
#define TRIALS 5
#define ALGO_NAME 10

/* Functionality functions. */
void generateData(int[]);
void copyArrays(int[], int[][LENGTH]);
void displayRow(int[][LENGTH], int); // Isn't really necessary anymore.
void swap(int*, int*);
void averages(clock_t[][ALGORITHMS], double[]);
void minimum(double[], char[][ALGO_NAME]);
int verifyOrder(int[][LENGTH], int);

/* Sorting algorithms. */
void sortDirectory(int[][LENGTH], int);
void bubble(int[][LENGTH], int);
void selection(int[][LENGTH], int);
void insertion(int[][LENGTH], int);
void shell(int[][LENGTH], int);

int main(void) {
	/* All of the variables. They're not very organized. */
	char algoName[ALGORITHMS][ALGO_NAME] = { { "Bubble" }, { "Selection" }, { "Insertion" }, { "Shell" } };
	int origin[LENGTH];
	int data[ALGORITHMS][LENGTH];
	clock_t start_t, end_t;
	clock_t trials[TRIALS][ALGORITHMS];
	double average[ALGORITHMS] = { 0.0 };
	int verify;

	/* First row of text. */
	printf("         ");
	for (int i = 0; i < ALGORITHMS; i++)
		printf("%-10s", algoName[i]);
	printf("\n");

	/* Tests algorithms and prints results on the screen. */
	for (int trial = 0; trial < TRIALS; trial++) {
		generateData(origin);
		copyArrays(origin, data);

		printf("Trial %d: ", trial + 1);

		for (int algo = 0; algo < ALGORITHMS; algo++) {
			start_t = clock();
			sortDirectory(data, algo);
			end_t = clock();

			trials[trial][algo] = end_t - start_t;
			printf("%-10d", (int)trials[trial][algo]);

			verify = verifyOrder(data, algo);

			if (!verify) {
				printf("ERROR: Sorting algorithm bugged.");
				trial = TRIALS;
				break;
			}
		}
		printf("\n");
	}

	if (verify) {
		averages(trials, average);
		minimum(average, algoName);
	}

	return 0;
}

/* Generates an array containing no repeating numbers. */
void generateData(int data[]) {
	srand((unsigned)time(NULL));

	int flag;

	for (int i = 0; i < LENGTH; i++) {
		flag = 0;
		data[i] = rand() % MAX_NUM + 1;

		for (int j = 0; j < i; j++)
		if (data[j] == data[i])
			flag = 1;

		if (flag)
			i--;
	}
}

/* Copies the original array into a 2D array. */
void copyArrays(int origin[], int data[][LENGTH]) {
	for (int i = 0; i < ALGORITHMS; i++)
	for (int j = 0; j < LENGTH; j++)
		data[i][j] = origin[j];
}


/* Prints a row of a 2D array on the screen. */
void displayRow(int data[][LENGTH], int row) {
	for (int i = 0; i < LENGTH; i++)
		printf("%d ", data[row][i]);

	printf("\n");
}

/* Swaps two integers using call by reference. */
void swap(int *a, int *b) {
	int temp;

	temp = *b;
	*b = *a;
	*a = temp;
}

/* Prints the average of each algorithm's sorting time. */
void averages(clock_t trials[][ALGORITHMS], double average[]) {
	printf("Average: ");

	for (int i = 0; i < ALGORITHMS; i++) {
		for (int j = 0; j < TRIALS; j++) {
			average[i] += trials[j][i];
		}

		average[i] /= TRIALS;
		printf("%-10.0f", average[i]);
	}

	printf("\n");
}

/* Finds the shortest sorting time. */
void minimum(double data[], char algoName[][ALGO_NAME]) {
	int mindex = 0;

	for (int i = 1; i < ALGORITHMS; i++)
		if (data[i] < data[mindex])
			mindex = i;

	printf("\n%s averaged to be the fastest sorting algorithm\nwith an average sorting time of %.0f milliseconds.\n\n", algoName[mindex], data[mindex]);
}

int verifyOrder(int data[][LENGTH], int row) {
	int order = 1;

	for (int i = 1; i < LENGTH; i++) {
		if (data[row][i] < data[row][i - 1]) {
			order = 0;
			i = LENGTH;
		}
	}

	return order;
}

/**********************************
 ********SORTING ALGORITHMS********
 **********************************/

void sortDirectory(int data[][LENGTH], int algo) {
	if (algo == 0)
		bubble(data, algo);
	else if (algo == 1)
		selection(data, algo);
	else if (algo == 2)
		insertion(data, algo);
	else if (algo == 3)
		shell(data, algo);
}

void bubble(int data[][LENGTH], int row) {
	int sort = 1;
	int j = 0;

	while (sort) {
		sort = 0;
		j++;
		
		for (int i = 0; i < LENGTH - j; i++) {
			if (data[row][i] > data[row][i + 1]) {
				swap(&data[row][i], &data[row][i + 1]);
				sort = 1;
			}
		}
	}
}

void selection(int data[][LENGTH], int row) {
	int mindex;

	for (int i = 0; i < LENGTH - 1; i++) {
		mindex = i;

		for (int j = i + 1; j < LENGTH; j++)
			if (data[row][j] < data[row][mindex])
				mindex = j;

		if (mindex != i)
			swap(&data[row][i], &data[row][mindex]);
	}
}

void insertion(int data[][LENGTH], int row) {
	int j;

	for (int i = 1; i < LENGTH; i++) {
		j = i;

		while (j > 0 && data[row][j] < data[row][j - 1]) {
			swap(&data[row][j], &data[row][j - 1]);
			j--;
		}
	}
}
/*
void shell(int data[][LENGTH], int row) {
	int i, j, increment = 3, temp;

	while (increment > 0) {
		for (i = 0; i < LENGTH; i++) {
			j = i;
			temp = data[row][i];

			while ((j >= increment) && (data[row][j - increment] > temp)) {
				data[row][j] = data[row][j - increment];
				j -= increment;
			}

			data[row][j] = temp;
		}
		if (increment / 2 != 0)
			increment = increment / 2;
		else if (increment == 1)
			increment = 0;
		else
			increment = 1;
	}
}
*/

void shell(int data[][LENGTH], int row) {
	for (int gap = LENGTH / 2; gap > 0; gap /= 2)
		for (int i = gap; i < LENGTH; i++)
			for (int j = i - gap; j >= 0 && data[row][j] > data[row][j + gap]; j -= gap)
				swap(&data[row][j], &data[row][j + gap]);
}
