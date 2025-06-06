package main;

import java.util.List;

import javax.swing.SwingUtilities;

import org.json.JSONException;
import org.json.JSONObject;

import java.awt.AWTException;
import java.awt.image.BufferedImage;
import java.lang.reflect.InvocationTargetException;
import java.util.ArrayList;

import entities.AnimatedEntity;
import entities.GameMaster;
import entities.InteractionBox;
import entities.Panam;
import entities.PhysicalEntity;

public class GameLoop implements Runnable {
	
    private boolean running = false;
	
    // Main objects
    public final GameMaster gm;
    private final List<Game> windows;
    
    
    private ImageSaver saver = new ImageSaver();
    private Thread saverThread = new Thread(saver);
    
    int map = 0;
    
    public boolean killerWin = false, victimWin = false, end_game = false, timer_finished = false;
    
    private List<AnimatedEntity> deadEntities= new ArrayList<>();
    
    long start_game;
    boolean send_killer_ack = false;
    boolean send_victim_ack = false;
    
    int cont1 = 0;
    int cont2 = 0;
    int cont3 = 0;
    
    public JSONObject killerObj;
    public JSONObject victimObj;
    
    ComunicationAI com;

    public GameLoop(List<Game> views, int map) {
        gm = GameMaster.getInstance();
        windows = views;
        running = true;
        this.map = map;
        com = new ComunicationAI(windows, gm.animatedEntities, this);
    }

    public void reset() {
        running = false;
    }
    
    private boolean toggle = false;
    private int lastTrigger = -1;
    
