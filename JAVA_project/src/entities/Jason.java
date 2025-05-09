package entities;

import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.IOException;

import javax.imageio.ImageIO;

public class Jason extends AnimatedEntity{
	
	public Jason(int x, int y, int width, int heigth, int STEP, int TILE) {
		
		super(x, y, width, heigth, STEP, TILE);
		box = new CollisionBox(x, y, width, heigth, TILE, id);
		
	}

	private static Jason instance;
	
    public static synchronized Jason getInstance(int x, int y, int width, int heigth, int STEP, int TILE) {
        if (instance == null) {
            instance = new Jason(x, y, width, heigth, STEP, TILE);
        }
        return instance;
    }
    
    public static synchronized Jason getInstance() {
        if (instance == null) {
            return null;
        }
        return instance;
    }
	
	@Override
	public void update(String key) {
		
		switch ( key ) {
		
		case "w":
			y -= step;
			break;
		
		case "a":
			x -= step;
			break;
			
		case "s":
			y += step;
			break;
			
		case "d":
			x += step;
			break;
			
		}

	}

	@Override
	public void draw(Graphics brush) {
		
		brush.drawImage(sprites[0], x, y, null);
		
	}

	@Override
	protected void loadImages() {
		
		try {
			sprites= new BufferedImage[] {
					ImageIO.read(getClass().getResourceAsStream("/sprites/jason/0.png")),
			};
			imgResizer(sprites, width, heigth);
			
		} catch (IOException e) {
			e.printStackTrace();
		}
		
	}

}
