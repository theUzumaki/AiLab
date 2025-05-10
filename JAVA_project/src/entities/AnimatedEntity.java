package entities;

public abstract class AnimatedEntity extends PhysicalEntity{
	
	protected int olddoorX, olddoorY;
	protected int step;
	public boolean interaction;
	public InteractionBox intrBox;
	
	public AnimatedEntity(int x, int y, int xoffset, int yoffset, int width, int heigth, int STEP, int TILE, int selector, String kind) {
		
		super(x, y, xoffset, yoffset, width, heigth, TILE, selector, kind);
		this.step = STEP;
		
		intrBox = new InteractionBox (x, y, xoffset, yoffset, width, heigth, TILE, "animated");
		
	}
	
	public abstract void update(String key);
	
	public void setLocation(int x, int y) {
		
		olddoorX = this.x;
		olddoorY = this.y;
		
		this.x = x;
		this.y = y;
		box.updatePosition(x, y);
		intrBox.updatePosition(x, y);
	}
	
	public void exitHouse() {
		
		this.x = olddoorX;
		this.y = olddoorY;
		
	}
	
}
