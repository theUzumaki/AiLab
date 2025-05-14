package entities;

public abstract class AnimatedEntity extends PhysicalEntity{
	
	protected int olddoorX, olddoorY;
	
	// Velocita attuale
	protected int step;
	
	public boolean interaction, dead;
	public InteractionBox intrBox;
	
	// Quanto va lento
	public int slow;
	
	// Velocita base
	public int defaultStep;
	
	public AnimatedEntity(int x, int y, int xoffset, int yoffset, int width, int heigth, int STEP, int TILE, int selector, String kind) {
		
		super(x, y, xoffset, yoffset, width, heigth, TILE, selector, kind);
		this.step = STEP;
		this.slow = STEP - 1;
		this.defaultStep = STEP;
		
		intrBox = new InteractionBox (x, y, xoffset, yoffset, width, heigth, TILE, "animated");
		intrBox.linkObj = this;
		
	}
	
	public abstract void update(boolean[] keys);

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
	
	public void memorizeValues() {
		oldx = x;
		oldy = y;
	}
	
	public void setBack() {
		
		x = oldx;
		y = oldy;
	}
	
}
