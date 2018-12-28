import javax.swing.Box;
import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JPanel;
import javax.swing.JFrame;
import javax.swing.JOptionPane;

import java.awt.Container;
import java.awt.Dimension;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.BufferedWriter;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.UnsupportedEncodingException;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;

@SuppressWarnings("serial")
public class SudokuSolver extends JPanel implements ActionListener {
	final static int BOX_DIM = 41;

	int row;
	int column;

	protected JButton[][] square = new JButton[Globals.SIZE][Globals.SIZE];
	protected JButton[] number = new JButton[Globals.SIZE];
	protected JButton optHelp = new JButton("Help");
	protected JButton optLoad = new JButton("Load");
	protected JButton optSave = new JButton("Save");
	protected JButton optClear = new JButton("Clear");
	protected JButton optHint = new JButton("Hint");
	protected JButton optSolve = new JButton("Solve");

	public SudokuSolver() {
		Container pane = new Container(); // contains the whole content pane
		pane.setLayout(new BoxLayout(pane, BoxLayout.X_AXIS));

		Container leftPane = new Container(); // contains the puzzle and numbers
		leftPane.setLayout(new BoxLayout(leftPane, BoxLayout.Y_AXIS));

		// initialize boxes, and buttons in each box
		JPanel puzzle = new JPanel(); // puzzle of 3x3 boxes
		puzzle.setLayout(new GridLayout(Globals.BOX_SIZE, Globals.BOX_SIZE, 6, 6));

		JPanel[][] box = new JPanel[Globals.BOX_SIZE][Globals.BOX_SIZE];

		for (int i = 0; i < Globals.BOX_SIZE; i++) {
			for (int j = 0; j < Globals.BOX_SIZE; j++) {
				box[i][j] = new JPanel();
				box[i][j].setLayout(new GridLayout(Globals.BOX_SIZE, Globals.BOX_SIZE, 2, 2));

				for (int k = i * Globals.BOX_SIZE; k < i * Globals.BOX_SIZE + Globals.BOX_SIZE; k++) {
					for (int l = j * Globals.BOX_SIZE; l < j * Globals.BOX_SIZE + Globals.BOX_SIZE; l++) {
						square[k][l] = new JButton(" ");
						square[k][l].setActionCommand("chooseNum" + String.valueOf(k) + String.valueOf(l));
						square[k][l].addActionListener(this);
						square[k][l].setPreferredSize(new Dimension(BOX_DIM, BOX_DIM));
						box[i][j].add(square[k][l]);
					}
				}

				puzzle.add(box[i][j]);
			}
		}

		// initialize a button for each number 1-9
		JPanel numbers = new JPanel();
		numbers.setLayout(new GridLayout(1, Globals.SIZE, 3, 3));

		for (int i = 0; i < Globals.SIZE; i++) {
			number[i] = new JButton(String.valueOf(i + 1));
			number[i].setActionCommand(String.valueOf(i + 1));
			number[i].addActionListener(this);
			number[i].setEnabled(false);
			number[i].setPreferredSize(new Dimension(BOX_DIM, BOX_DIM));
			numbers.add(number[i]);
		}

		// add the puzzle and numbers to the left side of the screen
		leftPane.add(puzzle);
		leftPane.add(Box.createRigidArea(new Dimension(0, 15)));
		leftPane.add(numbers);

		// initialize buttons for options
		JPanel options = new JPanel();
		options.setLayout(new GridLayout(6, 1, 20, 20));

		optHelp.setActionCommand("help");
		optLoad.setActionCommand("load");
		optSave.setActionCommand("save");
		optClear.setActionCommand("clear");
		optHint.setActionCommand("hint");
		optSolve.setActionCommand("solve");

		optHelp.addActionListener(this);
		optLoad.addActionListener(this);
		optSave.addActionListener(this);
		optClear.addActionListener(this);
		optHint.addActionListener(this);
		optSolve.addActionListener(this);

		options.add(optHelp);
		options.add(optLoad);
		options.add(optSave);
		options.add(optClear);
		options.add(optHint);
		options.add(optSolve);

		// add sections to the content pane
		pane.add(leftPane);
		pane.add(Box.createRigidArea(new Dimension(20, 0)));
		pane.add(options);

		add(pane);
	}

	public void actionPerformed(ActionEvent e) {
		String command = e.getActionCommand();

		switch (command) {
		case "help":
			help();
			break;
		case "load":
			load();
			break;
		case "save":
			save();
			break;
		case "clear":
			clear();
			break;
		case "hint":
			solve(true);
			break;
		case "solve":
			solve(false);
			break;
		default:
			if (command.contains("chooseNum")) chooseNum(command);
			else numChosen(command);
			break;
		}
	}

	private void help() {
		String helpText = "To input a sudoku puzzle, you can either manually input each square\n";
		helpText += "by clicking the square and then clicking the corresponding number, or\n";
		helpText += "you can load a previously saved puzzle using the Load button.\n";
		helpText += "After manually inputting a sudoku puzzle, you can press the Save button\n";
		helpText += "to save the current state of the puzzle to a file. Note that this\n";
		helpText += "will overwrite the file if it exists.\n";
		helpText += "Use Clear to clear the board of all numbers, Hint to give the\n";
		helpText += "next solveable square, and Solve to give the solution to the puzzle.";
		JOptionPane.showMessageDialog(null, helpText, "Help", JOptionPane.INFORMATION_MESSAGE);
	}

