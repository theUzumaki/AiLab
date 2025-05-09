package entities;

public class CollisionBox {

	public int id;
	public int width, heigth;
	public int left, right, top, bottom;
	
	public CollisionBox (int x, int y, int width, int heigth, int TILE, int id) {
		
		
		left = x * TILE;
		right = ( x + width ) * TILE;
		top = y * TILE;
		bottom = ( y + heigth ) * TILE;
		this.width = width;
		this.heigth = heigth;
		this.id = id;
		
	}

	public void updatePosition(int x, int y) {
		
		left = x;
		right = x + width;
		top = y;
		bottom = y + heigth;
		
	}
	
}