package main;

import java.util.List;
import java.awt.Rectangle;

import javax.swing.JFrame;

import entities.GameMaster;

public class Main {
    public static void main(String[] args) {
        
        int[][] windowValues = new int[][] {
        	{ 20, 20, 40 },
        	{ 20, 8, 16 },
        	{ 20, 8, 16 }
        };
        
        boolean show = Boolean.valueOf(args[0]);
        int map = Integer.valueOf(args[1]);
        String phase = args[2];
        
        int[] dims1 = new int[] { windowValues[0][2] * windowValues[0][0], windowValues[0][1] * windowValues[0][0] };
        int[] dims2 = new int[] { windowValues[1][2] * windowValues[1][0], windowValues[1][1] * windowValues[1][0] };
        int[] dims3 = new int[] { windowValues[2][2] * windowValues[2][0], windowValues[2][1] * windowValues[2][0] };

        Rectangle forestCam = new Rectangle(0, 0, dims1[0], dims1[1] );
        Rectangle house1Cam = new Rectangle(dims1[0], dims1[1], dims2[0], dims2[1] );
        Rectangle house2Cam = new Rectangle(dims1[0] + dims2[0], dims1[1] + dims2[1], dims3[0], dims3[1] );
        
        GameMaster.getInstance(windowValues, map);

        Game forest = new Game(forestCam, 0, windowValues[0][0], phase);
        Game house1 = new Game(house1Cam, 1, windowValues[1][0], phase);
        Game house2 = new Game(house2Cam, 2, windowValues[2][0], phase);

        createWindow("Forest", forest, 0, 0, show);
        createWindow("House 1", house1, dims1[0], dims1[1], show);
        createWindow("House 2", house2, dims1[0] + dims2[0], dims1[1] + dims2[1], show);

        List<Game> allViews = List.of(forest, house1, house2);
        
        Thread gameLoop = new Thread(new GameLoop(allViews, map, phase, show));
        
        System.out.println("[JAVA] Game loop starting");
        gameLoop.start();
    }

    private static void createWindow(String title, Game view, int x, int y, boolean show) {
        JFrame frame = new JFrame(title);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.add(view);
        frame.pack();
        frame.setLocation(x, y);
        frame.setVisible(show);
    }
}
