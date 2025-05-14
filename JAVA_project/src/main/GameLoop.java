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
    
    private List<AnimatedEntity> deadEntities= new ArrayList<>();

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

            int num_window = 0;
            
            // Update all entities with input from any view
            for (Game window : windows) {
            	
            	for (AnimatedEntity dead : deadEntities) {
            		gm.animatedEntities.remove(dead);
            		gm.interactionBoxes.remove(dead.intrBox);
            	}
                
                for (AnimatedEntity ent : gm.animatedEntities) {
                	
                    if (ent.y != -1000) ent.memorizeValues();
                    
                    ent.update(window.getKeyManager().keys);
                    if (ent.y != -1000) { ent.box.updatePosition(ent.x, ent.y); ent.intrBox.updatePosition(ent.x, ent.y); }

                    boolean match = false;
                    
                    if (ent.interaction && ent.y == -1000) {
                    	
                    	ent.triggerIntr(null);
                    	
                    } else if (ent.interaction) {
            		
	            		
	            		InteractionBox intr = null;
	            		
	            		for (InteractionBox intr2 : gm.interactionBoxes) {
	            			
	            			if (gm.checkInteraction(ent.intrBox, intr2)) { intr = intr2; break; }
            			
            		}
            		if (intr != null) System.out.println(ent.kind + " INTERACTING WITH: " + intr.kind);
            		if (intr != null) switch (intr.kind) {
            		
            		case "door0": ent.exitHouse(); match = true; break;
            		case "door1": ent.setLocation(windows.get(1).getCamera().x, windows.get(1).getCamera().y + gm.windowValues[1][0]); match = true; break;
            		case "door2": ent.setLocation(windows.get(2).getCamera().x, windows.get(2).getCamera().y + gm.windowValues[2][0]); match = true; break;
            		case "box": intr.linkObj.triggerIntr(ent); ent.triggerIntr(intr.linkObj); break;
            		case "warehouse": intr.linkObj.triggerIntr(ent); ent.triggerIntr(intr.linkObj); break;
            		case "animated": intr.linkObj.triggerIntr(ent);
            		
            		}
                		
                		
                	}
                    
                    if (ent.dead) deadEntities.add(ent);
                    
                    if (!match && gm.checkCollision(ent.box, ent, num_window)) {
                    	
                        ent.setBack();
                        ent.box.updatePosition(ent.x, ent.y);
                        
                    }
                }
                num_window++;
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

}
