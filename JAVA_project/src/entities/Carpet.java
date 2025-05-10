package entities;

import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.IOException;

import javax.imageio.ImageIO;

public class Carpet extends BackgroundEntity {

	public Carpet(int x, int y, int xoffset, int yoffset, int width, int heigth, int TILE, int selector) {
		super(x, y, xoffset, yoffset, width, heigth, TILE, selector);

	}

	@Override
	public void draw(Graphics brush) {
		
		brush.drawImage(img, x, y, null);
		
	}
	
	@Override
	protected void loadImages() {
		
		try {
			sprites= new BufferedImage[] {
					ImageIO.read(getClass().getResourceAsStream("/sprites/house_inside/tappeto2.PNG")),
			};
			imgResizer(sprites, width, heigth);
			
		} catch (IOException e) {
			e.printStackTrace();
		}
		
	}

}

