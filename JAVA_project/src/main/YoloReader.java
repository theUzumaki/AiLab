package main;

import java.io.*;
import java.nio.channels.Channels;
import java.nio.channels.FileChannel;
import java.nio.channels.FileLock;
import java.nio.file.Files;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;

public class YoloReader {
    public static class Detection {
        public String className;
        public float[] bbox; // [x1, y1, x2, y2]
        public float confidence;
    }

    public static Detection[] getDetections(String path) throws IOException {
    	
    	try (RandomAccessFile file = new RandomAccessFile(path, "rw");
                FileChannel channel = file.getChannel();
                FileLock lock = channel.lock(0L, Long.MAX_VALUE, false)) {
    		
    		if (file.length() == 0) {
    			return null;
    		}
    		
    		File f = new File(path);
        	String json = new String(Files.readAllBytes(f.toPath()));
        	file.setLength(0);

        	JSONArray array = new JSONArray(json);
            
            Detection[] detections = new Detection[array.length()];
            for (int i = 0; i < array.length(); i++) {
                JSONObject obj = array.getJSONObject(i);
                Detection d = new Detection();
                d.className = obj.getString("class");
                JSONArray bboxArray = obj.getJSONArray("bbox");
                d.bbox = new float[] {
                    (float) bboxArray.getDouble(0),
                    (float) bboxArray.getDouble(1),
                    (float) bboxArray.getDouble(2),
                    (float) bboxArray.getDouble(3)
                };
                d.confidence = (float) obj.getDouble("confidence");
                detections[i] = d;
            }
            
        	return detections;
    	} catch(JSONException e) {
    		return null;
    	}
    	
    }
}
