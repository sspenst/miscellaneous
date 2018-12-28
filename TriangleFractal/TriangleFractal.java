import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.awt.geom.Line2D;
import java.util.ArrayList;
import java.util.List;

import javax.swing.JFrame;
import javax.swing.SwingUtilities;

@SuppressWarnings("serial")
public class TriangleFractal extends JFrame {

	public List<Line> lineList = new ArrayList<Line>();
	public List<Triangle> triangleList = new ArrayList<Triangle>();
	// option 0 = line, 1 = triangle
	public int option = 0;

	class Line {
		public Line(double a1, double b1, double a2, double b2) {
			x1 = a1;
			y1 = b1;
			x2 = a2;
			y2 = b2;
		}

		public Line(Line line) {
			x1 = line.x1;
			y1 = line.y1;
			x2 = line.x2;
			y2 = line.y2;
		}

		private double x1, y1, x2, y2;
	}

	class Triangle {
		public Triangle(double a1, double b1, double a2, double b2, double a3, double b3) {
			x1 = a1;
			y1 = b1;
			x2 = a2;
			y2 = b2;
			x3 = a3;
			y3 = b3;
		}

		public Triangle(Triangle triangle) {
			x1 = triangle.x1;
			y1 = triangle.y1;
			x2 = triangle.x2;
			y2 = triangle.y2;
			x3 = triangle.x3;
			y3 = triangle.y3;
		}

		private double x1, y1, x2, y2, x3, y3;
	}

	// split one line into four triangular lines
	private void incFractal(Line line) {
		double thirdX = (line.x2 - line.x1) / 3;
		double thirdY = (line.y2 - line.y1) / 3;

		Line line1 = new Line(line.x1, line.y1, line.x1 + thirdX, line.y1 + thirdY);
		lineList.add(line1);

		double x2 = line1.x2 + thirdX / 2 + thirdY * Math.sqrt(3) / 2;
		double y2 = line1.y2 + thirdY / 2 - thirdX * Math.sqrt(3) / 2;
		Line line2 = new Line(line1.x2, line1.y2, x2, y2);
		lineList.add(line2);

		Line line3 = new Line(line2.x2, line2.y2, line.x2 - thirdX, line.y2 - thirdY);
		lineList.add(line3);

		Line line4 = new Line(line3.x2, line3.y2, line.x2, line.y2);
		lineList.add(line4);
	}

	// turn four lines into one straight line
	private void decFractal(Line firstLine, Line lastLine) {
		Line line = new Line(firstLine.x1, firstLine.y1, lastLine.x2, lastLine.y2);
		lineList.add(line);
	}

	// turn one triangle into three triangles
	private void incFractal(Triangle triangle) {
		triangle.x2 = triangle.x2 - (triangle.x2 - triangle.x1) / 2;
		triangle.x3 = triangle.x3 - (triangle.x3 - triangle.x1) / 2;
		triangle.y3 = triangle.y3 + (triangle.y1 - triangle.y3) / 2;

		double xShift = triangle.x2 - triangle.x1;
		Triangle triangleRight = new Triangle(triangle);
		triangleRight.x1 += xShift;
		triangleRight.x2 += xShift;
		triangleRight.x3 += xShift;
		triangleList.add(triangleRight);

		xShift /= 2;
		double yShift = triangle.y1 - triangle.y3;
		Triangle triangleUp = new Triangle(triangle);
		triangleUp.x1 += xShift;
		triangleUp.y1 -= yShift;
		triangleUp.x2 += xShift;
		triangleUp.y2 -= yShift;
		triangleUp.x3 += xShift;
		triangleUp.y3 -= yShift;
		triangleList.add(triangleUp);
	}

	// turn three triangles into one triangle
	private void decFractal(int i, int size) {
		triangleList.remove(size + i * 2 + 1);
		triangleList.remove(size + i * 2);

		Triangle triangle = triangleList.get(i);
		triangle.x2 = 2 * triangle.x2 - triangle.x1;
		triangle.x3 = 2 * triangle.x3 - triangle.x1;
		triangle.y3 = 2 * triangle.y3 - triangle.y1;
	}

	class Controls extends KeyAdapter {
		@Override
		public void keyPressed(KeyEvent e) {
			List<Line> clonedLines = new ArrayList<Line>(lineList.size());
			int keycode = e.getKeyCode();

			switch (keycode) {
			case KeyEvent.VK_UP:
				if (option == 0) {
					for (Line line : lineList)
						clonedLines.add(new Line(line));
					lineList.clear();
					for (Line line : clonedLines)
						incFractal(line);
					clonedLines.clear();
				} else {
					int size = triangleList.size();
					for (int i = 0; i < size; i++)
						incFractal(triangleList.get(i));
				}
				repaint();
				break;
			case KeyEvent.VK_DOWN:
				if (option == 0) {
					// don't reduce the complexity of a fractal at its most basic form
					if (lineList.size() != 1) {
						for (Line line : lineList)
							clonedLines.add(new Line(line));
						lineList.clear();
						for (int i = 0; i < clonedLines.size(); i += 4) {
							decFractal(clonedLines.get(i), clonedLines.get(i + 3));
						}
						clonedLines.clear();
					}
				} else {
					if (triangleList.size() != 1) {
						int size = triangleList.size();
						for (int i = size / 3 - 1; i >= 0; i--) {
							decFractal(i, size / 3);
						}
					}
				}
				repaint();
				break;
			case KeyEvent.VK_LEFT:
				option = 0;
				repaint();
				break;
			case KeyEvent.VK_RIGHT:
				option = 1;
				repaint();
				break;
			}
		}
	}

	void drawLines(Graphics g) {
		Graphics2D g2d = (Graphics2D) g;

		if (option == 0) {
			for (Line line : lineList)
				g2d.draw(new Line2D.Double(line.x1, line.y1, line.x2, line.y2));
		} else {
			for (Triangle triangle : triangleList) {
				g2d.draw(new Line2D.Double(triangle.x1, triangle.y1, triangle.x2, triangle.y2));
				g2d.draw(new Line2D.Double(triangle.x2, triangle.y2, triangle.x3, triangle.y3));
				g2d.draw(new Line2D.Double(triangle.x3, triangle.y3, triangle.x1, triangle.y1));
			}
		}
	}

	public void paint(Graphics g) {
		super.paint(g);
		drawLines(g);
	}

	public TriangleFractal() {
		super("Triangle Fractal");

		setSize(1500, 600);
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setLocationRelativeTo(null);

		addKeyListener(new Controls());

		Line firstLine = new Line(8, 550, 1491, 550);
		lineList.add(firstLine);

		double third = (firstLine.x2 - firstLine.x1) / 3;
		Triangle firstTriangle = new Triangle(firstLine.x1 + third, 550, firstLine.x2 - third, 550, firstLine.x1 + third * 1.5, 550 - third * Math.sqrt(3) / 2);
		triangleList.add(firstTriangle);

		System.out.println("Press the up arrow key to increase the complexity of the fractal, and the down arrow key to decrease it.");
		System.out.println("Press the right arrow key to switch the type of fractal that is displayed.");
	}

	public static void main(String[] args) {
		SwingUtilities.invokeLater(new Runnable() {
			@Override
			public void run() {
				new TriangleFractal().setVisible(true);
			}
		});
	}
}
