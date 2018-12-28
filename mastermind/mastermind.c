#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>

/*
 * 0 = r = red
 * 1 = o = orange
 * 2 = y = yellow
 * 3 = g = green
 * 4 = b = blue
 * 5 = p = purple
 * 6 = m = magenta
 * 7 = w = white
 * 
 */

void game(void);
void solve(void);

int main(int argc, char** argv) {
	srand(time(NULL));
	
	if (argc != 2) {
		printf("Argument options:\n1 - Play against the computer\n");
		printf("2 - Let the computer tell you your next move\n");
		exit(0);
	}
	
	long mode = strtol(argv[1], 0, 0);	
	
	if (mode == 1)
		game();
	else if (mode == 2) {
		printf("This option is not yet implemented\n");
		return 0;
		//solve();
	}
	else
		printf("Invalid option chosen.\n");
	
	return 0;
}

void game() {
	char keys[] = {'r', 'o', 'y', 'g', 'b', 'p', 'm', 'w'};
	char ans[5];
	ans[4] = '\0';
	char guess[5] = "0000";
	int guessNum = 0;
	int match[4] = { 0 };
	int red = 0;
	int white = 0;
	
	for (int i = 0; i < 4; i++) {
		ans[i] = keys[rand() % 8];
	}
	
	printf("\nGuess by typing four letters and pressing enter.\n\n");
	printf("Use the following letters:\n");
	printf("r = red\no = orange\ny = yellow\ng = green\n");
	printf("b = blue\np = purple\nm = magenta\nw = white\n\n");
	
	while (1) {
		guessNum++;
		printf("Guess %d: ", guessNum);
		scanf("%s", guess);
		
		if (strcmp(ans, guess) == 0) {
			printf("You guessed correctly!\n");
			break;
		}
		else {
			red = 0;
			white = 0;
			
			for (int i = 0; i < 4; i++) {
				if (guess[i] == ans[i]) {
					match[i] = 1;
					red++;
				}
				else
					match[i] = 0;
			}
			
			for (int i = 0; i < 4; i++) {
				if (match[i] != 1) {
					for (int j = 0; j < 4; j++) {
						if (match[j] == 0 && guess[i] == ans[j]) {
							match[j] = 2;
							white++;
							break;
						}
					}
				}
			}
			
			printf("Red pegs: %d\nWhite pegs: %d\n\n", red, white);
		}
	}
}

/*void solve() {
	int codes[4096] = { 0 };
	char keys[] = {'r', 'o', 'y', 'g', 'b', 'p', 'm', 'w'};
	int guessNum = 0;
	char guess[5];
	int red;
	int white;
	
	printf("\nInput your turn by typing your four letter guess and the number of red and white pegs.\n\n");
	printf("Use the following letters:\n");
	printf("r = red\no = orange\ny = yellow\ng = green\n");
	printf("b = blue\np = purple\nm = magenta\nw = white\n\n");
	printf("Example entry: royg 1 1\n\n");
	
	while (1) {
		guessNum++;
		printf("Turn %d: ");
		scanf("%s %d %d", guess, &red, &white);
	}
}*/
