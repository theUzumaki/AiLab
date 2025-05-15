package entities;

import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.IOException;

import javax.imageio.ImageIO;

public class Interior extends StaticEntity {

	public Interior(int x, int y, int xoffset, int yoffset, int width, int heigth, int TILE, int selector, int collision_x, int collision_y) {
		super(x, y, xoffset, yoffset, width, heigth, TILE, selector, "interior");
		box = new CollisionBox(x, y, xoffset, yoffset, collision_x, collision_y, TILE, id);
	}
	
	@Override
	public void update() {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void draw(Graphics brush) {
		
		brush.drawImage(img, x, y, null);
		
	}
	
	@Override
	protected void loadImages() {
		
		try {
			sprites= new BufferedImage[] {
					ImageIO.read(getClass().getResourceAsStream("/sprites/house_inside/scrivania.PNG")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/house_inside/scaffale.PNG")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/house_inside/Scaffale_Bello.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/house_inside/Tavolo.PNG")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/house_inside/sedia1.PNG")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/house_inside/sedia2.PNG")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/house_inside/panchina.PNG")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/house_inside/Panca_lunga.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/house_inside/Scrigno_Aperto_largo.png")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/house_inside/scrigno.PNG")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/house_inside/Sedia_Tavolo2.PNG")),
					ImageIO.read(getClass().getResourceAsStream("/sprites/house_inside/sediaTavolo.PNG")),
			};
			imgResizer(sprites, width, heigth);
			
		} catch (IOException e) {
			e.printStackTrace();
		}
		
	}

}
