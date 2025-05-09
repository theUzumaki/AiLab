package entities;

public abstract class BackgroundEntity extends ConceptEntity{
	
	int selector;

	public BackgroundEntity(int x, int y, int xoffset, int yoffset, int width, int heigth, int TILE, int selector) {
		
		super(x, y, xoffset, yoffset, width, heigth, TILE, selector);
		this.selector = selector;
		loadImages();
		img = sprites[selector];
		
	}

}
