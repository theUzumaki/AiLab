package Main;

import javax.swing.JFrame;

public class Main {
    public static void main(String[] args) {
        // Create a window (JFrame)
        JFrame window = new JFrame("Basic Java Game");
        window.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        window.setResizable(false);

        // Create the game panel and add to window
        Game game = new Game();
        window.add(game);
        window.pack();
        window.setLocationRelativeTo(null); // center on screen
        window.setVisible(true);

        // Start the game loop on a new thread
        game.start();
    }
}
