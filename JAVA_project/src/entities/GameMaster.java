package entities;

import java.util.List;
import java.util.Queue;
import java.util.LinkedList;

import javax.imageio.ImageIO;

import java.awt.Color;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.util.ArrayList;

public class GameMaster {

    private static GameMaster instance;
    private final int STEP = 2;
    public int[][] windowValues; // rows, columns
    
    public Queue<PhysicalEntity> linkingObjects = new LinkedList<>();
    
    public List<CollisionBox> collisionBoxes = new ArrayList<>();
    public List<InteractionBox> interactionBoxes = new ArrayList<>();
    
    public List<StaticEntity> staticEntities = new ArrayList<>();
    public List<AnimatedEntity> animatedEntities = new ArrayList<>();
    public List<PhysicalEntity> physicalEntities = new ArrayList<>();
    public List<BackgroundEntity> bgEntities1 = new ArrayList<>();
    public List<BackgroundEntity> bgEntities2 = new ArrayList<>();
    
    private int[][][][] windowTileMaps;

    private GameMaster(int[][] windowValues) {
    	
    	this.windowValues = windowValues;
    	windowTileMaps = new int[][][][] {
        		new int[4][windowValues[0][1]][windowValues[0][2]],
        		new int[4][windowValues[1][1]][windowValues[1][2]],
        		new int[4][windowValues[2][1]][windowValues[2][2]]
        };
    	
    	loadImage();
    	loadStage();
    	
    }

    public static synchronized GameMaster getInstance(int[][] windowValues) {
        if (instance == null) {
            instance = new GameMaster(windowValues);
        }
        return instance;
    }
    
    public static synchronized GameMaster getInstance() {
        if (instance == null) {
            return null;
        }
        return instance;
    }
    
