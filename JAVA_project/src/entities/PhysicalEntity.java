package entities;

public abstract class PhysicalEntity extends ConceptEntity{
	
	static private int serialId;
	protected int oldx, oldy;
	
	protected boolean full = false;
	
	public int id;
	public CollisionBox box;
	public String kind;

	public PhysicalEntity(int x, int y, int xoffset, int yoffset, int width, int heigth, int TILE, int selector, String kind) {
		
		super(x, y, xoffset, yoffset, width, heigth, TILE, selector);
		
		this.kind = kind;
		serialId++;
		id = serialId - 1;
		
	}

	@Override
	protected abstract void loadImages();
	
	public void triggerIntr(PhysicalEntity ent) {
		
	};
	
	public void reset() {}

}
