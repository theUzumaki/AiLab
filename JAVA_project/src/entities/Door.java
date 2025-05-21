package entities;

import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.IOException;

import javax.imageio.ImageIO;

public class Door extends BackgroundEntity {

	public Door(int x, int y, int xoffset, int yoffset, int width, int heigth, int TILE, int selector) {
		super(x, y, xoffset, yoffset, width, heigth, TILE, selector);
		// TODO Auto-generated constructor stub
	}

	@Override
	public void draw(Graphics brush) {
		// TODO Auto-generated method stub
		brush.drawImage(img, x, y, null);
	}

	@Override
	protected void loadImages() {
		try {
			sprites= new BufferedImage[] {
					ImageIO.read(getClass().getResourceAsStream("/sprites/misc/prova_2.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/misc/prova_1.png"))
					
			};
			imgResizer(sprites, width, heigth);
			
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

}
