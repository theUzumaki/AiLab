package main;

import java.util.List;

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
            	
                String key = getKeyPressed(window.getKeyManager());
                
                for (AnimatedEntity ent : gm.animatedEntities) {
                	
                    ent.memorizeValues();
                    
                    ent.update(key);
                    ent.box.updatePosition(ent.x, ent.y);

                    boolean match = false;
                    
                	if (ent.interaction) {
                		
                		ent.intrBox.updatePosition(ent.x, ent.y);
                		String kind = "";
                		
                		for (InteractionBox intr : gm.interactionBoxes) {
                			
                			if (gm.checkInteraction(ent.intrBox, intr)) { kind = intr.kind; break; }
                			
                		}
                		
                		switch (kind) {
                		
                		case "door0": ent.exitHouse(); match = true; break;
                		case "door1": ent.setLocation(windows.get(1).getCamera().x, windows.get(1).getCamera().y + gm.windowValues[1][0]); match = true; break;
                		
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

    private String getKeyPressed(KeyManager keys) {

        for (int i = 0; i < keys.keys.length; i++) {
        	
            if (keys.keys[i]) {
                return String.valueOf((char) ('a' + i));
            }
        }
        return "z";
    }
}
