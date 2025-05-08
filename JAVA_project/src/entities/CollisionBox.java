package entities;

import java.awt.image.BufferedImage;

public class CollisionBox {

	public int id;
	public int x, y;
	public int width, heigth;
	public int tile;
	public int selector;
	protected BufferedImage[] sprites;
	
	public CollisionBox (int x, int y, int width, int heigth, int TILE, int id) {
		
		this.x = x;
		this.y = y;
		this.width = width * TILE;
		this.heigth = heigth * TILE;
		this.tile = TILE;
		this.id = id;
		
	}
	
	public boolean checkCollision () {
		
		
		return false;
	}
	
}
