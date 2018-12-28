#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define MAX_NUM 100
#define MAX_ATTEMPTS 5
#define TRUE 1
#define FALSE 0

int getSecretNumber(int);
int getGuess(int);
int checkGuess(int, int);

int main(void) {
	int secretNum;
	int guess;
	int attemptsRemaining = MAX_ATTEMPTS;
	int gotIt = FALSE;

	srand((unsigned)time(NULL));

	secretNum = getSecretNumber(MAX_NUM);

	printf("The guessing game!\nGuess a number between 1 and 100.\n\n");

	while (attemptsRemaining > 0 && gotIt == FALSE) {
		guess = getGuess(attemptsRemaining);
		gotIt = checkGuess(guess, secretNum);
		attemptsRemaining--;
	}

	if (gotIt)
		printf("Congratulations!\n");
	else {
		printf("Sorry, you have no guesses remaining...\n");
		printf("The secret number was %d\n", secretNum);
	}

	return 0;
}

int getSecretNumber(int maxNum) {
	return rand() % maxNum + 1;
}

int getGuess(int attemptsRemaining) {
	int guess;

	printf("You have %d guesses remaining...\n", attemptsRemaining);
	printf("Enter your guess: ");
	scanf("%d", &guess);

	return guess;
}

int checkGuess(int guess, int secretNum) {
	if (guess < secretNum) {
		printf("Your guess is too low...\n\n");
		return FALSE;
	}
	else if (guess > secretNum) {
		printf("Your guess is too high...\n\n");
		return FALSE;
	}
	else {
		printf("You got it!\n\n");
		return TRUE;
	}
}
