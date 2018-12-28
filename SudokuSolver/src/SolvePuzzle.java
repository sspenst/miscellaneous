import java.util.ArrayList;
import java.util.BitSet;
import java.util.List;

public class SolvePuzzle {
	public int[][] puzzle = new int[Globals.SIZE][Globals.SIZE];
	private boolean oneSquare = false;
	private boolean noGuess = true;

	// constructor
	public SolvePuzzle(int[][] puzzle) {
		this.puzzle = puzzle.clone();
	};

	// return a solved sudoku puzzle
	public int[][] solve(int[][] puzzle, boolean hint) {
		int level = -1;
		List<Guess> guessList = new ArrayList<Guess>();
		BitSet[][] poss = new BitSet[Globals.SIZE][Globals.SIZE];

		int[][] original = new int[Globals.SIZE][Globals.SIZE];
		for (int i = 0; i < Globals.SIZE; i++) {
			original[i] = puzzle[i].clone();
		}

		getPoss(puzzle, poss);

		while (!completed(puzzle)) {
			int option;

			do {
				option = checkAllSquares(puzzle, poss, hint);
				if (oneSquare && noGuess && hint) return puzzle;
				option |= checkRowsCols(puzzle, poss, hint);
				if (oneSquare && noGuess && hint) return puzzle;
			} while (option == 1);

			if (completed(puzzle)) break;

			if (option == -1) {
				if (level == -1) {
					System.out.println("ERROR: Puzzle unsolvable.");
					System.exit(1);
				}

				int guessI = guessList.get(level).i;
				int guessJ = guessList.get(level).j;
				int[][] guessPuzzle = guessList.get(level).puzzle;
				BitSet[][] guessPoss = guessList.get(level).poss;

				// revert guesses if nothing in the square turns out to be correct
				while (nextOption(guessPoss[guessI][guessJ], guessPuzzle[guessI][guessJ]) == Globals.LAST_OPTION) {
					if (Globals.VERBOSE) System.out.println(guessPuzzle[guessI][guessJ] + " at (" + guessJ + "," + guessI + ") was incorrect ... WHILE");
					guessList.remove(level);
					level--;

					if (level == -1) {
						System.out.println("ERROR: Puzzle unsolvable.");
						System.exit(1);
					}

					guessI = guessList.get(level).i;
					guessJ = guessList.get(level).j;
					guessPuzzle = guessList.get(level).puzzle;
					guessPoss = guessList.get(level).poss;
				}

				if (Globals.VERBOSE) System.out.println(guessPuzzle[guessI][guessJ] + " at (" + guessJ + "," + guessI + ") was incorrect ...");
				guessPuzzle[guessI][guessJ] = nextOption(guessPoss[guessI][guessJ], guessPuzzle[guessI][guessJ]);
				if (Globals.VERBOSE) System.out.println("Guessing " + guessPuzzle[guessI][guessJ] + " at (" + guessJ + "," + guessI + ") ...");
				Globals.GUESSES++;

				// restore puzzle with a new guess
				for (int i = 0; i < Globals.SIZE; i++) {
					for (int j = 0; j < Globals.SIZE; j++) {
						puzzle[i][j] = guessPuzzle[i][j];
						poss[i][j] = (BitSet) guessPoss[i][j].clone();
					}
				}
				clearPoss(poss, guessI, guessJ, puzzle[guessI][guessJ]);
			} else if (option == 0) {
				noGuess = false;
				level++;
				guessList.add(new Guess());

				initialGuess:
				for (int i = 0; i < Globals.SIZE; i++) {
					for (int j = 0; j < Globals.SIZE; j++) {
						if (puzzle[i][j] == 0) {
							puzzle[i][j] = nextOption(poss[i][j], puzzle[i][j]);
							if (Globals.VERBOSE) System.out.println("Guessing " + puzzle[i][j] + " at (" + j + "," + i + ") ...");
							Globals.GUESSES++;

							for (int k = 0; k < Globals.SIZE; k++) {
								for (int l = 0; l < Globals.SIZE; l++) {
									guessList.get(level).poss[k][l] = new BitSet(Globals.SIZE);
									guessList.get(level).poss[k][l] = (BitSet) poss[k][l].clone();
								}
							}
							guessList.get(level).i = i;
							guessList.get(level).j = j;

							clearPoss(poss, i, j, puzzle[i][j]);
							break initialGuess;
						}
					}
				}

				for (int i = 0; i < Globals.SIZE; i++) {
					guessList.get(level).puzzle[i] = puzzle[i].clone();
				}
			}
		}

		// if there was a guess, solve the whole puzzle to confirm the guess was correct, then add the first guess to the original puzzle
		if (hint && !noGuess) {
			fillSquare:
			for (int i = 0; i < Globals.SIZE; i++) {
				for (int j = 0; j < Globals.SIZE; j++) {
					if (original[i][j] == 0) {
						original[i][j] = puzzle[i][j];
						break fillSquare;
					}
				}
			}
			return original;
		} else return puzzle;
	}

