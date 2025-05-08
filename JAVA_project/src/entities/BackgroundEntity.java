package entities;

public abstract class BackgroundEntity extends ConceptEntity{
	
	int selector;

	public BackgroundEntity(int x, int y, int width, int heigth, int TILE, int selector) {
		
		super(x, y, width, heigth, TILE);
		this.selector = selector;
		loadImages();
		
	}

}
