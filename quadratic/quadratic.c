/* Header files */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

/* Global variables */
int SIGN = 1;
int SIDE = 1;
int num[3] = { 0 };
char var = '.';

/* Function prototypes */
void analyze(char*);
int isletter(char);

/* Solves an expanded, unsimplified quadratic equation
   and outputs the answer(s) */
int main(int argc, char** argv) {
	int start;
	char* curr;
	
	/* Check every string inputted */
	for	(int i = 1; i < argc; i++) {
		start = 0;
		curr = (char*)malloc(sizeof(char)*(strlen(argv[i]) + 1));
		
		/* Check every character in the string */
		for (int j = 0; j < strlen(argv[i]); j++) {
			/* Split the string if there is an operator in it */
			if (argv[i][j] == '+' || argv[i][j] == '-' || argv[i][j] == '=') {
				curr[j] = '\0';
				analyze(curr + start);
				curr[j] = argv[i][j];
				curr[j+1] = '\0';
				analyze(curr + j);
				start = j + 1;
			}
			else {
				curr[j] = argv[i][j];
			}
		}
		
		if (start != strlen(argv[i])) {
			curr[strlen(argv[i])] = '\0';
			analyze(curr + start);
		}
		
		free(curr);
		curr = NULL;
	}
	
	/* Output the answer */
	if (num[2] == 0) {
		printf("%c = %.4g\n", var, num[0] * -1.0 / num[1]);
	}
	else {
		double temp = num[1] * num[1] - 4 * num[2] * num[0];
		
		/* Print here if the answer is imaginary */
		if (temp < 0) {
			double x1 = num[1] * -1.0 / (2 * num[2]);
			double x2 = fabs(sqrt(temp * -1.0) / (2 * num[2]));
			if (x1 == 0) {
				if (x2 == 1)
					printf("%c = -i, i\n", var);
				else
					printf("%c = -%.4gi, %.4gi\n", var, x2, x2);
			}
			else {
				if (x2 == 1)
					printf("%c = %.4g - i, %.4g + i\n", var, x1, x1);
				else
					printf("%c = %.4g - %.4gi, %.4g + %.4gi\n", var, x1, x2, x1, x2);
			}
		}
		else {
			double x1 = (num[1] * -1.0 - sqrt(temp)) / (2 * num[2]);
			double x2 = (num[1] * -1.0 + sqrt(temp)) / (2 * num[2]);
			if (x1 == x2)
				printf("%c = %.4g\n", var, x1);
			else
				printf("%c = %.4g, %.4g\n", var, x1, x2);
		}
	}
	
	return 0;
}

/* Analyzes the given string segment and records appropriate data about it */
void analyze(char* str) {
	/* Return if the string is empty */
	if (strcmp(str, "") == 0)
		return;
	/* Change sign depending on operator */
	else if (strcmp(str, "+") == 0)
		SIGN = 1;
	else if (strcmp(str, "-") == 0)
		SIGN = -1;
	else if (strcmp(str, "=") == 0) {
		SIDE = -1;
		SIGN = 1;
	}
	else {
		/* Deal with the quadratic variable */
		if (strstr(str, "^2") != NULL) {
			/* Make sure the variable is correct */
			if (var == '.')
				var = str[strlen(str) - 3];
			else if (str[strlen(str) - 3] != var) {
				printf("Please enter only one variable.\n");
				exit(0);
			}
			
			str[strlen(str) - 3] = '\0';
			if (strcmp(str, "") == 0)
				num[2] += SIGN * SIDE * 1;
			else
				num[2] += SIGN * SIDE * strtol(str, NULL, 10);
		}
		/* Deal with the linear variable */
		else if (isletter(str[strlen(str) - 1])) {
			/* Make sure the variable is correct */
			if (var == '.')
				var = str[strlen(str) - 1];
			else if (str[strlen(str) - 1] != var) {
				printf("Please enter only one variable.\n");
				exit(0);
			}
			
			str[strlen(str) - 1] = '\0';
			if (strcmp(str, "") == 0)
				num[1] += SIGN * SIDE * 1;
			else
				num[1] += SIGN * SIDE * strtol(str, NULL, 10);
		}
		/* Deal with the constants */
		else {
			num[0] += SIGN * SIDE * strtol(str, NULL, 10);
		}
	}
}

/* Returns if the given character is an integer */
int isletter(char let) {
	return (let >= 'A' && let <= 'Z') || (let >= 'a' && let <= 'z');
}