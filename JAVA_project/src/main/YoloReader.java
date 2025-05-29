package main;

import java.io.*;
import java.nio.channels.Channels;
import java.nio.channels.FileChannel;
import java.nio.channels.FileLock;

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONTokener;

public class YoloReader {
    public static class Detection {
        public String className;
        public float[] bbox; // [x1, y1, x2, y2]
        public float confidence;
    }

    public static Detection[] getDetections(String path) throws IOException {
    	
    	try (RandomAccessFile file = new RandomAccessFile(path, "r");
    		     FileChannel channel = file.getChannel();
    		     FileLock lock = channel.lock(0L, Long.MAX_VALUE, true);
    			InputStream is = Channels.newInputStream(channel);) {  // true = shared lock
	        JSONTokener tokener = new JSONTokener(is);
	        JSONArray array = new JSONArray(tokener);
	        
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
    	} catch (IOException e) {}
		return null;
    }
}
