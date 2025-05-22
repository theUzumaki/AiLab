package entities;

import java.awt.Graphics;

public abstract class HideoutEntity extends StaticEntity{

	public HideoutEntity(int x, int y, int xoffset, int yoffset, int width, int heigth, int TILE, int selector,
			String kind) {
		super(x, y, xoffset, yoffset, width, heigth, TILE, selector, kind);
		// TODO Auto-generated constructor stub
	}

	@Override
	public void update() {
		// TODO Auto-generated method stub
		
	}

	@Override
	protected void loadImages() {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void draw(Graphics brush) {
		// TODO Auto-generated method stub
		
	}
	
	public boolean handleHiding(String client) {
		
		switch (client) {
		
		case "panam":
			if (!full) { full = true; return false; }
			else { full = false; return true; }
		
		}
		return false;
	}
	
	@Override
	public void reset() {
		full = false;
	}

}
