package entities;

import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.IOException;

import javax.imageio.ImageIO;

public class Warehouse extends HideoutEntity{

	public Warehouse(int x, int y, int xoffset, int yoffset, int width, int heigth, int TILE, int selector) {
		super(x, y, xoffset, yoffset, width, heigth, TILE, selector, "warehouse");
		
		box = new CollisionBox(x, y + 2, xoffset, yoffset, width, heigth - 2, TILE, id);
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
					ImageIO.read(getClass().getResourceAsStream("/sprites/houses/casa6.png")),
			};
			imgResizer(sprites, width, heigth);
			
		} catch (IOException e) {
			e.printStackTrace();
		}
		
	}
	
	@Override
	public void triggerIntr(PhysicalEntity ent) {
		
		if (ent.kind == "jason") full = false;
		else if (ent.kind == "panam") if (selector == 0) handleHiding("panam");
		
	}

}
