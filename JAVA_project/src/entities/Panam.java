package entities;

import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.IOException;

import javax.imageio.ImageIO;

public class Panam extends AnimatedEntity{
	
	private int timer = 0, dash = 50, hiddenTimer = 1200, moveTimer = 0;
	private boolean hidden;
	private PhysicalEntity interactingObj;
	
	private int direction, interval;
	
	public Panam(int x, int y, int xoffset, int yoffset, int width, int heigth, int STEP, int TILE, int selector) {
		
		super(x, y, xoffset, yoffset, width, heigth, STEP, TILE, selector, "panam");
		box = new CollisionBox(x, y, xoffset, yoffset, width, heigth, TILE, id, true);
		
	}

	private static Panam instance;
	
    public static synchronized Panam getInstance(int x, int y, int xoffset, int yoffset, int width, int heigth, int STEP, int TILE, int selector) {
        if (instance == null) {
            instance = new Panam(x, y, xoffset, yoffset, width, heigth, STEP, TILE, selector);
        }
        return instance;
    }
    
    public static synchronized Panam getInstance() {
        if (instance == null) {
            return null;
        }
        return instance;
    }
	
	@Override
	public void update(boolean[] keys) {
		
		interaction = false;
		step = defaultStep;
		
		if (moved) {
			moveTimer++;
			
			switch(direction) {
			case 0: y -= step; break;
			case 1: x -= step; break;
			case 2: y += step; break;
			case 3: x += step; break;
			}
			
			if(moveTimer + 1 > interval) {
				switch(direction) {
				case 0: y -= tile - moveTimer * step; break;
				case 1: x -= tile - moveTimer * step; break;
				case 2: y += tile - moveTimer * step; break;
				case 3: x += tile - moveTimer * step; break;
				}
				
				moved = false;
				aligned = true;
				moveTimer = 0;
			}
		}
		else if (y != -1000) {
			
			if (keys[15]) {
				if (dash > 0) { step = defaultStep + 2; dash-= 1; moved = true;}
			}
			else if (dash == 0) { dash = -299; }
			else if (dash < -1) { dash++; }
			else if (dash == -1) dash = 50;

			if (keys[8])
				{ y -= step; moved = true; direction = 0;}
			else if (keys[9])
				{ x -= step; moved = true; direction = 1;}
			else if (keys[10])
				{ y += step; moved = true; direction = 2;}
			else if (keys[11])
				{ x += step; moved = true; direction = 3;}
			else if (keys[14])
				if (timer >= 60) { interaction = true; timer = 0; moved = true;}
			
			
		} else {
			
			if (!interactingObj.full) {
				hidden = false;
				setBack();
			} else if (keys[14]) {
				if (timer >= 60) { interaction = true; hiddenTimer = 1200; timer = 0; moved = true;}
			} else if (hiddenTimer != 0) {
				hiddenTimer--;
			} else {
				hiddenTimer = 240; interaction = true;
			}
			
		}
		
		
		timer++;


	}

	@Override
	public void draw(Graphics brush) {
		
		brush.drawImage(img, x, y, null);
		
	}
	
	public void handleHiding(PhysicalEntity ent) {

		if (ent == null || ent.selector != 1 || ent.kind == "chest") {
			if (!hidden) { hidden = true; memorizeValues(); interactingObj = ent; x = -1000; y = -1000; }
			else { hidden = false; setBack(); interactingObj.triggerIntr(this); }
		}
		
	}
	
	@Override
	public void triggerIntr(PhysicalEntity ent) {
		if (ent != null && ent.kind == "jason" ) { dead = true; img = sprites[1]; if (hidden) { setBack(); interactingObj.triggerIntr(this); } }
		else if (ent != null && ent.kind == "border") {
			if (!water) { x = tile * 4; y = tile * 15; water = true; }
			else { x = tile * 4; y = tile * 10; water = false; }
		}
		else handleHiding(ent);
	}

	@Override
	protected void loadImages() {
		
		try {
			sprites= new BufferedImage[] {
					ImageIO.read(getClass().getResourceAsStream("/sprites/panam/0.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/dead/0.png")),
			};
			imgResizer(sprites, width, heigth);
			
		} catch (IOException e) {
			e.printStackTrace();
		}
		
	}

}
