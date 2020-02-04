/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package arduinoReader;

import java.util.Scanner;
//import javax.swing.JFrame;
//import javax.swing.JSlider;
import com.fazecast.jSerialComm.*;

/**
 *
 * @author chpb5
 */
public class ArduinoReader {

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        // TODO code application logic here
        /*
            JFrame window = new JFrame();
            JSlider slider = new JSlider();
            slider.setMaximum(1023);
            window.add(slider);
            window.pack();
            window.setVisible(true);*/
        SerialPort[] ports = SerialPort.getCommPorts();
        System.out.println("Select a port:");
        int i = 1;
        for (SerialPort port : ports) {
            System.out.println(i++ + ": " + port.getSystemPortName());
        }
        Scanner s = new Scanner(System.in);
        int chosenPort = s.nextInt();

        SerialPort serialPort = ports[chosenPort - 1];
        if (serialPort.openPort()) {
            System.out.println("Port opened successfully.");
        } else {
            System.out.println("Unable to open the port.");
            return;
        }
        serialPort.setComPortParameters(9600, 8, 1, SerialPort.NO_PARITY);
        serialPort.setComPortTimeouts(SerialPort.TIMEOUT_NONBLOCKING, 0, 0);
        System.out.println("step1");
        Scanner data = new Scanner(serialPort.getInputStream());

//int value = 0;
        while (data.hasNext()) {
            System.out.println("step2");
            String str = data.nextLine();
//data.

            System.out.println(str + "Anas");
// try{value = Integer.parseInt(data.nextLine());}catch(Exception e){}
// slider.setValue(value);

        }

        try {
            while (true) {
                while (serialPort.bytesAvailable() == 0) {
                    Thread.sleep(20);
                }

                byte[] readBuffer = new byte[serialPort.bytesAvailable()];
                int numRead = serialPort.readBytes(readBuffer, readBuffer.length);
                System.out.println("Read " + numRead + " bytes." + readBuffer.toString());
                char c = 0;
                for(int j = 0; j < readBuffer.length; j++){
                    c = (char)readBuffer[j];
                    System.out.print(c + " ");
                }
                System.out.println();

            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        serialPort.closePort();
        System.out.println("Done.");
    }

}
