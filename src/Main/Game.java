package Main;

import javax.swing.JPanel;
import java.awt.Dimension;
import java.awt.Graphics;
import java.awt.Color;

@SuppressWarnings("serial")
public class Game extends JPanel implements Runnable {

    private Thread gameThread;
    private boolean running = false;

    // Size of the game window
    private final int WIDTH = 800;
    private final int HEIGHT = 600;

    public Game() {
        setPreferredSize(new Dimension(WIDTH, HEIGHT));
        setBackground(Color.BLACK);
    }

    public void start() {
        if (gameThread == null) {
            running = true;
            gameThread = new Thread(this);
            gameThread.start();
        }
    }

    @Override
    public void run() {
        // Basic game loop with fixed frame rate
        int fps = 60;
        long frameTime = 1000 / fps;

        while (running) {
            long startTime = System.currentTimeMillis();

            update();
            repaint(); // Calls paintComponent

            long endTime = System.currentTimeMillis();
            long delta = endTime - startTime;

            if (delta < frameTime) {
                try {
                    Thread.sleep(frameTime - delta);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    // Game logic update
    private void update() {
        // Example: print update
        System.out.println("Game updating...");
    }

    // Rendering logic
    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        // Example: draw a red rectangle
        g.setColor(Color.RED);
        g.fillRect(100, 100, 50, 50);
    }

    public void stop() {
        running = false;
    }
}

