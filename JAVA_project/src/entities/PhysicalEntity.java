package entities;

public abstract class PhysicalEntity extends ConceptEntity{
	
	static private int serialId;
	public int id;
	private int oldx, oldy;

	public PhysicalEntity(int x, int y, int width, int heigth, int TILE) {
		
		super(x, y, width, heigth, TILE);
		loadImages();
		
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
