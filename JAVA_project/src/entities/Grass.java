package entities;

import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.IOException;

import javax.imageio.ImageIO;

public class Grass extends BackgroundEntity{

	public Grass(int x, int y, int xoffset, int yoffset, int width, int heigth, int TILE, int selector) {
		
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
					ImageIO.read(getClass().getResourceAsStream("/sprites/floors/grass1.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/trees/pine/front.png")),
			};
			imgResizer(sprites, width, heigth);
			
		} catch (IOException e) {
			e.printStackTrace();
		}
		
	}

}
