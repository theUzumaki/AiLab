package entities;

import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.IOException;

import javax.imageio.ImageIO;

public class WinnerObject extends HideoutEntity {
	
	public boolean find = false;
	
	public WinnerObject(int x, int y, int xoffset, int yoffset, int width, int heigth, int TILE, int selector) {
		super(x, y, xoffset, yoffset, width, heigth, TILE, selector, "win");
		box = new CollisionBox(x, y, xoffset, yoffset, 1, 1, TILE, id);
	}

	@Override
	protected void loadImages() {
		try {
			sprites= new BufferedImage[] {
					ImageIO.read(getClass().getResourceAsStream("/sprites/misc/battery.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/misc/phone.png"))
					
			};
			imgResizer(sprites, width, heigth);
			
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	@Override
	public void draw(Graphics brush) {
		
		brush.drawImage(img, x, y, null);
	}
	
	@Override
	public void triggerIntr(PhysicalEntity ent) {
		System.out.println("trigger");
		
		if (ent.kind == "panam" && find == false) { 
			find = true;
			
			System.out.println("Dentro if");

	        if (!((Panam) ent).listOfObject.contains(this)) {
	        	System.out.println("Added");
	        	((Panam) ent).listOfObject.add(this);
	        }
	    }
		
	}
	
	@Override
	public void reset() {
		find = false;
	}

}
