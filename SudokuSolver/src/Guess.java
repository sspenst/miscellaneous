import java.util.BitSet;

public class Guess {
	public int[][] puzzle = new int[Globals.SIZE][Globals.SIZE];
	public int i;
	public int j;
	public BitSet[][] poss = new BitSet[Globals.SIZE][Globals.SIZE];
}
