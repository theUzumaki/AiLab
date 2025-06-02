package entities;

public class InteractionBox {

	public int id;
	public int width, heigth, tile;
	public int left, right, top, bottom;

	public String kind;
	public PhysicalEntity linkObj;
	
	public InteractionBox (int x, int y, int xoffset, int yoffset, int width, int heigth, int TILE, String kind) {
		
		left = x * TILE + xoffset - TILE / 2;
		right = ( x + width ) * TILE + xoffset + TILE / 2;
		top = y * TILE + yoffset - TILE / 2;
		bottom = ( y + heigth ) * TILE + yoffset + TILE / 2;
		this.width = width;
		this.heigth = heigth;
		this.tile = TILE;
		this.kind = kind;
		
		if (kind == "animated") {
			right -= 1;
			left += 1;
			bottom -= 1;
			top += 1;
		}
		
	}
	
	public InteractionBox (int x, int y, int xoffset, int yoffset, int width, int heigth, int TILE, String kind, PhysicalEntity linkObj) {
		
		left = x * TILE + xoffset - TILE / 2;
		right = ( x + width ) * TILE + xoffset + TILE / 2;
		top = y * TILE + yoffset - TILE / 2;
		bottom = ( y + heigth ) * TILE + yoffset + TILE / 2;
		this.width = width;
		this.heigth = heigth;
		this.tile = TILE;
		this.kind = kind;
		this.linkObj= linkObj;			
	
	}

	public void updatePosition(int x, int y) {
		
		if (linkObj.kind == "jason") {
			x -= tile / 2;
			y -= tile / 2;
		}
		
		left = x - tile / 2;
		right = x + width * tile + tile / 2;
		top = y - tile / 2;
		bottom = y + heigth * tile + tile / 2;
		
		if (kind == "animated") {
			right -= 1;
			left += 1;
			bottom -= 1;
			top += 1;
		}
		
	}
	
}
