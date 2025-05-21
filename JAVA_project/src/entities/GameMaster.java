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
    public int[][] windowValues; // tile, rows, columns
    public int[][] windowBorders;
    
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
        windowBorders = new int[][] {
        	{
        		windowValues[0][0],
        		windowValues[0][0] * ( windowValues[0][2] - 1),
        		windowValues[0][0],
        		windowValues[0][0] * ( windowValues[0][1] - 1)
        		
        	},
        	
        	{
        		windowValues[0][0] * windowValues[0][2],
        		windowValues[0][0] * windowValues[0][2] + windowValues[1][0] * windowValues[1][2],
        		windowValues[0][0] * windowValues[0][1],
        		windowValues[0][0] * windowValues[0][1] + windowValues[1][0] * windowValues[1][1]
        		
        	},
        	
        	{
        		windowValues[0][0] * windowValues[0][2] + windowValues[1][0] * windowValues[1][2],
        		windowValues[0][0] * windowValues[0][2] + windowValues[1][0] * windowValues[1][2] + windowValues[2][0] * windowValues[2][2],
        		windowValues[0][0] * windowValues[0][1] + windowValues[1][0] * windowValues[1][1],
        		windowValues[0][0] * windowValues[0][1] + windowValues[1][0] * windowValues[1][1] + windowValues[2][0] * windowValues[2][1]
        		
        	}
        	
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
    				case 10: bgEntities2.add(new Carpet(x, y, xoffset, yoffset, 4, 4, sizetile, 0)); break;
    				case 11: bgEntities2.add(new Floor(x, y, xoffset, yoffset, 1, 1, sizetile, 10)); break;
    				case 12: bgEntities2.add(new Floor(x, y, xoffset, yoffset, 1, 1, sizetile, 11)); break;
    				case 13: bgEntities2.add(new Floor(x, y, xoffset, yoffset, 1, 1, sizetile, 12)); break;
    				case 14: bgEntities2.add(new Floor(x, y, xoffset, yoffset, 1, 1, sizetile, 13)); break;
    				case 15: bgEntities2.add(new Grass(x, (y - 1), xoffset, yoffset, 1, 2, sizetile, 1)); break;
    				case 16: bgEntities2.add(new Door(x, (y - 1), xoffset, yoffset, 1, 2, sizetile, 0)); break;
    				case 17: bgEntities2.add(new Door(x, (y - 1), xoffset, yoffset, 1, 2, sizetile, 1)); break;
    				
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
    				case 6: 
    					StaticEntity bedGreen = new Bed(x, y, xoffset, yoffset, 1, 2, sizetile, 0);
    					staticEntities.add(bedGreen);
    					linkingObjects.add(bedGreen);
    					match = true; 
    					break;
    				case 32: staticEntities.add(new Bed(x, y, xoffset, yoffset, 1, 2, sizetile, 1)); match = true; break;
    				case 7: staticEntities.add(new Interior(x, y, xoffset, yoffset, 1, 1, sizetile, 0, 1, 1)); match = true; break;
    				case 8: 
    					StaticEntity box = new Box(x, y, xoffset, yoffset, 1, 1, sizetile, 0);
    					staticEntities.add(box);
    					linkingObjects.add(box);
    					match = true;
    					break;
    				case 9: staticEntities.add(new Stuff(x, y, xoffset, yoffset, 2, 2, sizetile, 0)); match = true; break;
    				
    				// LACHI
    				case 10: staticEntities.add(new Stuff(x, y, xoffset, yoffset, 1, 1, sizetile, 1)); match = true; break;	// BRICKS
    				case 11: staticEntities.add(new SlowObj(x, y, xoffset, yoffset, 1, 1, sizetile, 0)); match = true; break;	// HIGH GRASS
    				case 12: staticEntities.add(new SlowObj(x, y, xoffset, yoffset, 1, 1, sizetile, 1)); match = true; break;	// POND
    				case 13: 
    					StaticEntity PondB = new Border(x, y, xoffset, yoffset, 1, 1, sizetile, 0);
    					staticEntities.add(PondB);
    					linkingObjects.add(PondB); match = true; break;
    				case 14: 
    					StaticEntity PondBDX = new Border(x, y, xoffset, yoffset, 1, 1, sizetile, 1);
    					staticEntities.add(PondBDX);
    					linkingObjects.add(PondBDX); match = true; break;
    				case 15:
    					StaticEntity PondBSX = new Border(x, y, xoffset, yoffset, 1, 1, sizetile, 2);
    					staticEntities.add(PondBSX);
    					linkingObjects.add(PondBSX); match = true; break;
    				case 16:
    					StaticEntity PondDX = new Border(x, y, xoffset, yoffset, 1, 1, sizetile, 3);
    					staticEntities.add(PondDX);
    					linkingObjects.add(PondDX); match = true; break;
    				case 17:
    					StaticEntity PondSX = new Border(x, y, xoffset, yoffset, 1, 1, sizetile, 4);
    					staticEntities.add(PondSX);
    					linkingObjects.add(PondSX); match = true; break;
    				case 18:
    					StaticEntity PondT = new Border(x, y, xoffset, yoffset, 1, 1, sizetile, 5);
    					staticEntities.add(PondT);
    					linkingObjects.add(PondT); match = true; break;
    				case 19:
    					StaticEntity PondTDX = new Border(x, y, xoffset, yoffset, 1, 1, sizetile, 6);
    					staticEntities.add(PondTDX);
    					linkingObjects.add(PondTDX); match = true; break;
    				case 20: 
    					StaticEntity PondTSX = new Border(x, y, xoffset, yoffset, 1, 1, sizetile, 7);
    					staticEntities.add(PondTSX);
    					linkingObjects.add(PondTSX); match = true; break;
    				case 21: staticEntities.add(new Interior(x, y, xoffset, yoffset, 1, 2, sizetile, 1, 1, 2)); match = true; break;
    				case 22: staticEntities.add(new Interior(x, y, xoffset, yoffset, 1, 2, sizetile, 2, 1, 2)); match = true; break;
    				case 23: staticEntities.add(new Interior(x, y, xoffset, yoffset, 1, 1, sizetile, 3, 1, 1)); match = true; break;
    				case 24: staticEntities.add(new Interior(x, y, xoffset, yoffset, 1, 1, sizetile, 4, 1, 1)); match = true; break;
    				case 25: staticEntities.add(new Interior(x, y, xoffset, yoffset, 1, 1, sizetile, 5, 1, 1)); match = true; break;
    				case 26: staticEntities.add(new Interior(x, y, xoffset, yoffset, 1, 1, sizetile, 6, 1, 1)); match = true; break;
    				case 27: staticEntities.add(new Interior(x, y, xoffset, yoffset, 2, 1, sizetile, 7, 2, 1)); match = true; break;
    				case 28: 
    					StaticEntity bigChest = new Chest(x, y, xoffset, yoffset, 2, 1, sizetile, 0, 2, 1);
    					staticEntities.add(bigChest);
    					linkingObjects.add(bigChest); linkingObjects.add(bigChest);
    					match = true; 
    					break;
    				case 29:
    					StaticEntity chest = new Chest(x, y, xoffset, yoffset, 1, 1, sizetile, 1, 1, 1);
    					staticEntities.add(chest); 
    					linkingObjects.add(chest);
    					match = true; 
    					break;
    				case 30: staticEntities.add(new Interior(x, y, xoffset, yoffset, 2, 2, sizetile, 10, 2, 2)); match = true; break;
    				case 31: staticEntities.add(new Interior(x, y, xoffset, yoffset, 2, 2, sizetile, 11, 2, 2)); match = true; break;
    				case 33:
    					StaticEntity battery = new WinnerObject(x, y, xoffset, yoffset, 1, 1, sizetile, 0);
    					staticEntities.add(battery); 
    					linkingObjects.add(battery);
    					match = true; 
    					break;
    				case 34:
    					StaticEntity phone = new WinnerObject(x, y, xoffset, yoffset, 1, 1, sizetile, 1);
    					staticEntities.add(phone); 
    					linkingObjects.add(phone);
    					match = true; 
    					break;
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
    		
    		for (int[] row : tilemap[3]) {
    			x = 0;
    			
    			
    			for (int element : row) {
    				
    				match = false;
    				
    				switch (element) {
    				
    				case 0: interactionBoxes.add(new InteractionBox(x, y, xoffset, yoffset, 1, 1, sizetile, "door0")); break;
    				case 1: interactionBoxes.add(new InteractionBox(x, y, xoffset, yoffset, 1, 1, sizetile, "door1")); break;
    				case 3: interactionBoxes.add(new InteractionBox(x, y, xoffset, yoffset, 1, 1, sizetile, "door2")); break;
    				case 2: interactionBoxes.add(new InteractionBox(x, y, xoffset, yoffset, 1, 1, sizetile, "warehouse", linkingObjects.remove())); break;
    				case 4: interactionBoxes.add(new InteractionBox(x, y, xoffset, yoffset, 1, 1, sizetile, "box", linkingObjects.remove())); break;
    				case 6: interactionBoxes.add(new InteractionBox(x, y, xoffset, yoffset, 1, 1, sizetile, "border", linkingObjects.remove())); break;
    				case 7: interactionBoxes.add(new InteractionBox(x, y, xoffset, yoffset, 1, 1, sizetile, "winObject", linkingObjects.remove())); break;
    				
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
    
    public boolean checkLimit(CollisionBox box, int num_window) {
    	
    	int window_left = windowBorders[num_window][0];
    	int window_right = windowBorders[num_window][1];
    	int window_top = windowBorders[num_window][2];
    	int window_bottom = windowBorders[num_window][3];
    	
    	/*
    	System.out.println("LEFT: " + box.left + " window: " + window_left);
    	System.out.println("RIGHT: " + box.right + " window: " + window_right);
    	System.out.println("TOP: " + box.top + " window: " + window_top);
    	System.out.println("BOTTOM: " + box.bottom + " window: " + window_bottom);
    	*/
    	
    	if ( box.left < window_left) return true;
    	else if ( box.right > window_right ) return true;
    	else if ( box.top < window_top ) return true;
    	else if ( box.bottom > window_bottom ) return true;
    	
    	return false;
    }
    
    public boolean checkCollision(CollisionBox box, AnimatedEntity ent) {
    	
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
    							else if(alpha != 0 && red == 141 && green == 141 && blue == 141) temp[x] = 11; // BDX
    							else if(alpha != 0 && red == 141 && green == 141 && blue == 145) temp[x] = 12; // BSX
    							else if(alpha != 0 && red == 141 && green == 141 && blue == 150) temp[x] = 13; // TDX
    							else if(alpha != 0 && red == 141 && green == 141 && blue == 155) temp[x] = 14; // TSX
    							else if (alpha != 0 && red == 0 && green == 82 && blue == 39) temp[x] = 15; // GRASS /PINE 0
    							else if(alpha != 0 && red == 255 && green == 0 && blue == 236) temp[x] = 16; // DOOR RIGHT
    							else if(alpha != 0 && red == 105 && green == 0 && blue == 97) temp[x] = 17; // DOOR LEFT
    							break;
    							
    						case 2:
    							
    							if (alpha != 0 && red == 0 && green == 0 && blue == 0) temp[x] = 0; // PINE
    							else if (alpha != 0 && red == 176 && green == 82 && blue == 5) temp[x] = 9; // STUFF
    							else if (alpha != 0 && red == 142 && green == 66 && blue == 3) temp[x] = 8; // BOX
    							else if (alpha != 0 && red == 69 && green == 39 && blue == 4) temp[x] = 7; // DESK 0
    							else if (alpha != 0 && red == 30 && green == 210 && blue == 12) temp[x] = 6; // BED 0
    							else if (alpha != 0 && red == 161 && green == 210 && blue == 12) temp[x] = 32; // BED 1
    							else if (alpha != 0 && red == 67 && green == 67 && blue == 67) temp[x] = 5; // WELL
        						else if (alpha != 0 && red == 242 && green == 123 && blue == 123) temp[x] = 4; // HOUSE 3
        						else if (alpha != 0 && red == 120 && green == 120 && blue == 120) temp[x] = 3; // HOUSE 2
        						else if (alpha != 0 && red == 178 && green == 178 && blue == 178) temp[x] = 2; // HOUSE 1
        						else if (alpha != 0 && red == 71 && green == 42 && blue == 42) temp[x] = 1; // HOUSE 0
    							
    							// LACHI
        						else if (alpha != 0 && red == 142 && green == 3 && blue == 3) temp[x] = 10; // MATTONI 
        						else if (alpha != 0 && red == 8 && green == 103 && blue == 13) temp[x] = 11; // GRASS
        						else if (alpha != 0 && red == 250 && green == 61 && blue == 142) temp[x] = 12; // POND
        						else if (alpha != 0 && red == 3 && green == 61 && blue == 143) temp[x] = 13; // POND B
        						else if (alpha != 0 && red == 3 && green == 61 && blue == 144) temp[x] = 14; // POND BDX
        						else if (alpha != 0 && red == 3 && green == 61 && blue == 145) temp[x] = 15; // POND BSX
        						else if (alpha != 0 && red == 3 && green == 61 && blue == 146) temp[x] = 16; // POND DX
        						else if (alpha != 0 && red == 3 && green == 61 && blue == 147) temp[x] = 17; // POND SX
        						else if (alpha != 0 && red == 3 && green == 61 && blue == 148) temp[x] = 18; // POND T
        						else if (alpha != 0 && red == 3 && green == 61 && blue == 149) temp[x] = 19; // POND TDX
        						else if (alpha != 0 && red == 3 && green == 61 && blue == 150) temp[x] = 20; // POND TSX
    							
    							// Interior
        						else if(alpha != 0 && red == 174 && green == 232 && blue == 132) temp[x] = 21; // SCAFFALE
        						else if(alpha != 0 && red == 72 && green == 90 && blue == 59) temp[x] = 22; // SCAFFALE BELLO
        						else if(alpha != 0 && red == 4 && green == 20 && blue == 69) temp[x] = 23; // Tavolo
        						else if(alpha != 0 && red == 210 && green == 29 && blue == 181) temp[x] = 24; // Sedia a destra
        						else if(alpha != 0 && red == 159 && green == 52 && blue == 142) temp[x] = 25; // Sedia a sinistra
        						else if(alpha != 0 && red == 62 && green == 69 && blue == 4) temp[x] = 26; // Panchina
        						else if(alpha != 0 && red == 0 && green == 199 && blue == 255) temp[x] = 27; // Panca Lunga
        						else if(alpha != 0 && red == 126 && green == 89 && blue == 46) temp[x] = 28; // Scrigno lungo
        						else if(alpha != 0 && red == 138 && green == 75 && blue == 0) temp[x] = 29; // Scrigno
        						else if(alpha != 0 && red == 159 && green == 152 && blue == 61) temp[x] = 30; // Taovlo con sedia a sinistra
        						else if(alpha != 0 && red == 210 && green == 197 && blue == 29) temp[x] = 31; // Tavolo con sedia a destra
        						else if(alpha != 0 && red == 158 && green == 0 && blue == 0) temp[x] = 33; // Phone
        						else if(alpha != 0 && red == 93 && green == 33 && blue == 33) temp[x] = 34; // Battery
    							
        						else temp[x] = -1;
    							break;
    							
    						case 3:
    							
    							if (alpha != 0 && red == 255 && green == 255 && blue == 255) temp[x] = 0; // DOOR 0
    							else if (alpha != 0 && red == 0 && green == 0 && blue == 0) temp[x] = 1; // DOOR 1
    							else if (alpha != 0 && red == 168 && green == 168 &&  blue == 168) temp[x] = 2; // WAREHOUSE
    							else if(alpha != 0 && red == 133 && green == 133 && blue == 133) temp[x] = 3; // HOUSE RIGHT
    							else if(alpha != 0 && red == 219 && green == 219 && blue == 219) temp[x] = 5; // HOUSE DOWN 
    							else if (alpha != 0 && red == 142 && green == 66 && blue == 3) temp[x] = 4; // BREAK BOX
    							else if (alpha != 0 && red == 3 && green == 61 && blue == 148) temp[x] = 6; // BORDER
    							else if (alpha != 0 && red == 167 && green == 255 && blue == 0) temp[x] = 7; // WIN OBJECT 
    							
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
