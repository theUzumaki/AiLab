package entities;

public abstract class StaticEntity extends PhysicalEntity{

	public StaticEntity(int x, int y, int xoffset, int yoffset, int width, int heigth, int TILE, int selector, String kind) {
		
		super(x, y, xoffset, yoffset, width, heigth, TILE, selector, kind);
		
	}
	
	public abstract void update();
	
}
