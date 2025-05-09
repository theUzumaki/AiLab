package entities;

public class CollisionBox {

	public int id;
	public int width, heigth, tile;
	public int left, right, top, bottom;
	public int animatedCoeff = 0;
	
	public CollisionBox (int x, int y, int width, int heigth, int TILE, int id) {
		
		
		left = x * TILE;
		right = ( x + width ) * TILE;
		top = y * TILE;
		bottom = ( y + heigth ) * TILE;
		this.width = width;
		this.heigth = heigth;
		this.tile = TILE;
		this.id = id;
		
	}
	
	public CollisionBox (int x, int y, int width, int heigth, int TILE, int id, boolean animated) {
		
		left = x * TILE + 1;
		right = ( x + width ) * TILE - 1;
		top = y * TILE + 1;
		bottom = ( y + heigth ) * TILE - 1;
		this.width = width;
		this.heigth = heigth;
		this.tile = TILE;
		this.id = id;
		
		animatedCoeff = 1;
		
	}

	public void updatePosition(int x, int y) {
		
		left = x + 1 * animatedCoeff;
		right = x + width * tile - 1 * animatedCoeff;
		top = y + 1 * animatedCoeff;
		bottom = y + heigth * tile - 1 * animatedCoeff;
		
	}
	
}