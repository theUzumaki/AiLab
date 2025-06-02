package main;

import javax.swing.JPanel;

import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.util.Collections;
import java.util.Comparator;

import entities.*;

@SuppressWarnings("serial")
public class Game extends JPanel {

    private final GameMaster gm;
    private final KeyManager keys;
    final Rectangle camera;
    
    private final int id;
    private final int sizeTile;
    
    public boolean screen = false;

    public Game(Rectangle camera, int id, int sizeTile) {
        this.camera = camera;
        this.gm = GameMaster.getInstance();  // Shared game logic
        this.keys = new KeyManager();
        this.id = id;
        this.sizeTile = sizeTile;
        

        setPreferredSize(new Dimension(camera.width, camera.height));
        setBackground(Color.BLACK);
        setFocusable(true);
        addKeyListener(keys);
    }

    public KeyManager getKeyManager() {
        return keys;
    }
    
    public BufferedImage captureFrameCentered(int playerX, int playerY) {
    	
        int frameWidth = sizeTile * 5;
        int frameHeight = sizeTile * 5;

        // 1. Calcola il centro del giocatore
        int centerX = playerX + sizeTile / 2;
        int centerY = playerY + sizeTile / 2;
        
        // 3. Centra il frame sul blocco
        int frameX = centerX - frameWidth / 2;
        int frameY = centerY - frameHeight / 2;
        
        BufferedImage img = new BufferedImage(frameWidth, frameHeight, BufferedImage.TYPE_INT_RGB);
        Graphics g = img.getGraphics();

        g.translate(-(frameX - camera.x), -(frameY - camera.y));

        screen = true;
        this.paint(g);

        g.dispose();
        screen = false;
        
        return img;
    }
    
    protected void drawBox(float[] bbox, int player_x, int player_y, Graphics g, YoloReader.Detection d) {
    	int imageWidth = sizeTile * 5;
    	int imageHeight = sizeTile * 5;

    	float x1_local = bbox[0];
    	float y1_local = bbox[1];
    	float x2_local = bbox[2];
    	float y2_local = bbox[3];

    	// 1. Calcola il centro del giocatore
        int centerX = player_x + sizeTile / 2;
        int centerY = player_y + sizeTile / 2;

    	int imageStartX = centerX - imageWidth / 2;
    	int imageStartY = centerY - imageHeight / 2;
    	
    	int x1_global = imageStartX + Math.round(x1_local);
    	int y1_global = imageStartY + Math.round(y1_local);
    	int x2_global = imageStartX + Math.round(x2_local);
    	int y2_global = imageStartY + Math.round(y2_local);
    	
    	
    	g.setColor(Color.GREEN);
    	
    	g.drawRect(x1_global, y1_global, x2_global - x1_global, y2_global - y1_global);
        g.drawString(d.className, (int) x1_global, (int) y1_global - 5);
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);

        Graphics2D g2d = (Graphics2D) g;

        // Shift rendering to simulate camera
        g2d.translate(-camera.x, -camera.y);

        Collections.sort(gm.physicalEntities, Comparator.comparingInt(c -> c.y + c.heigth));

        for (BackgroundEntity ent : gm.bgEntities1) ent.draw(g);
        for (BackgroundEntity ent : gm.bgEntities2) ent.draw(g);
        for (PhysicalEntity ent : gm.physicalEntities) {
        	ent.draw(g);
        	if((ent.kind == "jason" || ent.kind == "panam") && screen == false) {
        		YoloReader.Detection[] detections;
        		try {
        			detections = YoloReader.getDetections("Object_detection/detections_"+ent.kind+".json");
        			if (detections != null) {
        				((AnimatedEntity) ent).detections = detections;
        			}
        			for(YoloReader.Detection d : ((AnimatedEntity) ent).detections) {
        				this.drawBox(d.bbox, ent.x, ent.y, g, d);
        	        }
        		} catch (IOException | NullPointerException e) {
        			continue;
        		}
        	}
        }
        
        // printCollisionBox(g2d);
    }

    public Rectangle getCamera() {
        return camera;
    }
    
    protected void printCollisionBox(Graphics2D g) {

    	Composite oldComposite = g.getComposite();
    	
        for(CollisionBox box : gm.collisionBoxes) {

        	g.setComposite(AlphaComposite.getInstance(AlphaComposite.SRC_OVER, 0.2f));
        	g.setColor(new Color(255, 0, 0)); // Red

        	g.fillRect(box.left, box.top, box.right - box.left, box.bottom - box.top);
        	
        }
        
        for(InteractionBox intrBox : gm.interactionBoxes ) {

        	g.setComposite(AlphaComposite.getInstance(AlphaComposite.SRC_OVER, 0.2f));
        	g.setColor(new Color(0, 255, 0)); // Red

        	g.fillRect(intrBox.left, intrBox.top, intrBox.right - intrBox.left, intrBox.bottom - intrBox.top);
        	
        }
        
        g.setComposite(oldComposite);
    }
}
