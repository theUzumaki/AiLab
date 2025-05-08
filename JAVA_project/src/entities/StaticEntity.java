package entities;

public abstract class StaticEntity extends PhysicalEntity{

	public StaticEntity(int x, int y, int width, int heigth, int TILE) {
		
		super(x, y, width, heigth, TILE);
		
	}
	
	public abstract void update();
	
}
