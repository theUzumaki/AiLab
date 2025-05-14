package entities;

import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.IOException;

import javax.imageio.ImageIO;

public class Panam extends AnimatedEntity{
	
	private int timer = 0;
	private boolean hidden;
	private PhysicalEntity interactingObj;
	
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
		
		if (y != -1000) {
			
			if (keys[8])
				y -= step;
			else if (keys[9])
				x -= step;
			else if (keys[10])
				y += step;
			else if (keys[11])
				x += step;
			else if (keys[14])
				if (timer >= 60) { interaction = true; timer = 0; }
			
		} else {
			
			if (hidden && !interactingObj.full) {
				hidden = false;
				setBack();
			} else if (keys[14]) {
				
				if (timer >= 60) { interaction = true; timer = 0; }
			}
			
		}
		
		
		timer++;


	}

	@Override
	public void draw(Graphics brush) {
		
		brush.drawImage(img, x, y, null);
		
	}
	
	public void handleHiding(PhysicalEntity ent) {

		if (ent == null || ent.selector != 1) {
			if (!hidden) { hidden = true; memorizeValues(); interactingObj = ent; x = -1000; y = -1000; }
			else { hidden = false; setBack(); interactingObj.triggerIntr(this); }
		}
		
	}
	
	@Override
	public void triggerIntr(PhysicalEntity ent) {
		if (ent != null && ent.kind == "jason" ) { dead = true; if (hidden) { setBack(); interactingObj.triggerIntr(this); } }
		else if (ent != null && ent.kind == "border") { x = 2*ent.x - x; y = 2*ent.y - y; }
		else handleHiding(ent);
	}

	@Override
	protected void loadImages() {
		
		try {
			sprites= new BufferedImage[] {
					ImageIO.read(getClass().getResourceAsStream("/sprites/panam/0.png")),
			};
			imgResizer(sprites, width, heigth);
			
		} catch (IOException e) {
			e.printStackTrace();
		}
		
	}

}
