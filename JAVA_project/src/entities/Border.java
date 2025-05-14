package entities;

import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.IOException;

import javax.imageio.ImageIO;

public class Border extends StaticEntity {
	
	public Border(int x, int y, int xoffset, int yoffset, int width, int heigth, int TILE, int selector) {
		super(x, y, xoffset, yoffset, width, heigth, TILE, selector, "border");
		
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
					ImageIO.read(getClass().getResourceAsStream("/sprites/pond/pondB.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/pond/pondBDX.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/pond/pondBSX.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/pond/pondDX.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/pond/pondSX.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/pond/pondT.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/pond/pondTDX.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/pond/pondTSX.png"))
			};
			imgResizer(sprites, width, heigth);
			
		} catch (IOException e) {
			e.printStackTrace();
		}
		
	}

}
