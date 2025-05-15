package entities;

import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.IOException;

import javax.imageio.ImageIO;

public class Jason extends AnimatedEntity{
	
	private int timer = 0;
	
	public Jason(int x, int y, int xoffset, int yoffset, int width, int heigth, int STEP, int TILE, int selector) {
		
		super(x, y, xoffset, yoffset, width, heigth, STEP, TILE, selector, "jason");
		box = new CollisionBox(x, y, xoffset, yoffset, width, heigth, TILE, id, true);
		
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
		step = defaultStep;
		
		if (keys[22])
			y -= step;
		else if (keys[0])
			x -= step;
		else if (keys[18])
			y += step;
		else if (keys[3])
			x += step;
		else if (keys[4])
			if (timer >= 60) { interaction = true; timer = 0; }
		
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

}
