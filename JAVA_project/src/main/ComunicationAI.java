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
	String phase;
	
	public ComunicationAI(List<Game> windows, List<AnimatedEntity> animatedEntities, GameLoop gl, String phase) {
		this.windows = windows;
		this.animatedEntities = animatedEntities;
		this.gl = gl;
		this.phase = phase;
	}
	
	public void writeAck(String aiFile) {
	    JSONObject ack = new JSONObject();
	    ack.put("moving", true);

	    try (RandomAccessFile file = new RandomAccessFile("Comunications_files/ack_" + aiFile + ".json", "rw");
	         FileChannel channel = file.getChannel();
	         FileLock lock = channel.lock(0L, Long.MAX_VALUE, false)) {

	    	if (file.length() == 0) {
	    		file.setLength(0);
	    		file.writeBytes(ack.toString());
	    		file.getFD().sync();
	    	}
	    } catch (Exception e) {
	    }
	}
	
	public void writeGameState(String aiFile) {
		try (RandomAccessFile file1 = new RandomAccessFile("Comunications_files/game_state_" + aiFile + ".json", "rw");
				FileChannel channel1 = file1.getChannel();
				FileLock lock1 = channel1.lock(0L, Long.MAX_VALUE, false)) {
			
			JSONObject state = game_info();
			
			if (file1.length() == 0) {
				file1.setLength(0);
				file1.writeBytes(state.toString());
				file1.getFD().sync();
			}
			
		} catch (Exception e) {
		}
    }
	
	public void writeGameState(String aiFile1, String aiFile2) {
		while(true) {
			try (RandomAccessFile file1 = new RandomAccessFile("Comunications_files/game_state_" + aiFile1 + ".json", "rw");
					FileChannel channel1 = file1.getChannel();
					FileLock lock1 = channel1.lock(0L, Long.MAX_VALUE, false);
					
					RandomAccessFile file2 = new RandomAccessFile("Comunications_files/game_state_" + aiFile2 + ".json", "rw");
					FileChannel channel2 = file2.getChannel();
					FileLock lock2 = channel2.lock(0L, Long.MAX_VALUE, false)) {
				
				JSONObject state = game_info();
				
				if (!phase.equals("jason")) {
					if (file2.length() == 0) {
						file1.setLength(0);
						file1.writeBytes(state.toString());
						file1.getFD().sync();
						
						file2.setLength(0);
						file2.writeBytes(state.toString());
						file2.getFD().sync();
						break;
					} else {
						continue;
					}					
				} else {
					if (file2.length() == 0 && file1.length() == 0) {
						file1.setLength(0);
						file1.writeBytes(state.toString());
						file1.getFD().sync();
						
						file2.setLength(0);
						file2.writeBytes(state.toString());
						file2.getFD().sync();
						break;
					} else {
						continue;
					}
				}
				
			} catch (Exception e) {
			}
		}
    }
	
	public JSONObject readAIAction(String aiFile) {
		String path = "Comunications_files/action_" + aiFile + ".json";

        try (RandomAccessFile file = new RandomAccessFile(path, "rw");
             FileChannel channel = file.getChannel();
             FileLock lock = channel.lock(0L, Long.MAX_VALUE, false)) {

            if (file.length() == 0) {
                return null;
            }

            InputStream is = Channels.newInputStream(channel);
            JSONTokener tokener = new JSONTokener(is);
            JSONObject obj = new JSONObject(tokener);

            file.setLength(0);
            return obj;

        } catch (Exception e) {}
		return null;
    }
        
    public JSONObject game_info() {
    	String status;
    	
    	JSONObject response = new JSONObject();
    	
    	JSONObject victim = new JSONObject();
    	Panam panam = (Panam) animatedEntities.getLast();
    	if (panam.hidden) {
    		status = "hide";
    	} else if (panam.interaction) {
    		status = "interact";
    	} else {
    		status = "visible";
    	}
    	victim.put("status", status);
    	
    	victim.put("phone", panam.phone);
    	victim.put("battery", panam.battery);
    	
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
    	victim.put("agent_x", panam.x);
    	victim.put("agent_y", panam.y);
    	
    	int sub_map = 0;
    	
    	// Spawn point
    	if (280 <= panam.x && panam.x <= 548 && 16 <= panam.y && panam.y <= 92)
    		sub_map = 1;
    	// Fountain
    	else if(296 <= panam.x && panam.x <= 536 && 104 <= panam.y && panam.y <= 200)
    		sub_map = 2;
    	// Lake
    	else if(36 <= panam.x && panam.x <= 280 && 200 <= panam.y && panam.y <= 360)
    		sub_map = 3;
    	// High Grass
    	else if(440 <= panam.x && panam.x <= 760 && 224 <= panam.y && panam.y <= 360)
    		sub_map = 4;
    	
    	int[] dist1;
    	int[] dist2;
    	
    	// Battery
		dist1 = gl.gm.distance(0);
		
		
		// Phone
		dist2 = gl.gm.distance(1);
		
		if(panam.stage == 0 && panam.battery) {
			dist2 = new int[] {0, 0};
		}
    	
    	victim.put("sub_map", sub_map);
    	
    	// Distance from the house of the battery or distance from the phone
    	victim.put("distance_1_x", dist1[0]);
    	victim.put("distance_1_y", dist1[1]);
    	
    	// Distance from the house of the phone or distance from the battery
    	victim.put("distance_2_x", dist2[0]);
    	victim.put("distance_2_y", dist2[1]);
    	
    	JSONObject killer = new JSONObject();
    	
    	Jason jason = (Jason) animatedEntities.getFirst();
    	if (jason.interaction) {
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
    	
    	sub_map = 0;
    	
    	// Spawn point
    	if (280 <= jason.x && jason.x <= 548 && 16 <= jason.y && jason.y <= 92)
    		sub_map = 1;
    	// Right house
    	else if(572 <= jason.x && jason.x <= 764 && 76 <= jason.y && jason.y <= 200)
    		sub_map = 2;
    	// Fountain
    	else if(296 <= jason.x && jason.x <= 536 && 104 <= jason.y && jason.y <= 200)
    		sub_map = 3;
    	// Left House
    	else if(20 <= jason.x && jason.x <= 272 && 16 <= jason.y && jason.y <= 188)
    		sub_map = 4;
    	// Lake
    	else if(36 <= jason.x && jason.x <= 280 && 200 <= jason.y && jason.y <= 360)
    		sub_map = 5;
    	// High Grass
    	else if(440 <= jason.x && jason.x <= 760 && 224 <= jason.y && jason.y <= 360)
    		sub_map = 6;
    	
    	killer.put("sub_map", sub_map);
    	killer.put("agent_x", jason.x);
    	killer.put("agent_y", jason.y);

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