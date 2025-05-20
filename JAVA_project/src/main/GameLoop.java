package main;

import java.util.List;

import javax.swing.SwingUtilities;

import java.util.ArrayList;
import java.util.Arrays;

import entities.AnimatedEntity;
import entities.GameMaster;
import entities.InteractionBox;

import java.awt.Robot;
import java.awt.Rectangle;
import java.awt.AWTException;
import java.awt.Graphics2D;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;

public class GameLoop implements Runnable {
	
    private boolean running = false;
	
    // Main objects
    private final GameMaster gm;
    private final List<Game> windows;
    
    private ImageSaver saver = new ImageSaver();
    private Thread saverThread = new Thread(saver);
    
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
        int fps = 15;
        long frameTime = 1000 / fps;
        
        int counter = 0;
        saverThread.start();
        
        new Thread(() -> {
        	saver.detection();
        }).start();

        while (running) {
            long start = System.currentTimeMillis();

            int num_window = 0;
            
            for (AnimatedEntity ent : gm.animatedEntities) {
            	if (ent.aligned) {
            		try {
						SwingUtilities.invokeAndWait(() -> {
							BufferedImage img = windows.get(ent.stage).captureFrameCentered(ent.x, ent.y);
							saver.saveImage(img, ent.kind);
						});
					} catch (Exception e) {
					    e.printStackTrace();
					}
            	}
            }
            
            
            // Update all entities with input from any view
            for (Game window : windows) {
            	
            	for (AnimatedEntity dead : deadEntities) {
            		gm.animatedEntities.remove(dead);
            		gm.interactionBoxes.remove(dead.intrBox);
            	}
            	
            	
                
                for (AnimatedEntity ent : gm.animatedEntities) {
                	
                    if (ent.y != -1000) ent.memorizeValues();
                    
                    if (ent.stage == num_window)
                    	ent.update(window.getKeyManager().keys);
                    
                    if (ent.y != -1000) { ent.box.updatePosition(ent.x, ent.y); ent.intrBox.updatePosition(ent.x, ent.y); }

                    InteractionBox intr = null;
                    
                    if (ent.interaction && ent.y == -1000) {

                    	ent.triggerIntr(null);
                    	continue;
                    	
                    } else if (ent.interaction) {
	            		
	            		for (InteractionBox intr2 : gm.interactionBoxes)
	            			
	            			if (gm.checkInteraction(ent.intrBox, intr2)) { intr = intr2; break; }
            			
            		} else if (ent.interacting) {
            			
            			for (AnimatedEntity ent2 : gm.animatedEntities)
            				
            				if ( gm.checkInteraction(ent.intrBox, ent2.intrBox) ) { intr = ent2.intrBox; break; }
            			
            		}
            		if (intr != null) System.out.print(ent.kind + " INTERACTING WITH: " + intr.kind);
            		if (intr != null) switch (intr.kind) {
            		
            		case "door0": ent.exitHouse(); break;
            		case "door1": ent.setLocation(windows.get(1).getCamera().x + gm.windowValues[1][0], windows.get(1).getCamera().y + gm.windowValues[1][0], 1); break;
            		case "door2": ent.setLocation(windows.get(2).getCamera().x + gm.windowValues[1][0], windows.get(2).getCamera().y + gm.windowValues[2][0], 2);break;
            		case "box": intr.linkObj.triggerIntr(ent); ent.triggerIntr(intr.linkObj); break;
            		case "warehouse": intr.linkObj.triggerIntr(ent); ent.triggerIntr(intr.linkObj); break;
            		case "border": ent.triggerIntr(intr.linkObj); break;
            		case "animated": intr.linkObj.triggerIntr(ent);
            		
            		}
                    
                    if (ent.dead) deadEntities.add(ent);
                    if (ent.stage == num_window && gm.checkLimit(ent.box, num_window)) {
                    	
                        ent.setBack();
                        ent.box.updatePosition(ent.x, ent.y);
                        continue;
                    	
                    };
                    
                    if (gm.checkCollision(ent.box, ent)) {
                    	
                        ent.setBack();
                        ent.box.updatePosition(ent.x, ent.y);
                        
                    }
                    
                }
                num_window++;
            }

            for (Game view : windows) {
        	    view.repaint();
            }

            if (counter == fps) counter = 0;
            counter++;
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
