package entities;

import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.IOException;

import javax.imageio.ImageIO;

public class Stuff extends StaticEntity {

	public Stuff(int x, int y, int xoffset, int yoffset, int width, int heigth, int TILE, int selector) {
		super(x, y, xoffset, yoffset, width, heigth, TILE, selector, "stuff");
		box = new CollisionBox(x, y, xoffset, yoffset, 2, 2, TILE, id);
	}
	
	// Usato per l'erba alta per imostare la collision box  1 x 1
	public Stuff(int x, int y, int xoffset, int yoffset, int width, int heigth, int TILE, int selector, int collisionSize) {
		super(x, y, xoffset, yoffset, width, heigth, TILE, selector, "small stuff");
		
		// Controlla se lo stuff 1 x 1 usato e l'erba alta o no
		if (selector == 1) {
			// L'uno finale serve come booleano per controllare nelle checkCollision se la box e di rallentamento o no
			box = new CollisionBox(x, y, xoffset, yoffset, 1, 1, TILE, id, 1);
		} else {
			box = new CollisionBox(x, y, xoffset, yoffset, 1, 1, TILE, id);
		}
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
					ImageIO.read(getClass().getResourceAsStream("/sprites/misc/Stuff.PNG")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/misc/grass.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/misc/mattoni.PNG"))
			};
			imgResizer(sprites, width, heigth);
			
		} catch (IOException e) {
			e.printStackTrace();
		}
		
	}

}
