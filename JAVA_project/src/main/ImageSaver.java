package main;

import java.awt.image.BufferedImage;
import java.util.concurrent.*;
import javax.imageio.ImageIO;

import java.io.File;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.channels.FileChannel;
import java.nio.channels.FileLock;

public class ImageSaver implements Runnable {
    private final BlockingQueue<BufferedImage> queue_jason = new LinkedBlockingQueue<>();
    private final BlockingQueue<BufferedImage> queue_victim = new LinkedBlockingQueue<>();
    private volatile boolean running = true;
    
    public BufferedImage img_last;
    
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
                if (!queue_jason.isEmpty()) {
                	Object[] array = queue_jason.toArray();
                	img_last = (BufferedImage) array[array.length - 1];
                	
                	try (RandomAccessFile file = new RandomAccessFile("Object_detection/jason_view.png", "rw");
                		     FileChannel channel = file.getChannel();
                			FileLock lock = channel.lock(0L, Long.MAX_VALUE, false)) {
                		ImageIO.write(img_last, "png", new File("Object_detection/jason_view.png"));
                	} catch (IOException e) {
                	}
                    
                    queue_jason.clear();
                }
                
                if (!queue_victim.isEmpty()) {
                	Object[] array = queue_victim.toArray();
                	img_last = (BufferedImage) array[array.length - 1];
                	
                	try (RandomAccessFile file = new RandomAccessFile("Object_detection/victim_view.png", "rw");
               		     FileChannel channel = file.getChannel();
                		FileLock lock = channel.lock(0L, Long.MAX_VALUE, false)) {
	               		ImageIO.write(img_last, "png", new File("Object_detection/victim_view.png"));
	               	} catch (IOException e) {
	               	}
                    
                	queue_victim.clear();
                }

            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
}