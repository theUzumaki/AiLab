package main;

import java.awt.image.BufferedImage;
import java.util.concurrent.*;
import javax.imageio.ImageIO;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;

public class ImageSaver implements Runnable {
    private final BlockingQueue<BufferedImage> queue_jason = new LinkedBlockingQueue<>();
    private final BlockingQueue<BufferedImage> queue_victim = new LinkedBlockingQueue<>();
    private volatile boolean running = true;
    
    private void detection(String kind) {
    	try {
            // Comando per eseguire lo script
            ProcessBuilder pb = new ProcessBuilder("./Object_detection/.venv/bin/python3", "Object_detection/detection.py", kind);

            // Redirect dell'output della console
            pb.redirectErrorStream(true);
            Process process = pb.start();

            // Leggi l'output dello script
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;
            while ((line = reader.readLine()) != null) {
                System.out.println("[PYTHON] " + line);
            }

            int exitCode = process.waitFor();
            System.out.println("Script terminato con codice: " + exitCode);
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
    }
    
    
    public void saveImage(BufferedImage img, String who) {
        if ("jason".equals(who)) {
            queue_jason.offer(img);
        } else if ("panam".equals(who)) {
            queue_victim.offer(img);
        }
    }
    

    public void stop() {
        running = false;
    }

    @Override
    public void run() {
        while (running || !queue_jason.isEmpty() || !queue_victim.isEmpty()) {
            try {
                BufferedImage img_jason = queue_jason.poll(); // NON blocca
                if (img_jason != null) {
                    ImageIO.write(img_jason, "png", new File("jason_view.png"));
                    System.out.println("Saved jason screen");
                    detection("jason");
                }

                BufferedImage img_victim = queue_victim.poll(); // NON blocca
                if (img_victim != null) {
                    ImageIO.write(img_victim, "png", new File("victim_view.png"));
                    System.out.println("Saved panam screen");
                    detection("panam");
                }

                // Dorme un po’ per evitare loop troppo veloci
                Thread.sleep(10);

            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
}