    private void loadStage() {
    	
    	Jason jason = Jason.getInstance(16, 2, 0, 0, 1, 1, 3, windowValues[0][0], 0);
    	animatedEntities.add(jason);
    	physicalEntities.add(jason);
    	collisionBoxes.add(jason.box);
    	interactionBoxes.add(jason.intrBox);
    	
    	Panam panam = Panam.getInstance(24, 2, 0, 0, 1, 1, STEP, windowValues[0][0], 0);
    	animatedEntities.add(panam);
    	physicalEntities.add(panam);
    	collisionBoxes.add(panam.box);
    	interactionBoxes.add(panam.intrBox);
    
    	int indexWindow = 0;
    	int xoffset = 0, yoffset = 0;
    	int x = 0, y = 0;
    	
    	for (int[][][] tilemap : windowTileMaps) {
    		
    		int sizetile = windowValues[indexWindow][0];
    		
    		y = 0;
    		
    		for (int[] row : tilemap[0]) {
    			x = 0;
    			
    			for (int element : row) {
    				
    				switch (element) {
    				
    				case 0: bgEntities1.add(new Grass(x, y, xoffset, yoffset, 1, 1, sizetile, 0)); break;
    				case 1: bgEntities1.add(new Grass(x, y, xoffset, yoffset, 1, 1, sizetile, 1)); break;
    				case 2: bgEntities1.add(new Grass(x, y, xoffset, yoffset, 1, 1, sizetile, 2)); break;
    				case 3: bgEntities1.add(new Floor(x, y, xoffset, yoffset, 2, 2, sizetile, 9)); break;
    				
    				}
    				x += 1;
    				
    			}
    			y+= 1;
    		}
    		
    		y = 0;
    		
    		for (int[] row : tilemap[1]) {
    			x = 0;
    			
    			for (int element : row) {
    				
    				switch (element) {
    				
    				case 1: bgEntities2.add(new Floor(x, y, xoffset, yoffset, 1, 1, sizetile, 0)); break;
    				case 2: bgEntities2.add(new Floor(x, y, xoffset, yoffset, 1, 1, sizetile, 1)); break;
    				case 3: bgEntities2.add(new Floor(x, y, xoffset, yoffset, 1, 1, sizetile, 2)); break;
    				case 4: bgEntities2.add(new Floor(x, y, xoffset, yoffset, 1, 1, sizetile, 3)); break;
    				case 5: bgEntities2.add(new Floor(x, y, xoffset, yoffset, 1, 1, sizetile, 4)); break;
    				case 6: bgEntities2.add(new Floor(x, y, xoffset, yoffset, 1, 1, sizetile, 5)); break;
    				case 7: bgEntities2.add(new Floor(x, y, xoffset, yoffset, 1, 1, sizetile, 6)); break;
    				case 8: bgEntities2.add(new Floor(x, y, xoffset, yoffset, 1, 1, sizetile, 7)); break;
    				case 9: bgEntities2.add(new Floor(x, y, xoffset, yoffset, 1, 1, sizetile, 8)); break;
    				case 10: bgEntities2.add(new Carpet(x, y, xoffset, yoffset, 3, 3, sizetile, 0)); break;
    				
    				}
    				x += 1;
    			}
    			y+= 1;
    		}
    		
    		y = 0;
    		boolean match;
    		
    		for (int[] row : tilemap[2]) {
    			x = 0;
    			
    			for (int element : row) {
    				
    				match = false;
    				
    				switch (element) {
    				
    				case 0: staticEntities.add(new Pine(x, (y - 1), xoffset, yoffset, 1, 2, sizetile, 0)); match = true; break;
    				case 1: staticEntities.add(new House(x, (y - 2), xoffset, yoffset, 7, 8, sizetile, 0)); match = true; break;
    				case 2: staticEntities.add(new House(x, (y - 2), xoffset, yoffset, 7, 8, sizetile, 1)); match = true; break;
    				case 3: staticEntities.add(new House(x, (y - 2), xoffset, yoffset, 5, 8, sizetile, 2)); match = true; break;
    				case 4:
    					StaticEntity warehouse = new Warehouse((x - 2), (y - 4), xoffset, yoffset, 4, 5, sizetile, 0);
    					staticEntities.add(warehouse);
    					linkingObjects.add(warehouse);
    					match = true;
    					break;
    				case 5:
    					StaticEntity well = new Well(x, y, xoffset, yoffset, 2, 2, sizetile, 0);
    					staticEntities.add(well);
    					linkingObjects.add(well); linkingObjects.add(well); linkingObjects.add(well); linkingObjects.add(well);
    					match = true;
    					break;
    				case 6: staticEntities.add(new Bed(x, y, xoffset, yoffset, 1, 2, sizetile, 0)); match = true; break;
    				case 7: staticEntities.add(new Desk(x, y, xoffset, yoffset, 1, 1, sizetile, 0)); match = true; break;
    				case 8: 
    					StaticEntity box = new Box(x, y, xoffset, yoffset, 1, 1, sizetile, 0);
    					staticEntities.add(box);
    					linkingObjects.add(box);
    					match = true;
    					break;
    				case 9: staticEntities.add(new Stuff(x, y, xoffset, yoffset, 2, 2, sizetile, 0)); match = true; break;
    				
    				// LACHI
    				case 10: staticEntities.add(new Stuff(x, y, xoffset, yoffset, 1, 1, sizetile, 1, 1)); match = true; break;	// Erba alta
    				case 11: staticEntities.add(new Stuff(x, y, xoffset, yoffset, 1, 1, sizetile, 2, 1)); match = true; break;	// Mattoni
    				
    				}
    				
    				if (match) {    				
    					physicalEntities.add(staticEntities.getLast());
    					collisionBoxes.add(staticEntities.getLast().box);
    				}
    				x += 1;
    			}
    			y+= 1;
    		}
    		
    		y = 0;
    		match = false;
    		
    		for (int[] row : tilemap[3]) {
    			x = 0;
    			
    			
    			for (int element : row) {
    				
    				match = false;
    				
    				switch (element) {
    				
    				case 0: interactionBoxes.add(new InteractionBox(x, y, xoffset, yoffset, 1, 1, sizetile, "door0")); match = true; break;
    				case 1: interactionBoxes.add(new InteractionBox(x, y, xoffset, yoffset, 1, 1, sizetile, "door1")); match = true; break;
    				case 3: interactionBoxes.add(new InteractionBox(x, y, xoffset, yoffset, 1, 1, sizetile, "door2")); match = true; break;
    				case 2: interactionBoxes.add(new InteractionBox(x, y, xoffset, yoffset, 1, 1, sizetile, "warehouse", linkingObjects.remove())); match = true; break;
    				case 4: interactionBoxes.add(new InteractionBox(x, y, xoffset, yoffset, 1, 1, sizetile, "box", linkingObjects.remove())); match = true; break;
    				
    				}
    				
    				if (match) {    				
    					physicalEntities.add(staticEntities.getLast());
    					collisionBoxes.add(staticEntities.getLast().box);
    				}
    				x += 1;
    			}
    			y+= 1;
    		}
    		
    		xoffset += x * sizetile;
    		yoffset += y * sizetile;

    		indexWindow+= 1;
    	}

    	
    }
    