	private void getPoss(int[][] puzzle, BitSet[][] poss) {
		for (int i = 0; i < Globals.SIZE; i++) {
			for (int j = 0; j < Globals.SIZE; j++) {
				poss[i][j] = new BitSet(Globals.SIZE);
				if (puzzle[i][j] == 0) {
					// initialize BitSet to 1's
					poss[i][j].set(0, Globals.SIZE);

					// check row and column for numbers to clear from BitSet
					for (int a = 0; a < Globals.SIZE; a++) {
						if (puzzle[i][a] != 0) poss[i][j].clear(puzzle[i][a] - 1);
						if (puzzle[a][j] != 0) poss[i][j].clear(puzzle[a][j] - 1);
					}

					// check box for numbers to clear from BitSet
					for (int a = i / Globals.BOX_SIZE * Globals.BOX_SIZE; a < i / Globals.BOX_SIZE * Globals.BOX_SIZE + Globals.BOX_SIZE; a++) {
						for (int b = j / Globals.BOX_SIZE * Globals.BOX_SIZE; b < j / Globals.BOX_SIZE * Globals.BOX_SIZE + Globals.BOX_SIZE; b++) {
							if (puzzle[a][b] != 0) poss[i][j].clear(puzzle[a][b] - 1);
						}
					}
				}
			}
		}
	}

	// check all squares to see if they can be easily filled in
	private int checkAllSquares(int[][] puzzle, BitSet[][] poss, boolean hint) {
		int flag = 0;

		/* Flags:
		 * -1 ~ An error occurred.
		 * 0 ~ No squares were filled.
		 * 1 ~ At least one square was filled.
		 */

		for (int i = 0; i < Globals.SIZE; i++) {
			for (int j = 0; j < Globals.SIZE; j++) {
				if (puzzle[i][j] == 0) {
					int option = checkSquare(puzzle, i, j, poss);
					if (option == -1) return -1;
					else if (option == 1) {
						flag = 1;
						oneSquare = true;
						if (hint) return flag;
					}
				}
			}
		}

		return flag;
	}

	// check to see if a square of the puzzle can be filled in
	private int checkSquare(int[][] puzzle, int i, int j, BitSet[][] poss) {
		int sum = 0;
		int index = 0;

		/* Options:
		 * -1 ~ Error, square cannot be filled.
		 * 0 ~ Nothing could be determined about the square.
		 * 1 ~ There was only one possibility for the square and it has been filled.
		 */

		for (int a = 0; a < Globals.SIZE; a++) {
			if (poss[i][j].get(a)) {
				sum++;
				index = a;
			}
		}

		if (sum == 1) {
			puzzle[i][j] = index + 1;
			clearPoss(poss, i, j, index + 1);
			return 1;
		} else if (sum == 0) {
			return -1;
		} else {
			return 0;
		}
	}

	private int checkRowsCols(int[][] puzzle, BitSet[][] poss, boolean hint) {
		int option = 0;

		// check rows
		for (int i = 0; i < Globals.SIZE; i++) {
			int[] occur = new int[Globals.SIZE];
			int[] index = new int[Globals.SIZE];
			// collect number of occurrences of each number
			for (int j = 0; j < Globals.SIZE; j++) {
				for (int k = 0; k < Globals.SIZE; k++) {
					if (poss[i][j].get(k)) {
						occur[k]++;
						index[k] = j;
					}
				}
			}
			// check if a number occurs once, then deal with it
			for (int j = 0; j < Globals.SIZE; j++) {
				if (occur[j] == 1) {
					option = 1;
					puzzle[i][index[j]] = j + 1;
					poss[i][index[j]].clear();
					clearPoss(poss, i, index[j], j + 1);
					oneSquare = true;
					if (hint) return option;
				}
			}
		}

		// check columns
		for (int i = 0; i < Globals.SIZE; i++) {
			int[] occur = new int[Globals.SIZE];
			int[] index = new int[Globals.SIZE];
			// collect number of occurrences of each number
			for (int j = 0; j < Globals.SIZE; j++) {
				for (int k = 0; k < Globals.SIZE; k++) {
					if (poss[j][i].get(k)) {
						occur[k]++;
						index[k] = j;
					}
				}
			}
			// check if a number occurs once, then deal with it
			for (int j = 0; j < Globals.SIZE; j++) {
				if (occur[j] == 1) {
					option = 1;
					puzzle[index[j]][i] = j + 1;
					poss[index[j]][i].clear();
					clearPoss(poss, index[j], i, j + 1);
					oneSquare = true;
					if (hint) return option;
				}
			}
		}

		return option;
	}

	// get the next possibility for a given square
	private int nextOption(BitSet poss, int lastGuess) {
		for (int i = lastGuess; i < Globals.SIZE; i++) {
			if (poss.get(i)) return i + 1;
		}
		return Globals.LAST_OPTION;
	}

	// clear a row, column, and box of having the possibility of index
	private void clearPoss(BitSet[][] poss, int i, int j, int index) {
		for (int a = 0; a < Globals.SIZE; a++) {
			poss[i][a].clear(index - 1);
			poss[a][j].clear(index - 1);
		}

		for (int a = i / Globals.BOX_SIZE * Globals.BOX_SIZE; a < i / Globals.BOX_SIZE * Globals.BOX_SIZE + Globals.BOX_SIZE; a++) {
			for (int b = j / Globals.BOX_SIZE * Globals.BOX_SIZE; b < j / Globals.BOX_SIZE * Globals.BOX_SIZE + Globals.BOX_SIZE; b++) {
				poss[a][b].clear(index - 1);
			}
		}
	}

	// check if the puzzle is completed
	private boolean completed(int[][] puzzle) {
		for (int i = 0; i < Globals.SIZE; i++) {
			for (int j = 0; j < Globals.SIZE; j++) {
				if (puzzle[i][j] == 0) return false;
			}
		}
		return true;
	}
}
