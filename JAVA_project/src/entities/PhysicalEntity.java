package entities;

public abstract class PhysicalEntity extends ConceptEntity{
	
	static private int serialId;
	private int oldx, oldy;
	public int id;
	public CollisionBox box;

	public PhysicalEntity(int x, int y, int width, int heigth, int TILE, int selector) {
		
		super(x, y, width, heigth, TILE, selector);
		
		serialId++;
		id = serialId - 1;
		
	}

	@Override
	protected abstract void loadImages();
	
	public void memorizeValues() {
		oldx = x;
		oldy = y;
	}
	
	public void setBack() {
		x = oldx;
		y = oldy;
	}

}
