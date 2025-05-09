package entities;

import java.awt.Graphics;
import java.awt.image.BufferedImage;

public abstract class ConceptEntity {

	public int x, y;
	public int width, heigth;
	public int tile;
	public int selector;
	protected BufferedImage[] sprites;
	
	public ConceptEntity (int x, int y, int width, int heigth, int TILE) {
		
		this.x = x * TILE;
		this.y = y * TILE;
		this.width = width * TILE;
		this.heigth = heigth * TILE;
		this.tile = TILE;
		
	}
	
	public abstract void draw(Graphics brush);
	
	protected abstract void loadImages();
	
	protected void imgResizer(BufferedImage[] sprites, int width, int height) {	// scales immediately the images to avoid doing it at runtime
		for (int i= 0; i< sprites.length; i++) {
			BufferedImage scaledImage= new BufferedImage(width, height, BufferedImage.TYPE_4BYTE_ABGR);
			Graphics g= scaledImage.createGraphics();
			g.drawImage(sprites[i], 0, 0, width, height, null);
			sprites[i]= scaledImage;
		}
	}

}
