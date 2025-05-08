package entities;

import java.awt.Graphics;

public abstract class StaticEntity extends ConceptEntity{

	public StaticEntity(int x, int y, int width, int heigth, int TILE) {
		
		super(x, y, width, heigth, TILE);
		loadImages();
		
	}
	
	public abstract void update();
	
	public abstract void draw(Graphics g);
	
}