    public void updateLocationIfNeeded(int cont1, int cont2, int cont3) {
        int sum = cont1 + cont2 + cont3;

		if (sum % 10 == 0 && sum != lastTrigger) {
            lastTrigger = sum;

			if (toggle) {
                gm.animatedEntities.getLast().setLocation(
                    windows.get(1).getCamera().x + gm.windowValues[1][0],
                    windows.get(1).getCamera().y + gm.windowValues[1][0],
                    1
                );
            } else {
                gm.animatedEntities.getLast().setLocation(
                    windows.get(2).getCamera().x + gm.windowValues[1][0],
                    windows.get(2).getCamera().y + gm.windowValues[2][0],
                    2
                );
            }

            toggle = !toggle;
        }
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
        
        gm.animatedEntities.getLast().setLocation( windows.get(map).getCamera().x + gm.windowValues[map][0] + 20, windows.get(map).getCamera().y + gm.windowValues[map][0] + 20, map);

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
            
            if (elapsedTime > 3 * 60 * 1000) {
            	timer_finished = true;
            	
            	cont1 += 1;
            	System.out.println("Game finished " + cont1);
            	
            	com.writeAck("killer");
            	com.writeAck("victim");
            	
            	com.writeGameState("killer", "victim");
            	
                
                System.out.println("game state writed");
            	
            	for (PhysicalEntity reset : gm.resetEntities) {
    	    		if (reset instanceof Panam) {
    	    			try {
    	    				gm.collisionBoxes.add(((Panam) reset).listOfObject.get(0).box); 
    	    				gm.collisionBoxes.add(((Panam) reset).listOfObject.get(1).box);    	    				
    	    			} catch (IndexOutOfBoundsException e) {}
    	    		}
    	    		reset.reset();
    	    	}
            	
            	try {
					Thread.sleep(1000);
				} catch (InterruptedException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
            	

                gm.animatedEntities.getLast().setLocation( windows.get(map).getCamera().x + gm.windowValues[map][0] + 20, windows.get(map).getCamera().y + gm.windowValues[map][0] + 20,map);
                
            	timer_finished = false;
        		start_game = System.currentTimeMillis();
            
            } else if (panam.kind == "panam" && ((Panam) panam).listOfObject.size() == 2) {
            	if(!end_game) {
            		start_game = System.currentTimeMillis();            		
            	}
            	
        		end_game = true;
        		
        		if (elapsedTime > 60 * 1000) {
        			killerWin = false;
        			victimWin = true;
        			
        			cont2 += 1;
        			System.out.println("Victim win " + cont2);
        			
        			com.writeAck("killer");
                	com.writeAck("victim");
        			
        			com.writeGameState("killer", "victim");
        			
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
        			end_game = false;
        			
        			try {
						Thread.sleep(1000);
					} catch (InterruptedException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}

        	        gm.animatedEntities.getLast().setLocation( windows.get(map).getCamera().x + gm.windowValues[map][0] + 20, windows.get(map).getCamera().y + gm.windowValues[map][0] + 20,map);
        	        
        			start_game = System.currentTimeMillis();
        		}
            } else if (deadEntities.size() >= 1) {
            	deadEntities.clear();
            	
            	killerWin = true;
            	victimWin = false;
            	
            	cont3 += 1;
            	System.out.println("Killer win " + cont3);
            	
            	com.writeAck("killer");
            	com.writeAck("victim");
            	
            	com.writeGameState("killer", "victim");
            	
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

    			try {
					Thread.sleep(1000);
				} catch (InterruptedException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}

    	        gm.animatedEntities.getLast().setLocation( windows.get(map).getCamera().x + gm.windowValues[map][0] + 20, windows.get(map).getCamera().y + gm.windowValues[map][0] + 20,map);
    	        
    			start_game = System.currentTimeMillis();
            }
            
            killerObj = com.readAIAction("killer");
            victimObj = com.readAIAction("victim");
            
            if (killerObj != null) {
            	new Thread(() -> {
            		try {
						com.pressKey(killerObj.getString("agent"), killerObj.getString("action"));
					} catch (JSONException | AWTException | InterruptedException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}
            	}).start();;            	
            }
            
            if (victimObj != null) {
            	new Thread(() -> {
            		try {
						com.pressKey(victimObj.getString("agent"), victimObj.getString("action"));
					} catch (JSONException | AWTException | InterruptedException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}
            	}).start();;            	
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
                    	
                		if(ent.aligned || ent.interaction || ent.hidden) {
                			
                			try {
								SwingUtilities.invokeAndWait(() -> {
									BufferedImage img = windows.get(ent.stage).captureFrameCentered(ent.x, ent.y);
									saver.saveImage(img, ent.kind);
								});
							} catch (InvocationTargetException | InterruptedException e) {
								// TODO Auto-generated catch block
								e.printStackTrace();
							}
                			
                			if (ent.kind == "jason") {
                				com.writeGameState("killer");
                				com.writeAck("killer");
                			} else {
                				com.writeGameState("victim");
                				com.writeAck("victim");
                			}
                		}
                    
                    if (ent.y != -1000) { ent.box.updatePosition(ent.x, ent.y); ent.intrBox.updatePosition(ent.x, ent.y); }

                    InteractionBox intr = null;
                    
                    if (ent.interaction && ent.y == -1000) {

                    	ent.triggerIntr(null);
                    	continue;
                    	
                    } else if (ent.interaction) {
	            		
	            		for (InteractionBox intr2 : gm.interactionBoxes) {
	            			if(ent.kind == "panam" && intr2.kind == "animated") {continue;}
	            			if (gm.checkInteraction(ent.intrBox, intr2)) {
	            				intr = intr2;
	            				break; 
	            			}
	            		}
	            			
            			
            		}
                    /*
                    else if (ent.interacting) {
            			
            			for (AnimatedEntity ent2 : gm.animatedEntities) {
            				if(ent.kind == "panam" && ent2.kind == "jason") {continue;}
            				if ( gm.checkInteraction(ent.intrBox, ent2.intrBox) ) { intr = ent2.intrBox; break; }
            			}
            			
            		}
            		*/
                    
                    if (intr != null) {
                    	// System.out.println(ent.kind + " has interacted with: " + intr.kind); 
                    	ent.interaction = false;
                    }
            		if (intr != null) switch (intr.kind) {
            		
            		
            		case "door0": System.out.println(ent.kind + "EXIT"); ent.exitHouse(); break;
            		case "door1": System.out.println(ent.kind + "HOUSE1"); ent.setLocation(windows.get(1).getCamera().x + gm.windowValues[1][0], windows.get(1).getCamera().y + gm.windowValues[1][0], 1); break;
            		case "door2": System.out.println(ent.kind + "HOUSE2"); ent.setLocation(windows.get(2).getCamera().x + gm.windowValues[1][0], windows.get(2).getCamera().y + gm.windowValues[2][0], 2);break;
            		case "box": ent.triggerIntr(intr.linkObj); 
            			if(ent.kind == "jason")
            				gm.interactionBoxes.remove(intr);
            			break;
            		case "warehouse": ent.triggerIntr(intr.linkObj); break;
            		case "border":
            			ent.triggerIntr(intr.linkObj); 
            			break;
            		case "animated": 
            			System.out.println(ent.kind + " INTERACTING WITH: " + intr.kind);
            			intr.linkObj.triggerIntr(ent); 
            			break;
            		case "winObject":
            			System.out.println(ent.kind + " INTERACTING WITH: " + intr.kind);
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
                }
                num_window++;
            }
            
            for(Game view: windows) {
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
