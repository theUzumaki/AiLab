package entities;

import java.util.List;

import javax.imageio.ImageIO;

import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.util.ArrayList;

public class GameMaster {

    private static GameMaster instance;
    private final int STEP = 2;
    private int rows, columns, sizetile;
    
    public List<AnimatedEntity> animatedEntities = new ArrayList<>();
    
    private BufferedImage[] sprites;

    private GameMaster(int TILE, int ROWS, int COLUMNS) {
    	
    	loadImages();
    	animatedEntities.add(Jason.getInstance(20, 20, 1, 1, STEP, TILE));
    	
    	this.rows= ROWS;
    	this.columns = COLUMNS;
    	this.sizetile = TILE;
    	
    }

    public static synchronized GameMaster getInstance(int TILE, int ROWS, int COLUMNS) {
        if (instance == null) {
            instance = new GameMaster(TILE, ROWS, COLUMNS);
        }
        return instance;
    }
    
    public void draw(Graphics brush) {
    	
    	
    	
    }
    
	private void loadImages() {
		
		try {
			sprites= new BufferedImage[] {
					ImageIO.read(getClass().getResourceAsStream("/sprites/jason/0.png")),
			};
			imgResizer(sprites, columns*sizetile, rows*sizetile);
			
		} catch (IOException e) {
			e.printStackTrace();
		}
		
	}
	
	private void imgResizer(BufferedImage[] sprites, int width, int height) {	// scales immediately the images to avoid doing it at runtime
		for (int i= 0; i< sprites.length; i++) {
			BufferedImage scaledImage= new BufferedImage(width, height, BufferedImage.TYPE_4BYTE_ABGR);
			Graphics g= scaledImage.createGraphics();
			g.drawImage(sprites[i], 0, 0, width, height, null);
			sprites[i]= scaledImage;
		}
	}
	
}
