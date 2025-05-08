package entities;

import java.awt.Graphics;

public abstract class AnimatedEntity extends ConceptEntity{
	
	protected int step;
	
	public AnimatedEntity(int x, int y, int width, int heigth, int STEP, int TILE) {
		
		super(x, y, width, heigth, TILE);
		this.step = STEP;
		loadImages();
	}
	
	public abstract void update(String key);
	
	public abstract void draw(Graphics g);
	
}
