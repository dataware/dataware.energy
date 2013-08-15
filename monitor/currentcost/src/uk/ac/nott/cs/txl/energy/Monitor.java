package uk.ac.nott.cs.txl.energy;

import gnu.io.CommPortIdentifier;
import gnu.io.PortInUseException;
import gnu.io.SerialPort;
import gnu.io.SerialPortEvent;
import gnu.io.SerialPortEventListener;
import gnu.io.UnsupportedCommOperationException;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.Scanner;
import java.util.TooManyListenersException;

import org.hwdb.srpc.*;
import java.util.Date;
import java.text.SimpleDateFormat;

public class Monitor implements Runnable, SerialPortEventListener{

    static CommPortIdentifier	portId;
	@SuppressWarnings("rawtypes")
	static Enumeration			portList;
	Scanner						inputScanner;
	SerialPort					serialPort;
	Thread						readThread;
    Connection                  connection;
    SimpleDateFormat format      = new SimpleDateFormat("yyyy/MM/dd:HH:mm:ss"); 

	public static void main(String[] args)
	{
		boolean portFound = false;
		String defaultPort = "/dev/tty.usbserial";
		if (args.length != 1)
		{
			System.out.println("YOU FAIL");
			System.exit( - 1);
		}
		else
		{
			//hubId = Integer.parseInt(args[0]);
			defaultPort = args[0];
			//user = args[2];
			//apiKey = args[3];
		}
		portList = CommPortIdentifier.getPortIdentifiers();
		while (portList.hasMoreElements())
		{
			portId = (CommPortIdentifier)portList.nextElement();
			if (portId.getPortType() == CommPortIdentifier.PORT_SERIAL)
			{
				if (portId.getName().equals(defaultPort))
				{
					System.out.println("Found port: " + defaultPort);
					portFound = true;
					@SuppressWarnings("unused")
					Monitor reader = new Monitor();
				}
			}
		}
		if ( ! portFound)
		{
			System.out.println("port " + defaultPort + " not found.");
		}

	}

	public Monitor()
	{
		try
		{
		  
			
			serialPort = (SerialPort)portId.open("SimpleReadApp", 2000);
			inputScanner = new Scanner(serialPort.getInputStream());
			serialPort.addEventListener(this);
			serialPort.notifyOnDataAvailable(true);
			serialPort.setSerialPortParams(57600, SerialPort.DATABITS_8, SerialPort.STOPBITS_1, SerialPort.PARITY_NONE);
			
			
			try{
			    SRPC srpc = new SRPC();
			
			    byte[] addr = new byte[]{
			        (byte) 127,
			        (byte) 0,
			        (byte) 0,
			        (byte) 1
			    };
			
		    	connection = srpc.connect(addr, 987, "HWDB");
			}catch(Exception e){
			    System.err.println("Error connecting to database");
			}
			
			//readThread = new Thread(this);
			//readThread.start();

		}
		catch (PortInUseException e)
		{
			e.printStackTrace();
		}
		catch (IOException e)
		{
			e.printStackTrace();
		}
		catch (TooManyListenersException e)
		{
			e.printStackTrace();
		}
		catch (UnsupportedCommOperationException e)
		{
			e.printStackTrace();
		}

	}

	public void run()
	{

	}

	public void serialEvent(SerialPortEvent event)
	{
		switch (event.getEventType())
		{

			case SerialPortEvent.BI:

			case SerialPortEvent.OE:

			case SerialPortEvent.FE:

			case SerialPortEvent.PE:

			case SerialPortEvent.CD:

			case SerialPortEvent.CTS:

			case SerialPortEvent.DSR:

			case SerialPortEvent.RI:

			case SerialPortEvent.OUTPUT_BUFFER_EMPTY:
				break;

			case SerialPortEvent.DATA_AVAILABLE:
				//ArrayList<Reading> readings = new ArrayList<Reading>();
				
				
				System.out.println("starting input scanner");
				
				while (inputScanner.hasNext())
				{

					String parsableLine = inputScanner.next();
					System.out.println(parsableLine);
					if(parsableLine.contains("hist"))
					{
						// do nothing
					}
					else
					{
						if(parsableLine.contains("msg"))
						{
							try
							{
							    String ts = format.format(new Date());
							    
								int sensorId = Integer.parseInt(parseSingleElement(parsableLine, "id"));
								double value = Double.parseDouble(parseSingleElement(parsableLine, "watts"));
								
								System.out.println(ts + " " + sensorId + " " + value);
								
								if (value > 0){
								    String stmt = String.format("SQL: insert into EnergyUse values(\"%s\", '%d', '%f')", ts, sensorId, value);
								    System.out.println(stmt);
		                            System.out.println(connection.call(stmt));
								}
								//readings.add(new Reading(sensorId, value));
							}
							catch(IOException ioe){
							    ioe.printStackTrace();
							}
							catch (NumberFormatException n)
							{
								n.printStackTrace();
							}
							if (parsableLine.contains("</msg>"))
							{

								
							}
						}
					}
				}
		}
	}

	public String parseSingleElement(String m, String t)
	{
		int start = m.indexOf("<" + t + ">") + t.length() + 2;
		int end = m.indexOf("</" + t + ">");
		return (m.substring(start, end));
	}

}