	private void load() {
		String filename = JOptionPane.showInputDialog(null, "Enter file name:", "Load File", JOptionPane.OK_CANCEL_OPTION);

		if (filename != null) {
			List<String> lines = null;
			// retrieve data from a file
			try {
				lines = Files.readAllLines(Paths.get("puzzles/" + filename), StandardCharsets.US_ASCII);

				// take data from file and input it into the squares
				for (int i = 0; i < Globals.SIZE; i++) {
					String line = lines.get(i);
					for (int j = 0; j < Globals.SIZE; j++) {
						if (line.charAt(j) == '.') square[i][j].setText(" ");
						else square[i][j].setText(Character.toString(line.charAt(j)));
					}
				}
			} catch (IOException e1) {
				JOptionPane.showMessageDialog(null, "File not found.", "Error", JOptionPane.ERROR_MESSAGE);
			}
		}
	}

	private void save() {
		String filename = JOptionPane.showInputDialog(null, "Enter file name:", "Save File", JOptionPane.OK_CANCEL_OPTION);

		if (filename != null) {
			try (Writer writer = new BufferedWriter(new OutputStreamWriter(new FileOutputStream("puzzles/" + filename), "utf-8"))) {
				for (int i = 0; i < Globals.SIZE; i++) {
					for (int j = 0; j < Globals.SIZE; j++) {
						String squareText = square[i][j].getText();
						if (squareText.equals(" ")) writer.write(".");
						else writer.write(squareText);
					}
					writer.write("\r\n");
				}
			} catch (UnsupportedEncodingException e) {
				e.printStackTrace();
			} catch (FileNotFoundException e) {
				e.printStackTrace();
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
	}

	private void clear() {
		if (row == 0 && column == 0) {
			for (int i = 0; i < Globals.SIZE; i++) {
				for (int j = 0; j < Globals.SIZE; j++) {
					square[i][j].setText(" ");
				}
			}
		} else {
			numChosen(" ");
		}
	}
	
	private void solve(boolean hint) {
		int[][] puzzle = new int[Globals.SIZE][Globals.SIZE];

		// get the current state of the puzzle
		for (int i = 0; i < Globals.SIZE; i++) {
			for (int j = 0; j < Globals.SIZE; j++) {
				String squareData = square[i][j].getText();
				if (squareData == " ") puzzle[i][j] = 0;
				else puzzle[i][j] = Integer.valueOf(squareData);
			}
		}

		final long startTime = System.currentTimeMillis();

		// solve the puzzle
		SolvePuzzle solvePuzzle = new SolvePuzzle(puzzle);
		puzzle = solvePuzzle.solve(puzzle, hint).clone();

		final long endTime = System.currentTimeMillis();
		System.out.println("Solving time: " + (endTime - startTime));
		System.out.println("Guesses: " + Globals.GUESSES);
		Globals.GUESSES = 0;

		// write the solved puzzle back to the screen
		for (int i = 0; i < Globals.SIZE; i++) {
			for (int j = 0; j < Globals.SIZE; j++) {
				if (puzzle[i][j] == 0) square[i][j].setText(" ");
				else square[i][j].setText(Integer.toString(puzzle[i][j]));
			}
		}
	}

	public void chooseNum(String command) {
		// let the user choose a number
		for (int i = 0; i < Globals.SIZE; i++) {
			number[i].setEnabled(true);
		}

		optHelp.setEnabled(false);
		optLoad.setEnabled(false);
		optSave.setEnabled(false);
		optHint.setEnabled(false);
		optSolve.setEnabled(false);
		// store the location the user pressed
		row = Character.getNumericValue(command.charAt(9));
		column = Character.getNumericValue(command.charAt(10));
	}

	public void numChosen(String command) {
		// restrict the user from choosing a number
		for (int i = 0; i < Globals.SIZE; i++) {
			number[i].setEnabled(false);
		}
		optHelp.setEnabled(true);
		optLoad.setEnabled(true);
		optSave.setEnabled(true);
		optHint.setEnabled(true);
		optSolve.setEnabled(true);
		// update the button with the chosen number
		square[row][column].setText(command);
		row = 0;
		column = 0;
	}

	private static void createAndShowGUI() {
		// Create and set up the window.
		JFrame frame = new JFrame("SudokuSolver");
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

		// Create and set up the content pane.
		SudokuSolver newContentPane = new SudokuSolver();
		newContentPane.setOpaque(true); // content panes must be opaque
		frame.setContentPane(newContentPane);
		frame.setResizable(false);

		// Display the window.
		frame.pack();
		frame.setVisible(true);
	}

	public static void main(String[] args) {
		// Schedule a job for the event-dispatching thread:
		// creating and showing this application's GUI.
		javax.swing.SwingUtilities.invokeLater(new Runnable() {
			public void run() {
				createAndShowGUI();
			}
		});
	}
}
