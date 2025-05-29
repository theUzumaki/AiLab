package main;

import java.io.RandomAccessFile;
import java.nio.channels.FileChannel;
import java.nio.channels.FileLock;

public class FileLocker {
    private RandomAccessFile file;
    public FileChannel channel;
    private FileLock lock;

    // 🔐 Acquisisce il lock (bloccante, condiviso o esclusivo)
    public void lockFile(String path, boolean shared) throws Exception {
        file = new RandomAccessFile(path, "rw"); // usa "r" se non devi scrivere
        channel = file.getChannel();
        lock = channel.lock(0L, Long.MAX_VALUE, shared); // true = shared, false = exclusive
        System.out.println("🔒 File lock acquisito");
    }

    // 🔓 Rilascia il lock e chiude le risorse
    public void unlockFile() {
        try {
            if (lock != null) {
                lock.release();
                System.out.println("🔓 Lock rilasciato");
            }
            if (channel != null) {
                channel.close();
            }
            if (file != null) {
                file.close();
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
