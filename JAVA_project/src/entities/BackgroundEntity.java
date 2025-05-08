package entities;

import java.awt.Graphics;

public abstract class BackgroundEntity extends ConceptEntity{

	public BackgroundEntity(int x, int y, int width, int heigth, int TILE) {
		super(x, y, width, heigth, TILE);
	}
	
	public abstract void draw(Graphics brush);

}
