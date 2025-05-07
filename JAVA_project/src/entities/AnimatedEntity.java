package entities;

import java.awt.Graphics;

public abstract class AnimatedEntity extends ConceptEntity{
	
	public AnimatedEntity(int x, int y, int width, int heigth, int STEP, int TILE) {
		super(x, y, width, heigth, STEP, TILE);
	}
	
	public abstract void update(String key);
	
	public abstract void draw(Graphics g);
	
}
