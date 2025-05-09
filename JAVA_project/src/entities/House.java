package entities;

import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.IOException;

import javax.imageio.ImageIO;

public class House extends StaticEntity{

	public House(int x, int y, int width, int heigth, int TILE, int selector) {
		super(x, y, width, heigth, TILE, selector);
		
		box = new CollisionBox(x, y + 2, width, heigth - 2, TILE, id);
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
					ImageIO.read(getClass().getResourceAsStream("/sprites/houses/casa2.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/houses/casa3.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/houses/casa5.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/houses/casa6.png")),
			};
			imgResizer(sprites, width, heigth);
			
		} catch (IOException e) {
			e.printStackTrace();
		}
		
	}

}
