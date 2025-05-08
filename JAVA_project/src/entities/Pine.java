package entities;

import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.IOException;

import javax.imageio.ImageIO;

public class Pine extends StaticEntity{

	public Pine(int x, int y, int width, int heigth, int TILE) {
		super(x, y, width, heigth, TILE);
		// TODO Auto-generated constructor stub
	}
	
	@Override
	public void update() {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void draw(Graphics brush) {
		
		brush.drawImage(sprites[0], x, y, null);
		
	}
	
	@Override
	protected void loadImages() {
		
		try {
			sprites= new BufferedImage[] {
					ImageIO.read(getClass().getResourceAsStream("/sprites/trees/pine/front.png")),
			};
			imgResizer(sprites, width, heigth);
			
		} catch (IOException e) {
			e.printStackTrace();
		}
		
	}

}
