package main;

import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

import javax.swing.SwingUtilities;

import java.util.ArrayList;

import entities.AnimatedEntity;
import entities.GameMaster;
import entities.InteractionBox;
import entities.Panam;
import entities.PhysicalEntity;

import java.awt.image.BufferedImage;

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

    public void reset() {
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
            	if(ent.kind == "panam" && ((Panam) ent).listOfObject.size() == 2) {
            		
            		ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();

            	    Runnable task = () -> {
            	    	for (PhysicalEntity reset : gm.resetEntities) {
            	    		if (reset instanceof Panam) {
            	    			gm.collisionBoxes.add(((Panam) reset).listOfObject.get(0).box); 
            	    			gm.collisionBoxes.add(((Panam) reset).listOfObject.get(1).box);
            	    		}
            	    		reset.reset();
            	    	}
            	    	ResultWriter.writeWinner(false, true);
            	    };

            	    scheduler.schedule(task, 5, TimeUnit.SECONDS);
            	}
            	
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
            
            if (deadEntities.size() == 1) {
            	deadEntities.clear();
            	
            	for (PhysicalEntity reset : gm.resetEntities) {
    	    		if (reset instanceof Panam) {
    	    			
    	    			gm.animatedEntities.add((Panam) reset);
                		gm.interactionBoxes.add(((Panam)reset).intrBox);
                		
    	    			try {
    	    				gm.collisionBoxes.add(((Panam) reset).listOfObject.get(0).box); 
    	    				gm.collisionBoxes.add(((Panam) reset).listOfObject.get(1).box);    	    				
    	    			} catch (IndexOutOfBoundsException e) {}
    	    		}
    	    		reset.reset();
    	    	}
            	ResultWriter.writeWinner(true, false);
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
            		if (intr != null) System.out.println(ent.kind + " INTERACTING WITH: " + intr.kind);
            		if (intr != null) switch (intr.kind) {
            		
            		case "door0": ent.exitHouse(); break;
            		case "door1": ent.setLocation(windows.get(1).getCamera().x + gm.windowValues[1][0], windows.get(1).getCamera().y + gm.windowValues[1][0], 1); break;
            		case "door2": ent.setLocation(windows.get(2).getCamera().x + gm.windowValues[1][0], windows.get(2).getCamera().y + gm.windowValues[2][0], 2);break;
            		case "box": intr.linkObj.triggerIntr(ent); ent.triggerIntr(intr.linkObj); break;
            		case "warehouse": intr.linkObj.triggerIntr(ent); ent.triggerIntr(intr.linkObj); break;
            		case "border": ent.triggerIntr(intr.linkObj); break;
            		case "animated": intr.linkObj.triggerIntr(ent); break;
            		case "winObject":
            			intr.linkObj.triggerIntr(ent); 
            			gm.collisionBoxes.remove(intr.linkObj.box);
            			break;
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
