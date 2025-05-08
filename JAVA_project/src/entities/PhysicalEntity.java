package entities;

public abstract class PhysicalEntity extends ConceptEntity{
	
	static private int serialId;
	public int id;
	public CollisionBox box;

	public PhysicalEntity(int x, int y, int width, int heigth, int TILE) {
		
		super(x, y, width, heigth, TILE);
		loadImages();
		
		serialId++;
		id = serialId - 1;
		
		box = new CollisionBox(x, y, width, heigth, TILE, id);
	}

	@Override
	protected void loadImages() {
	}

}