    public boolean checkCollision(CollisionBox box, AnimatedEntity ent, int num_window) {
    	
    	if ( box.left <= windowValues[num_window][1] ) return true;
    	
    	for (CollisionBox col : collisionBoxes) {
    		
    		/*
    		if (box.id == 0) {
    			System.out.println("BOX: "+ box.left + " - " + box.right + " / " + box.top + " - " + box.bottom);
    			System.out.println("COL: "+ col.left + " - " + col.right + " / " + col.top + " - " + col.bottom);
    		}
    		*/
    		
    		if (col.slow == 1){
    			if ( col.left < box.left && box.left < col.right || col.left < box.right && box.right < col.right ) {
            		if ( col.top < box.top && box.top < col.bottom ) { ent.step = ent.slow; return false; }
            		else if ( col.top < box.bottom && box.bottom < col.bottom ) { ent.step = ent.slow; return false; }
            	}
    		} else  {
    			if ( col.left < box.left && box.left < col.right || col.left < box.right && box.right < col.right ) {
            		if ( col.top < box.top && box.top < col.bottom ) return true;
            		else if ( col.top < box.bottom && box.bottom < col.bottom ) return true;
            	}
    		}
    		
    		ent.step = ent.defaultStep;
    		
    	}
    	
		return false;
    	
    }
    
    public boolean checkInteraction(InteractionBox box, InteractionBox intr) {

    	if ( intr.left < box.left && box.left < intr.right || intr.left < box.right && box.right < intr.right ) {
    		if ( intr.top < box.top && box.top < intr.bottom ) return true;
    		else if ( intr.top < box.bottom && box.bottom < intr.bottom ) return true;
    	}
    	
		return false;
    	
    }
    
