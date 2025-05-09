package entities;

public abstract class AnimatedEntity extends PhysicalEntity{
	
	protected int step;
	
	public AnimatedEntity(int x, int y, int xoffset, int yoffset, int width, int heigth, int STEP, int TILE, int selector) {
		
		super(x, y, xoffset, yoffset, width, heigth, TILE, selector);
		this.step = STEP;
		
	}
	
	public abstract void update(String key);
	
}
