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
    
    private void printCollisionBox(Graphics2D g) {
        for(CollisionBox box : gm.collisionBoxes) {

        	// Save the old composite so you can restore it later
        	Composite oldComposite = g.getComposite();

        	g.setComposite(AlphaComposite.getInstance(AlphaComposite.SRC_OVER, 0.2f));
        	g.setColor(new Color(255, 0, 0)); // Red

        	g.fillRect(box.left, box.top, box.right - box.left, box.bottom - box.top);
        	
        	g.setComposite(oldComposite);
        }
    }
}