    private void loadImage() {
    	try {
    		

    		for (int j = 0; j < 3; j++) {    			
    			for (int i = 0; i < 4; i++) {
    				
    				BufferedImage image = ImageIO.read(getClass().getResourceAsStream("/sprites/tilemap/"+(j+1)+"/"+i+".png"));
    				
    				int width = image.getWidth();
    				int height = image.getHeight();
    				
    				for (int y = 0; y < height; y++) {
    					
    					int[] temp = windowTileMaps[j][i][y];
    					
    					for (int x = 0; x < width; x++) {
    						
    						int rgb = image.getRGB(x, y);
    						Color color = new Color(rgb, true);
    						
    						int red = color.getRed();
    						int green = color.getGreen();
    						int blue = color.getBlue();
    						int alpha = color.getAlpha();
    						
    						switch (i) {
    						
    						case 0:
    							
    							if (alpha != 0 && red == 37 && green == 138 && blue == 0) temp[x] = 0; // GRASS 0
    							else if (alpha != 0 && red == 138 && green == 75 && blue == 0) temp[x] = 3; // HOUSE FLOOR - FLOOR 9
    							else temp[x] = -1;
    							break;
    							
    						case 1:
    							
    							if (alpha != 0 && red == 178 && green == 10 && blue == 38) temp[x] = 10; // CARPET 0
    							else if(alpha != 0 && red == 255 && green == 255 && blue == 255) temp[x] = 1; // FLOOR 1 - MAP
    							else if(alpha != 0 && red == 94 && green == 94 && blue == 94) temp[x] = 5;	// FLOOR RIGHT
    							else if(alpha != 0 && red == 154 && green == 153 && blue == 153) temp[x] = 7; // FLOOR TOP - RIGHT
    							else if(alpha != 0 && red == 172 && green == 172 && blue == 172) temp[x] = 2; // FLOOR TOP
    							else if(alpha != 0 && red == 37 && green == 37 && blue == 37) temp[x] = 6; // FLOOR TOP - LEFT
    							else if(alpha != 0 && red == 0 && green == 0 && blue == 0) temp[x] = 3; // FLOOR LEFT
    							else if(alpha != 0 && red == 92 && green == 67 && blue == 67) temp[x] = 9; // BOTTOM - LEFT
    							else if(alpha != 0 && red == 97 && green == 56 && blue == 56) temp[x] = 4; // BOTTOM
    							else if(alpha != 0 && red == 146 && green == 48 && blue == 48) temp[x] = 8; // BOTTOM - RIGHT
    							break;
    							
    						case 2:
    							
    							if (alpha != 0 && red == 0 && green == 0 && blue == 0) temp[x] = 0; // PINE
    							else if (alpha != 0 && red == 176 && green == 82 && blue == 5) temp[x] = 9; // STUFF
    							else if (alpha != 0 && red == 142 && green == 66 && blue == 3) temp[x] = 8; // BOX
    							else if (alpha != 0 && red == 69 && green == 39 && blue == 4) temp[x] = 7; // DESK 0
    							else if (alpha != 0 && red == 30 && green == 210 && blue == 12) temp[x] = 6; // BED 0
    							else if (alpha != 0 && red == 67 && green == 67 && blue == 67) temp[x] = 5; // WELL
        						else if (alpha != 0 && red == 242 && green == 123 && blue == 123) temp[x] = 4; // HOUSE 3
        						else if (alpha != 0 && red == 120 && green == 120 && blue == 120) temp[x] = 3; // HOUSE 2
        						else if (alpha != 0 && red == 178 && green == 178 && blue == 178) temp[x] = 2; // HOUSE 1
        						else if (alpha != 0 && red == 71 && green == 42 && blue == 42) temp[x] = 1; // HOUSE 0
    							
    							// LACHI
        						else if (alpha != 0 && red == 9 && green == 103 && blue == 13) temp[x] = 10; // GRASS
        						else if (alpha != 0 && red == 142 && green == 3 && blue == 3) temp[x] = 11; // MATTONI 
        						else temp[x] = -1;
    							break;
    							
    						case 3:
    							
    							if (alpha != 0 && red == 255 && green == 255 && blue == 255) temp[x] = 0; // DOOR 0
    							else if (alpha != 0 && red == 0 && green == 0 && blue == 0) temp[x] = 1; // DOOR 1
    							else if (alpha != 0 && red == 168 && green == 168 &&  blue == 168) temp[x] = 2; // WAREHOUSE
    							else if(alpha != 0 && red == 133 && green == 133 && blue == 133) temp[x] = 3; // HOUSE RIGHT
    							else if(alpha != 0 && red == 219 && green == 219 && blue == 219) temp[x] = 5; // HOUSE DOWN 
    							else if (alpha != 0 && red == 142 && green == 66 && blue == 3) temp[x] = 4; // BREAK BOX
    							else temp[x] = -1;
    							break;
    							
    						}
    					}
    					
    				}
    			}
            }

        } catch (IOException e) {
            e.printStackTrace();
        }
    	
    }
	
}
