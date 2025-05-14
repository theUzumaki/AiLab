package main;

import javax.swing.JPanel;
import java.awt.*;
import java.util.Collections;
import java.util.Comparator;

import entities.*;

@SuppressWarnings("serial")
public class Game extends JPanel {

    private final GameMaster gm;
    private final KeyManager keys;
    private final Rectangle camera;

    public Game(Rectangle camera) {
        this.camera = camera;
        this.gm = GameMaster.getInstance();  // Shared game logic
        this.keys = new KeyManager();

        setPreferredSize(new Dimension(camera.width, camera.height));
        setBackground(Color.BLACK);
        setFocusable(true);
        addKeyListener(keys);
    }

    public KeyManager getKeyManager() {
        return keys;
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
        for (PhysicalEntity ent : gm.physicalEntities) ent.draw(g);
        
        printCollisionBox(g2d);
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
