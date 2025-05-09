package main;

import java.util.List;
import java.awt.Component;

import entities.AnimatedEntity;
import entities.GameMaster;

public class GameLoop implements Runnable {
	
    private boolean running = false;
	
    // Main objects
    private final GameMaster gm;
    private final List<Game> windows;

    public GameLoop(List<Game> views) {
        gm = GameMaster.getInstance();
        windows = views;
        running = true;
    }

    public void stop() {
        running = false;
    }

    @Override
    public void run() {
        int fps = 60;
        long frameTime = 1000 / fps;

        while (running) {
            long start = System.currentTimeMillis();

            // Update all entities with input from any view
            for (Game window : windows) {
            	
                String key = getKeyPressed(window.getKeyManager());
                
                for (AnimatedEntity ent : gm.animatedEntities) {
                    ent.memorizeValues();
                    ent.update(key);
                    ent.box.updatePosition(ent.x, ent.y);
                    if (gm.checkCollision(ent.box)) {
                        ent.setBack();
                        ent.box.updatePosition(ent.x, ent.y);
                    }
                }
            }

            for (Game view : windows) {
                view.repaint();
            }

            long elapsed = System.currentTimeMillis() - start;
            if (elapsed < frameTime) {
                try {
                    Thread.sleep(frameTime - elapsed);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    private String getKeyPressed(KeyManager keys) {

        for (int i = 0; i < keys.keys.length; i++) {
        	
            if (keys.keys[i]) {
                return String.valueOf((char) ('a' + i));
            }
        }
        return "z";
    }
}
