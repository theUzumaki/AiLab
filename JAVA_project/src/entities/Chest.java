package entities;

import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.IOException;

import javax.imageio.ImageIO;

public class Chest extends HideoutEntity {

	public Chest(int x, int y, int xoffset, int yoffset, int width, int heigth, int TILE, int selector, int collision_x, int collision_y) {
		super(x, y, xoffset, yoffset, width, heigth, TILE, selector, "chest");
		box = new CollisionBox(x, y, xoffset, yoffset, collision_x, collision_y, TILE, id);
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
					ImageIO.read(getClass().getResourceAsStream("/sprites/house_inside/Scrigno_Aperto_largo.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/house_inside/scrigno.PNG")),
			};
			imgResizer(sprites, width, heigth);
			
		} catch (IOException e) {
			e.printStackTrace();
		}
		
	}
	
	@Override
	public void triggerIntr(PhysicalEntity ent) {
		
		if (ent.kind == "jason") full = false;
		else if (ent.kind == "panam") handleHiding("panam");
	}

}
