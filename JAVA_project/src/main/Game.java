package main;

import javax.swing.JPanel;

import java.awt.Dimension;
import java.awt.Graphics;
import java.util.Collections;
import java.util.Comparator;
import java.awt.Color;

import entities.GameMaster;
import entities.PhysicalEntity;
import entities.AnimatedEntity;
import entities.BackgroundEntity;
import entities.CollisionBox;

@SuppressWarnings("serial")
public class Game extends JPanel implements Runnable {

    private Thread gameThread;
    private boolean running = false;

    // Size of the game window
    private final int ROWS = 15;
    private final int COLUMNS = 30;
    private final int SIZETILE = 48;
    private final int WIDTH = COLUMNS * SIZETILE;
    private final int HEIGHT = ROWS * SIZETILE;
    
    // Main objects
    KeyManager keys;
    GameMaster gm;

    public Game() {
        setPreferredSize(new Dimension(WIDTH, HEIGHT));
        setBackground(Color.BLACK);
        setFocusable(true);
        
		keys = new KeyManager();
		addKeyListener(keys);
		gm = GameMaster.getInstance(SIZETILE, ROWS, COLUMNS);
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

        String key = getKeyPressed();
        
        for(AnimatedEntity ent : gm.animatedEntities) {
        	
        	ent.memorizeValues();
        	
        	ent.update(key);
        	ent.box.updatePosition(ent.x, ent.y);
        	
        	if ( gm.checkCollision(ent.box) ) {
        		ent.setBack();
        		ent.box.updatePosition(ent.x, ent.y);
        	}        	
        }
        
    }

    // Rendering logic
    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        
        Collections.sort(gm.physicalEntities, Comparator.comparingInt(c -> c.y + c.heigth));
        
        for(BackgroundEntity ent : gm.bgEntities1) {
        	ent.draw(g);
        }
        
        for(BackgroundEntity ent : gm.bgEntities2) {
        	ent.draw(g);
        }
        
        for(PhysicalEntity ent : gm.physicalEntities) {
        	ent.draw(g);
        }
        
        /*
        for(CollisionBox box : gm.collisionBoxes) {
        	g.fillRect(box.left, box.top, SIZETILE, SIZETILE);
        }
        */
    }

    public void stop() {
        running = false;
    }
    
    private String getKeyPressed () {
    	
        for (int i = 0; i < keys.keys.length; i++) {
            if (keys.keys[i]) {
                // Convert index to character
                return String.valueOf((char) ('a' + i));
            }
        }
		return "z";
    	
    }
}

