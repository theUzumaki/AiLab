package main;

import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

import org.json.JSONException;
import org.json.JSONObject;

import java.awt.AWTException;
import java.util.ArrayList;

import entities.AnimatedEntity;
import entities.GameMaster;
import entities.InteractionBox;
import entities.Panam;
import entities.PhysicalEntity;

public class GameLoop implements Runnable {
	
    private boolean running = false;
	
    // Main objects
    private final GameMaster gm;
    private final List<Game> windows;
    
    
    private ImageSaver saver = new ImageSaver();
    private Thread saverThread = new Thread(saver);
    
    public boolean killerWin = false, victimWin = false, end_game = false, timer_finished = false;
    
    private List<AnimatedEntity> deadEntities= new ArrayList<>();
    
    long start_game;
    boolean waiting = false;
    
    ComunicationAI com;

    public GameLoop(List<Game> views) {
        gm = GameMaster.getInstance();
        windows = views;
        running = true;
        com = new ComunicationAI(windows, gm.animatedEntities, this);
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
        
        /* new Thread(() -> {
        	saver.detection();
        }).start(); */
        
        try {
			Thread.sleep(5000);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
        
        start_game = System.currentTimeMillis();

        while (running) {
            long start = System.currentTimeMillis();

            int num_window = 0;
            
            AnimatedEntity panam = gm.animatedEntities.getLast();
            long elapsedTime = System.currentTimeMillis() - start_game;
            
            com.writeGameState("killer");
            com.writeGameState("victim");
            
            
            JSONObject killerObj = com.readAIAction("killer");
            JSONObject victimObj = com.readAIAction("victim");
            
            if (killerObj != null) {
            	new Thread(() -> {
            		try {
            			com.pressKey(killerObj.getString("agent"), killerObj.getString("action"));
            		} catch (JSONException | AWTException | InterruptedException e) {
            			// TODO Auto-generated catch block
            			e.printStackTrace();
            		}
            	}).start();            	
            }
            
            if (victimObj != null) {
            	new Thread(() -> {
            		try {
            			com.pressKey(victimObj.getString("agent"), victimObj.getString("action"));
            		} catch (JSONException | AWTException | InterruptedException e) {
            			// TODO Auto-generated catch block
            			e.printStackTrace();
            		}
            	}).start();            	
            }
            
            if (elapsedTime > 3 * 60 * 1000) {
            	timer_finished = true;
            	
            	for (PhysicalEntity reset : gm.resetEntities) {
    	    		if (reset instanceof Panam) {
    	    			try {
    	    				gm.collisionBoxes.add(((Panam) reset).listOfObject.get(0).box); 
    	    				gm.collisionBoxes.add(((Panam) reset).listOfObject.get(1).box);    	    				
    	    			} catch (IndexOutOfBoundsException e) {}
    	    		}
    	    		reset.reset();
    	    	}
            	
            	timer_finished = false;
        		start_game = System.currentTimeMillis();
            
            } else if (panam.kind == "panam" && ((Panam) panam).listOfObject.size() == 2) {
            	start_game = System.currentTimeMillis();
        		end_game = true;
        		
        		ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();
        		
        		Runnable task = () -> {
        			
        			killerWin = false;
        			victimWin = true;
        			
        			try {
    					Thread.sleep(5000);
    				} catch (InterruptedException e) {
    					// TODO Auto-generated catch block
    					e.printStackTrace();
    				}
        			
        			for (PhysicalEntity reset : gm.resetEntities) {
        				if (reset instanceof Panam) {
        					try {
        	    				gm.collisionBoxes.add(((Panam) reset).listOfObject.get(0).box); 
        	    				gm.collisionBoxes.add(((Panam) reset).listOfObject.get(1).box);    	    				
        	    			} catch (IndexOutOfBoundsException e) {}
        				}
        				reset.reset();
        			}
        			
        			killerWin = false;
        			victimWin = false;
        			
        			start_game = System.currentTimeMillis();
        			end_game = false;
        		};
        		
        		scheduler.schedule(task, 5, TimeUnit.SECONDS);
            } else if (deadEntities.size() >= 1) {
            	deadEntities.clear();
            	
            	killerWin = true;
            	victimWin = false;
            	
            	for (PhysicalEntity reset : gm.resetEntities) {
    	    		if (reset instanceof Panam) {
                		gm.interactionBoxes.add(((Panam)reset).intrBox);
                		
    	    			try {
    	    				gm.collisionBoxes.add(((Panam) reset).listOfObject.get(0).box); 
    	    				gm.collisionBoxes.add(((Panam) reset).listOfObject.get(1).box);    	    				
    	    			} catch (IndexOutOfBoundsException e) {}
    	    		}
    	    		reset.reset();
    	    	}
            	
            	killerWin = false;
    			victimWin = false;
    			
    			start_game = System.currentTimeMillis();
            }
            
            // Update all entities with input from any view
            for (Game window : windows) {
            	
            	for (AnimatedEntity dead : deadEntities) {
            		gm.interactionBoxes.remove(dead.intrBox);
            	}
            	
                for (AnimatedEntity ent : gm.animatedEntities) {
                	
                    if (ent.y != -1000) ent.memorizeValues();
                    
                    if (ent.stage == num_window) {
                    	ent.update(window.getKeyManager().keys);
                    	
                		if(ent.aligned || ent.interaction) {
                			if (ent.kind == "jason") {
                				com.writeAck("killer");         
                			} else {
                				com.writeAck("victim");
                			}
                			
                		}
                    }
                    
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
            		case "box": intr.linkObj.triggerIntr(ent); ent.triggerIntr(intr.linkObj); 
            			if(ent.kind == "jason")
            				gm.interactionBoxes.remove(intr);
            			break;
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
