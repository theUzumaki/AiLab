package main;

import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;

public class KeyManager implements KeyListener{

	public boolean jump, enter, exit;
	public boolean[] keys= new boolean[26];

	@Override
	public void keyTyped(KeyEvent e) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void keyPressed(KeyEvent e) {
		int code= e.getKeyCode();
		switch(code) {
		case KeyEvent.VK_A: keys[0]= true; break;
		case KeyEvent.VK_B: keys[1]= true; break;
		case KeyEvent.VK_C: keys[2]= true; break;
		case KeyEvent.VK_D: keys[3]= true; break;
		case KeyEvent.VK_E: keys[4]= true; break;
		case KeyEvent.VK_F: keys[5]= true; break;
		case KeyEvent.VK_G: keys[6]= true; break;
		case KeyEvent.VK_H: keys[7]= true; break;
		case KeyEvent.VK_I: keys[8]= true; break;
		case KeyEvent.VK_J: keys[9]= true; break;
		case KeyEvent.VK_K: keys[10]= true; break;
		case KeyEvent.VK_L: keys[11]= true; break;
		case KeyEvent.VK_M: keys[12]= true; break;
		case KeyEvent.VK_N: keys[13]= true; break;
		case KeyEvent.VK_O: keys[14]= true; break;
		case KeyEvent.VK_P: keys[15]= true; break;
		case KeyEvent.VK_Q: keys[16]= true; break;
		case KeyEvent.VK_R: keys[17]= true; break;
		case KeyEvent.VK_S: keys[18]= true; break;
		case KeyEvent.VK_T: keys[19]= true; break;
		case KeyEvent.VK_U: keys[20]= true; break;
		case KeyEvent.VK_V: keys[21]= true; break;
		case KeyEvent.VK_W: keys[22]= true; break;
		case KeyEvent.VK_X: keys[23]= true; break;
		case KeyEvent.VK_Y: keys[24]= true; break;
		case KeyEvent.VK_Z: keys[25]= true; break;
		case KeyEvent.VK_SPACE: jump= true; break;
		case KeyEvent.VK_ENTER: enter= true; break;
		case KeyEvent.VK_ESCAPE: exit= true; break;
		}
	}

	@Override
	public void keyReleased(KeyEvent e) {
		int code= e.getKeyCode();
		switch(code) {
		case KeyEvent.VK_A: keys[0]= false; break;
		case KeyEvent.VK_B: keys[1]= false; break;
		case KeyEvent.VK_C: keys[2]= false; break;
		case KeyEvent.VK_D: keys[3]= false; break;
		case KeyEvent.VK_E: keys[4]= false; break;
		case KeyEvent.VK_F: keys[5]= false; break;
		case KeyEvent.VK_G: keys[6]= false; break;
		case KeyEvent.VK_H: keys[7]= false; break;
		case KeyEvent.VK_I: keys[8]= false; break;
		case KeyEvent.VK_J: keys[9]= false; break;
		case KeyEvent.VK_K: keys[10]= false; break;
		case KeyEvent.VK_L: keys[11]= false; break;
		case KeyEvent.VK_M: keys[12]= false; break;
		case KeyEvent.VK_N: keys[13]= false; break;
		case KeyEvent.VK_O: keys[14]= false; break;
		case KeyEvent.VK_P: keys[15]= false; break;
		case KeyEvent.VK_Q: keys[16]= false; break;
		case KeyEvent.VK_R: keys[17]= false; break;
		case KeyEvent.VK_S: keys[18]= false; break;
		case KeyEvent.VK_T: keys[19]= false; break;
		case KeyEvent.VK_U: keys[20]= false; break;
		case KeyEvent.VK_V: keys[21]= false; break;
		case KeyEvent.VK_W: keys[22]= false; break;
		case KeyEvent.VK_X: keys[23]= false; break;
		case KeyEvent.VK_Y: keys[24]= false; break;
		case KeyEvent.VK_Z: keys[25]= false; break;
		case KeyEvent.VK_SPACE: jump= false; break;
		case KeyEvent.VK_ENTER: enter= false; break;
		case KeyEvent.VK_ESCAPE: exit= false; break;
		}
	}

}
