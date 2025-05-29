package entities;

import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.IOException;

import javax.imageio.ImageIO;

public class Jason extends AnimatedEntity{
	
	private int intrTimer = 120, moveTimer = 0;
	private int direction, interval;
	
	public Jason(int x, int y, int xoffset, int yoffset, int width, int heigth, int STEP, int TILE, int selector) {
		
		super(x, y, xoffset, yoffset, width, heigth, STEP + 1, TILE, selector, "jason");
		box = new CollisionBox(x, y, xoffset, yoffset, width, heigth, TILE, id, true);
		interval = TILE / (STEP + 1);
		
	}

	private static Jason instance;
	
    public static synchronized Jason getInstance(int x, int y, int xoffset, int yoffset, int width, int heigth, int STEP, int TILE, int selector) {
        if (instance == null) {
            instance = new Jason(x, y, xoffset, yoffset, width, heigth, STEP, TILE, selector);
        }
        return instance;
    }
    
    public static synchronized Jason getInstance() {
        if (instance == null) {
            return null;
        }
        return instance;
    }
	
	@Override
	public void update(boolean[] keys) {
		
		interaction = false;
		aligned = false;
		step = defaultStep;
		
		
		if (moved) {
			// System.out.println("1 Move timer: " + moveTimer + " ( " + x + ", " + y + " )");
			moveTimer++;
			
			switch(direction) {
			case 0: y -= step; break;
			case 1: x -= step; break;
			case 2: y += step; break;
			case 3: x += step; break;
			}
			
			if(moveTimer + 1 > interval) {
				// System.out.println("2 Move timer: " + moveTimer + " ( " + x + ", " + y + " )");
				switch(direction) {
				case 0: y -= tile - moveTimer * step; break;
				case 1: x -= tile - moveTimer * step; break;
				case 2: y += tile - moveTimer * step; break;
				case 3: x += tile - moveTimer * step; break;
				}
				// System.out.println("3 Move timer: " + moveTimer + " ( " + x + ", " + y + " )");
				
				moved = false;
				aligned = true;
				moveTimer = 0;
			}
		}
		else if (!interacting) {			
			if (keys[22])
				{ y -= step; moved = true; direction = 0;}
			else if (keys[0])
				{ x -= step; moved = true; direction = 1;}
			else if (keys[18])
				{ y += step; moved = true; direction = 2;}
			else if (keys[3])
				{ x += step; moved = true; direction = 3;}
			else if (keys[4])
				if (timer >= 15) { interacting = true; timer = 0; }
		} else {
			if (intrTimer == 0) { interaction = true; interacting = false; intrTimer = 30; }
			intrTimer--;
		}
		
		timer++;
	}

	@Override
	public void draw(Graphics brush) {
		
		brush.drawImage(img, x, y, null);
		
	}
	
	@Override
	public void triggerIntr(PhysicalEntity ent) {
		
		if (ent != null && ent.kind == "border") {
			if (!water) { x = tile * 4; y = tile * 15; water = true; }
			else { x = tile * 4; y = tile * 10; water = false; }
		}
		
	}

	@Override
	protected void loadImages() {
		
		try {
			sprites= new BufferedImage[] {
					ImageIO.read(getClass().getResourceAsStream("/sprites/jason/0.png")),
			};
			imgResizer(sprites, width, heigth);
			
		} catch (IOException e) {
			e.printStackTrace();
		}
		
	}
	
	@Override
	public void reset() {
		x = defaultx;
		y = defaulty;
		interacting = false;
		interaction = false;
		dead = false;
		water = false;
		moved = false;
		
		stage = 0;
		
		timer = 0;
		intrTimer = 120;
		moveTimer = 0;
	}

}
