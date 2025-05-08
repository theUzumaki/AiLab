package entities;

import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.IOException;

import javax.imageio.ImageIO;

public class Floor extends BackgroundEntity {

	public Floor(int x, int y, int width, int heigth, int TILE, int selector) {
		super(x, y, width, heigth, TILE, selector);
	}

	@Override
	public void draw(Graphics brush) {
		
		brush.drawImage(sprites[0], x, y, null);
		
	}

	@Override
	protected void loadImages() {
		
		try {
			sprites= new BufferedImage[] {
					ImageIO.read(getClass().getResourceAsStream("/sprites/floors/floor.png")),
			};
			imgResizer(sprites, width, heigth);
			
		} catch (IOException e) {
			e.printStackTrace();
		}
		
	}

}
