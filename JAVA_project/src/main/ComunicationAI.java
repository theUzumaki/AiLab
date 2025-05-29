package main;

import java.io.*;
import java.nio.channels.Channels;
import java.nio.channels.FileChannel;
import java.nio.channels.FileLock;
import java.util.List;

import org.json.JSONObject;
import org.json.JSONTokener;

import entities.AnimatedEntity;
import entities.Jason;
import entities.Panam;

import java.awt.AWTException;

public class ComunicationAI {
	
	private List<Game> windows;
	private List<AnimatedEntity> animatedEntities;
	private GameLoop gl;
	private int TIME_SLEEP = 100;
	
	// Used to check in the game loop what send to the AI
	public boolean get_game = false;
	public boolean moving = false;
	
	public ComunicationAI(List<Game> windows, List<AnimatedEntity> animatedEntities, GameLoop gl) {
		this.windows = windows;
		this.animatedEntities = animatedEntities;
		this.gl = gl;
	}
	
	public void writeAck(String aiFile) {
	    JSONObject ack = new JSONObject();
	    ack.put("moving", moving);

	    try (RandomAccessFile file = new RandomAccessFile("ack_" + aiFile + ".json", "rw");
	         FileChannel channel = file.getChannel();
	         FileLock lock = channel.lock(0L, Long.MAX_VALUE, false)) {

	        file.setLength(0);
	        file.writeBytes(ack.toString());

	    } catch (Exception e) {
	    }
	}
	
	public void writeGameState(String aiFile) {
        try (RandomAccessFile file = new RandomAccessFile("game_state_"+ aiFile +".json", "rw");
             FileChannel channel = file.getChannel();
             FileLock lock = channel.lock(0L, Long.MAX_VALUE, false)) {
        	
        	JSONObject state = game_info();

            file.setLength(0);
            file.writeBytes(state.toString());

        } catch (Exception e) {
        }
    }
	
	public JSONObject readAIAction(String aiFile) {
        try (RandomAccessFile file = new RandomAccessFile("action_" + aiFile + ".json", "rw");
             FileChannel channel = file.getChannel();
             FileLock lock = channel.lock()) {
        	
        	InputStream is = Channels.newInputStream(channel);
    		
    		JSONTokener tokener = new JSONTokener(is);
            JSONObject obj = new JSONObject(tokener);
            
            file.setLength(0);
            
            return obj;
        } catch (Exception e) {
            return null;
        }
    }
        
    public JSONObject game_info() {
    	String status;
    	
    	JSONObject response = new JSONObject();
    	
    	JSONObject victim = new JSONObject();
    	Panam panam = (Panam) animatedEntities.getLast();
    	if (panam.hidden) {
    		status = "hide";
    	} else if (panam.interacting) {
    		status = "interact";
    	} else {
    		status = "visible";
    	}
    	victim.put("status", status);
    	victim.put("items", panam.listOfObject.size());
    	victim.put("map", panam.stage);
    	if (panam.step == panam.slow) {
    		victim.put("slow", true);                        		
    	} else {
    		victim.put("slow", false);
    	}
    	victim.put("speed", panam.dashing);
    	victim.put("win", gl.victimWin);
    	victim.put("dead", panam.dead);
    	victim.put("end-game", gl.end_game);
    	victim.put("finished", gl.timer_finished);

    	JSONObject killer = new JSONObject();
    	
    	Jason jason = (Jason) animatedEntities.getFirst();
    	if (jason.interacting) {
    		status = "interact";
    	} else {
    		status = "visible";
    	}
    	killer.put("status", status);
    	killer.put("map", jason.stage);
    	if (jason.stage == jason.slow) {
    		killer.put("slow", true);               		
    	} else {
    		killer.put("slow", false);
    	}
    	killer.put("win", gl.killerWin);
    	killer.put("end-game", gl.end_game);
    	killer.put("finished", gl.timer_finished);

    	response.put("victim", victim);
    	response.put("killer", killer);
    	
    	return response;
    }
    
    public void pressKey(String agent, String action) throws AWTException, InterruptedException {
    	if (agent.equals("killer")) {
    		AnimatedEntity ent = animatedEntities.get(0);
    		switch (action) {
    	    case "up":
    	    	this.windows.get(ent.stage).getKeyManager().keys[22] = true;
    	    	Thread.sleep(TIME_SLEEP);
    	    	this.windows.get(ent.stage).getKeyManager().keys[22] = false;
    	        break;
    	    case "down":
    	    	this.windows.get(ent.stage).getKeyManager().keys[18] = true;
    	    	Thread.sleep(TIME_SLEEP);
    	    	this.windows.get(ent.stage).getKeyManager().keys[18] = false;
    	        break;
    	    case "left":
    	    	this.windows.get(ent.stage).getKeyManager().keys[0] = true;
    	    	Thread.sleep(TIME_SLEEP);
    	    	this.windows.get(ent.stage).getKeyManager().keys[0] = false;
    	        break;
    	    case "right":
    	    	this.windows.get(ent.stage).getKeyManager().keys[3] = true;
    	    	Thread.sleep(TIME_SLEEP);
    	    	this.windows.get(ent.stage).getKeyManager().keys[3] = false;
    	        break;
    	    case "interact":
    	    	this.windows.get(ent.stage).getKeyManager().keys[4] = true;
    	    	Thread.sleep(TIME_SLEEP);
    	    	this.windows.get(ent.stage).getKeyManager().keys[4] = false;
    	        break;
    		}
    	} else {
    		AnimatedEntity ent = animatedEntities.get(1);
    		switch (action) {
    	    case "up":
    	    	this.windows.get(ent.stage).getKeyManager().keys[8] = true;
    	    	Thread.sleep(TIME_SLEEP);
    	    	this.windows.get(ent.stage).getKeyManager().keys[8] = false;
    	        break;
    	    case "down":
    	    	this.windows.get(ent.stage).getKeyManager().keys[10] = true;
    	    	Thread.sleep(TIME_SLEEP);
    	    	this.windows.get(ent.stage).getKeyManager().keys[10] = false;
    	        break;
    	    case "left":
    	    	this.windows.get(ent.stage).getKeyManager().keys[9] = true;
    	    	Thread.sleep(TIME_SLEEP);
    	    	this.windows.get(ent.stage).getKeyManager().keys[9] = false;
    	        break;
    	    case "right":
    	    	this.windows.get(ent.stage).getKeyManager().keys[11] = true;
    	    	Thread.sleep(TIME_SLEEP);
    	    	this.windows.get(ent.stage).getKeyManager().keys[11] = false;
    	        break;
    	    case "interact":
    	    	this.windows.get(ent.stage).getKeyManager().keys[14] = true;
    	    	Thread.sleep(TIME_SLEEP);
    	    	this.windows.get(ent.stage).getKeyManager().keys[14] = false;
    	        break;
    	    case "dash":
    	    	this.windows.get(ent.stage).getKeyManager().keys[15] = true;
    	    	Thread.sleep(3000);
    	    	this.windows.get(ent.stage).getKeyManager().keys[15] = false;
    	        break;
    		}
    	}
    }
}
