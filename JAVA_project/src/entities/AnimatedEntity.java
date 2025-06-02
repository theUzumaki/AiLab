package entities;

import main.YoloReader;

public abstract class AnimatedEntity extends PhysicalEntity{
	
	protected int olddoorX, olddoorY;
	
	public int step;
	
	public boolean interaction, dead, water;
	public boolean interacting = false;
	public InteractionBox intrBox;
	
	public boolean aligned = false;
	
	public boolean moved = false;
	
	public int slow, defaultStep;
	public int stage = 0;
	protected int defaultx;

	protected int defaulty;
	
	public boolean hidden;
	
	public YoloReader.Detection[] detections;
	
	public int timer;
	
	public AnimatedEntity(int x, int y, int xoffset, int yoffset, int width, int heigth, int STEP, int TILE, int selector, String kind) {
		
		super(x, y, xoffset, yoffset, width, heigth, TILE, selector, kind);
		this.step = STEP;
		this.slow = STEP - 1;
		this.defaultStep = STEP;
		
		defaultx = x * TILE;
		defaulty = y * TILE;
	}
	
	public abstract void update(boolean[] keys);

	public void setLocation(int x, int y, int window) {
		
		stage = window;
		
		olddoorX = this.x;
		olddoorY = this.y;
		
		this.x = x;
		this.y = y;
		box.updatePosition(x, y);
		intrBox.updatePosition(x, y);

	}
	
	public void exitHouse() {
		
		stage = 0;
		
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
