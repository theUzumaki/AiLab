package entities;

import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.IOException;

import javax.imageio.ImageIO;

public class Floor extends BackgroundEntity {

	public Floor(int x, int y, int xoffset, int yoffset, int width, int heigth, int TILE, int selector) {
		
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
					
					ImageIO.read(getClass().getResourceAsStream("/sprites/floors/floor1.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/floors/floor_up.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/floors/floor_left.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/floors/floor_down.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/floors/floor_right.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/floors/top_left.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/floors/top_right.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/floors/bottom_right.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/floors/bottom_left.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/floors/pavimento3.PNG")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/floors/AnagoloBDx.PNG")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/floors/AnagoloBSx.PNG")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/floors/AnagoloTDx.PNG")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/floors/AnagoloTSx.PNG")),
					
			};
			imgResizer(sprites, width, heigth);
			
		} catch (IOException e) {
			e.printStackTrace();
		}
		
	}

}
