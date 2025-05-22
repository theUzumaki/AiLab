package main;

import org.json.JSONObject;
import java.io.FileWriter;
import java.io.IOException;

public class ResultWriter {

    public static void writeWinner(boolean killerWon, boolean victimWon) {
        JSONObject result = new JSONObject();
        result.put("killer", killerWon);
        result.put("victim", victimWon);

        try (FileWriter file = new FileWriter("winner.json")) {
            file.write(result.toString(4)); // '4' per formattazione leggibile
            file.flush();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
