package entities;

import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.IOException;

import javax.imageio.ImageIO;

public class Box extends HideoutEntity {

	public Box(int x, int y, int xoffset, int yoffset, int width, int heigth, int TILE, int selector) {
		super(x, y, xoffset, yoffset, width, heigth, TILE, selector, "box");
		box = new CollisionBox(x, y, xoffset, yoffset, 1, 1, TILE, id);
	}
	
	@Override
	public void update() {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void draw(Graphics brush) {
		
		brush.drawImage(img, x, y, null);
		
	}

	@Override
	protected void loadImages() {
		
		try {
			sprites= new BufferedImage[] {
					ImageIO.read(getClass().getResourceAsStream("/sprites/misc/cassa.PNG")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/misc/cassaRotta.PNG")),
			};
			imgResizer(sprites, width, heigth);
			
		} catch (IOException e) {
			e.printStackTrace();
		}
		
	}
	
	@Override
	public void triggerIntr(PhysicalEntity ent) {
		
		if (ent.kind == "jason") { img = sprites[1]; selector = 1; full = false; }
		else if (ent.kind == "panam") if (selector == 0) handleHiding("panam");
		
	}
	
	@Override
	public void reset() {
		full = false;
		img = sprites[0];
		selector = 0;
	}
	
}
