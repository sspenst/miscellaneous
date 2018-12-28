import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import java.util.ArrayList;
import java.util.List;

class Ball {
	public double pos[] = {Globals.WIDTH/2 - Globals.RADIUS, Globals.HEIGHT/2 - Globals.RADIUS};
	public double vel[] = {0,0};
	public double acc[] = {0,Globals.ACC}; 
}

@SuppressWarnings("serial")
class Board extends JPanel {
    private Timer timer;
    public List<Ball> balls = new ArrayList<Ball>();
    
    public Board() {
        initBoard();
    }

    private void initBoard() {
        balls.add(new Ball());
    	
        addKeyListener(new Controls());
        setFocusable(true);
        
        timer = new Timer(Globals.DELAY, clock);
        timer.start();
    }
    
    ActionListener clock = new ActionListener() {
        public void actionPerformed(ActionEvent e) {
            repaint();
        }
    };
    
    @Override
    public void paintComponent(Graphics g) {
        super.paintComponent(g);
        doDrawing(g);
    }
    
    private void doDrawing(Graphics g) {
        Graphics2D g2d = (Graphics2D) g;

        g2d.setPaint(Color.red);

        RenderingHints rh = new RenderingHints(
                RenderingHints.KEY_ANTIALIASING,
                RenderingHints.VALUE_ANTIALIAS_ON);

        rh.put(RenderingHints.KEY_RENDERING,
               RenderingHints.VALUE_RENDER_QUALITY);

        g2d.setRenderingHints(rh);

    	updateBalls();
        boolean collision = true;
        boolean overlap = true;
        //while (collision || overlap) {
    		overlap = checkBallCollisions();
        	collision = checkWallCollisions();
        //}
        setVelocityZero();
        
        for (int i = 0; i < balls.size(); i++) {
        	g2d.fillOval((int)balls.get(i).pos[0], (int)balls.get(i).pos[1], Globals.DIAMETER, Globals.DIAMETER);
        }
    }
    
	private void updateBalls() {
        for (int i = 0; i < balls.size(); i++) {
			balls.get(i).vel[0] += balls.get(i).acc[0];
			balls.get(i).vel[1] += balls.get(i).acc[1];
			balls.get(i).pos[0] += balls.get(i).vel[0];
			balls.get(i).pos[1] += balls.get(i).vel[1];
        }
	}
	
	private boolean checkWallCollisions() {
		boolean collision = false;
		for (int i = 0; i < balls.size(); i++) {
			// collision with left or right wall
			if (balls.get(i).pos[0] < 0) {
				balls.get(i).pos[0] *= -1;
				balls.get(i).vel[0] *= -Globals.ELASTICITY;
				balls.get(i).vel[1] *= Globals.FRICTION;
				collision = true;
			} else if (balls.get(i).pos[0] > Globals.WIDTH - Globals.DIAMETER) {
				balls.get(i).pos[0] = 2*(Globals.WIDTH - Globals.DIAMETER) - balls.get(i).pos[0];
				balls.get(i).vel[0] *= -Globals.ELASTICITY;
				balls.get(i).vel[1] *= Globals.FRICTION;
				collision = true;
			}
			
			// collision with top or bottom wall
			if (balls.get(i).pos[1] < 0) {
				balls.get(i).pos[1] *= -1;
				balls.get(i).vel[1] *= -Globals.ELASTICITY;
				balls.get(i).vel[0] *= Globals.FRICTION;
				collision = true;
			} else if (balls.get(i).pos[1] > Globals.HEIGHT - Globals.DIAMETER) {
				balls.get(i).pos[1] = 2*(Globals.HEIGHT - Globals.DIAMETER) - balls.get(i).pos[1];
				balls.get(i).vel[1] *= -Globals.ELASTICITY;
				balls.get(i).vel[0] *= Globals.FRICTION;
				collision = true;
			}
		}
		return collision;
	}
	
