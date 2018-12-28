#define _CRT_SECURE_NO_WARNINGS

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <DAQlib.h>
#include <conio.h> /* _getch() and _khbit() */
#include <Windows.h>

#define TRUE 1
#define FALSE 0

#define ON 1
#define OFF 0

int reflex(void);

int main(void) {
	int setupNum, play = 1, best = 0, attempt, trial = 1;
	char guess = 1;

	printf("Enter configuration type (0 for the device or 6 for the simulator): ");
	scanf("%d", &setupNum);

	if (setupDAQ(setupNum) == TRUE) {
		printf("\nTHE REFLEX GAME\n\nHow to play:\nAfter a few seconds, a random LED will light up on the screen.\n");
		printf("Your goal is to press the number on the keyboard (1-4) that\ncorresponds with the LED that has been lit up.\n");
		printf("When pressing the corresponding key, make sure the console window is\nin front, and not the DAQ window. ");
		printf("The game won't be able to\ntell that you've pressed a key if the DAQ window is in front.\n\n");

		while (play && continueSuperLoop() == TRUE) {
			printf("Press 's' to start or 'q' to quit...\n");

			while (guess && continueSuperLoop() == TRUE) {
				if (_kbhit()) {
					guess = _getch();

					if (guess == 's') {
						attempt = reflex();

						if (attempt == 0) {
						}
						else if (best == 0)
							best = attempt;
						else if (attempt < best)
							best = attempt;

						guess = NULL;
						trial++;
					}
					else if (guess == 'q') {
						play = 0;
						guess = NULL;
					}
				}
			}

			guess = 1;
		}

		if (trial != 1 && best != 0) {
			printf("\nYour fastest reaction time was %d milliseconds.\n", best);
			printf("Thank you for playing!\n\n");
		}
	}
	else
		printf("ERROR: Cannot initialize system.\n");

	system("PAUSE");
	return 0;
}

int reflex(void) {
	clock_t start_t, end_t, total_t;
	char guess = 1;
	int pause, answer, correct;

	printf("Get ready to react...\n\n");
	guess = 1;

	srand((unsigned)time(NULL));

	/* Sleep for some length of time between 3.000 and 4.500 seconds. */
	pause = rand() % 1501 + 3000;
	Sleep(pause);

	/* Turn on a random LED. */
	answer = rand() % 4;
	digitalWrite(answer, ON);
	start_t = clock();

	while (guess && continueSuperLoop() == TRUE) {
		if (_kbhit()) {
			guess = _getch();

			if (guess == answer + 49) {
				correct = 1;
				end_t = clock();
				digitalWrite(answer, OFF);
				guess = NULL;
			}
			else {
				correct = 0;
				end_t = clock();
				digitalWrite(answer, OFF);
				guess = NULL;
				printf("You pressed the wrong key!\n");
			}
		}
	}

	if (correct) {
		total_t = end_t - start_t;
		printf("Reaction time: %d milliseconds.\n", total_t);
		return total_t;
	}
}