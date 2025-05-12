package main;

import java.util.List;
import java.util.ArrayList;

import entities.AnimatedEntity;
import entities.GameMaster;
import entities.InteractionBox;

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
            	
                ArrayList<String> key = getKeyPressed(window.getKeyManager());
                
                for (AnimatedEntity ent : gm.animatedEntities) {
                	
                    ent.memorizeValues();
                    
                    ent.update(window.getKeyManager().keys);
                    ent.box.updatePosition(ent.x, ent.y);

                    boolean match = false;
                    
                	if (ent.interaction) {
                		
                		ent.intrBox.updatePosition(ent.x, ent.y);
                		InteractionBox intr = null;
                		
                		for (InteractionBox intr2 : gm.interactionBoxes) {
                			
                			if (gm.checkInteraction(ent.intrBox, intr2)) { intr = intr2; break; }
                			
                		}
                		
                		if (intr != null)
                		switch (intr.kind) {
                		
                		case "door0": ent.exitHouse(); match = true; break;
                		case "door1": ent.setLocation(windows.get(1).getCamera().x, windows.get(1).getCamera().y + gm.windowValues[1][0]); match = true; break;
                		case "box": intr.linkObj.triggerIntr(ent.kind); break;
                		
                		}
                		
                		
                	}
                    
                    if (!match && gm.checkCollision(ent.box)) {
                    	
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

    private ArrayList<String> getKeyPressed(KeyManager keys) {

    	ArrayList<String> keysPressed = new ArrayList<>();
    	
        for (int i = 0; i < keys.keys.length; i++) {
        	
            if (keys.keys[i]) {
                keysPressed.add(String.valueOf((char) ('a' + i)));
            }
        }
        return keysPressed;
    }
}