	private boolean checkBallCollisions() {
		boolean overlap = false;
		for (int i = 0; i < balls.size(); i++) {
			for (int j = i+1; j < balls.size(); j++) {
				double distance = Math.sqrt(Math.pow(balls.get(i).pos[0] - balls.get(j).pos[0], 2) + Math.pow(balls.get(i).pos[1] - balls.get(j).pos[1], 2));
				if (distance < Globals.DIAMETER) {
					// there are problems when you have multiple contacts in the same frame
					// if a ball is about to hit two other balls...
					// maybe the below change would fix this if implemented correctly
					
					// collisions might actually be incorrect still if deltay is negative
					// might have to switch some signs in that case... do some tests to find out
					
					// figure out how to revert the balls to the point where they were just barely tangent so that contactAngle can be close to perfect
					// apply the same portion of velocities that were subtracted to the additions at the end of this function
					balls.get(i).pos[0] -= balls.get(i).vel[0];
					balls.get(i).pos[1] -= balls.get(i).vel[1];
					balls.get(j).pos[0] -= balls.get(j).vel[0];
					balls.get(j).pos[1] -= balls.get(j).vel[1];
					
					double deltax = balls.get(i).pos[0] - balls.get(j).pos[0];
					double deltay = balls.get(i).pos[1] - balls.get(j).pos[1];
					double contactAngle = Math.toDegrees(Math.atan(deltay / deltax)) + 90;
					double cosAngle = Math.cos(contactAngle);
					double sinAngle = Math.sin(contactAngle);
					
					// x-axis-swapped rotated velocities
					double veljx = balls.get(i).vel[0] * cosAngle + balls.get(i).vel[1] * sinAngle;
					double veliy = -1 * balls.get(i).vel[0] * sinAngle + balls.get(i).vel[1] * cosAngle;
					double velix = balls.get(j).vel[0] * cosAngle + balls.get(j).vel[1] * sinAngle;
					double veljy = -1 * balls.get(j).vel[0] * sinAngle + balls.get(j).vel[1] * cosAngle;
					/*
					// rotated positions
					double posix = balls.get(i).pos[0] * cosAngle + balls.get(i).pos[1] * sinAngle;
					double posiy = -1 * balls.get(i).pos[0] * sinAngle + balls.get(i).pos[1] * cosAngle;
					double posjx = balls.get(j).pos[0] * cosAngle + balls.get(j).pos[1] * sinAngle;
					double posjy = -1 * balls.get(j).pos[0] * sinAngle + balls.get(j).pos[1] * cosAngle;
					
					double escapeDistance = Math.abs(posix - posjx) - Math.abs(velix - veljx);
					if (escapeDistance > 0) {
							escapeDistance += 1;
							if (posix > 0) posix += escapeDistance/2;
							else posix -= escapeDistance/2;
							if (posjx > 0) posjx += escapeDistance/2;
							else posjx -= escapeDistance/2;
					}
					
					balls.get(i).pos[0] = posix * cosAngle - posiy * sinAngle;
					balls.get(j).pos[0] = posjx * cosAngle - posjy * sinAngle;
					*/
					// restoring new velocities
					balls.get(i).vel[0] = velix * cosAngle - veliy * sinAngle;
					balls.get(i).vel[1] = velix * sinAngle + veliy * cosAngle;
					balls.get(j).vel[0] = veljx * cosAngle - veljy * sinAngle;
					balls.get(j).vel[1] = veljx * sinAngle + veljy * cosAngle;
					// apply new velocities
					balls.get(i).pos[0] += balls.get(i).vel[0];
					balls.get(i).pos[1] += balls.get(i).vel[1];
					balls.get(j).pos[0] += balls.get(j).vel[0];
					balls.get(j).pos[1] += balls.get(j).vel[1];
					overlap = true;
				}
			}
		}
		return overlap;
	}
	
	private void setVelocityZero() {
		for (int i = 0; i < balls.size(); i++) {
			if (Math.abs(balls.get(i).vel[0]) < 0.05) balls.get(i).vel[0] = 0;
			if (Math.abs(balls.get(i).vel[1]) < 0.05) balls.get(i).vel[1] = 0;
        }
	}
    
    class Controls extends KeyAdapter {
    	@Override
        public void keyPressed(KeyEvent e) {
            int keycode = e.getKeyCode();
            
            switch (keycode) {
            case KeyEvent.VK_LEFT:
                for (int i = 0; i < balls.size(); i++) {
                	balls.get(i).acc[0] = -Globals.ACC;
                	balls.get(i).acc[1] = 0;
                }
                break;
                
            case KeyEvent.VK_RIGHT:
                for (int i = 0; i < balls.size(); i++) {
                	balls.get(i).acc[0] = Globals.ACC;
                	balls.get(i).acc[1] = 0;
                }
                break;
            
            case KeyEvent.VK_DOWN:
                for (int i = 0; i < balls.size(); i++) {
                	balls.get(i).acc[0] = 0;
                	balls.get(i).acc[1] = Globals.ACC;
                }
            	break;
            
            case KeyEvent.VK_UP:
                for (int i = 0; i < balls.size(); i++) {
                	balls.get(i).acc[0] = 0;
                	balls.get(i).acc[1] = -Globals.ACC;
                }
            	break;
            
            // zero gravity
            case KeyEvent.VK_SPACE:
                for (int i = 0; i < balls.size(); i++) {
                	balls.get(i).acc[0] = 0;
                	balls.get(i).acc[1] = 0;
                }
            	break;
            	
            // reset
            case KeyEvent.VK_R:
            	balls.clear();
            	balls.add(new Ball());
            	break;
            	
            // spawn a new ball
            case KeyEvent.VK_S:
            	boolean conflict = false;
                for (int i = 0; i < balls.size(); i++) {
                	if (balls.get(i).pos[0] < Globals.WIDTH/2 + Globals.RADIUS && balls.get(i).pos[0] > Globals.WIDTH/2 - 3*Globals.RADIUS &&
                		balls.get(i).pos[1] < Globals.HEIGHT/2 + Globals.RADIUS && balls.get(i).pos[1] > Globals.HEIGHT/2 - 3*Globals.RADIUS) {
                		conflict = true;
                	}
                }
                if (!conflict) balls.add(new Ball());
            	break;
            
            case KeyEvent.VK_D:
            	timer.stop();
            	Globals.DELAY = 100;
            	timer = new Timer(Globals.DELAY, clock);
                timer.start();
            	break;
            	
            case KeyEvent.VK_F:
            	timer.stop();
            	Globals.DELAY = 16;
            	timer = new Timer(Globals.DELAY, clock);
                timer.start();
            	break;
    		}
    	}
    }
}

public class PhysicsEngine extends JFrame {

    public PhysicsEngine() {
        initUI();
    }

    private void initUI() {
        Board board = new Board();
        add(board);

        setTitle("Physics Engine");
        setSize(Globals.WIDTH + 16, Globals.HEIGHT + 39);
        setLocationRelativeTo(null);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
    }

    public static void main(String[] args) {
        EventQueue.invokeLater(new Runnable() {
            @Override
            public void run() {
            	PhysicsEngine physEng = new PhysicsEngine();
                physEng.setVisible(true);
            }
        });
    }
}