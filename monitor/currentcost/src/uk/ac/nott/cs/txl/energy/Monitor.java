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

import java.util.Date;
import java.util.Stack;
import java.text.SimpleDateFormat;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;

import java.io.FileInputStream;
import java.io.File;
import org.ini4j.Wini; 

public class Monitor implements Runnable, SerialPortEventListener{

    static CommPortIdentifier	portId;
	@SuppressWarnings("rawtypes")
	static Enumeration			portList;
	Scanner						inputScanner;
	SerialPort					serialPort;
	Thread						readThread;
    Connection                  connection;
    SimpleDateFormat format      = new SimpleDateFormat("yyyy/MM/dd:HH:mm:ss"); 
    String url, user, password;

	public static void main(String[] args)
	{
		boolean portFound = false;
		String defaultPort = "/dev/tty.usbserial";
		String iniFile = "/etc/dataware/energy_config.cfg";
		if (args.length >= 1)
		{
			defaultPort = args[0];
		}
	        if (args.length >= 2)
		{
			iniFile = args[1];        
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
					Monitor reader = new Monitor(iniFile);
				}
			}
		}
		if ( ! portFound)
		{
			System.out.println("port " + defaultPort + " not found.");
		}

	}

	public Monitor(String iniFile)
	{
		try
		{
		    
		    //read in config file
			
			try{
			    Wini ini = new Wini(new File(iniFile));
			    String hostname = ini.get("ResourceDB","hostname");
			    String db 	= ini.get("ResourceDB", "dbname");
	          	user   = ini.get("ResourceDB", "username");
			    password  = ini.get("ResourceDB", "password");
	            url = "jdbc:mysql://" + hostname + ":3306/" + db;
	            System.out.println(url);
			}catch(Exception e){
			    e.printStackTrace();
			    System.exit(-1);
			}
			serialPort = (SerialPort)portId.open("SimpleReadApp", 2000);
			inputScanner = new Scanner(serialPort.getInputStream());
			serialPort.addEventListener(this);
			serialPort.notifyOnDataAvailable(true);
			serialPort.setSerialPortParams(57600, SerialPort.DATABITS_8, SerialPort.STOPBITS_1, SerialPort.PARITY_NONE);
			
			try{
			    connection = DriverManager.getConnection(url, user, password);
			}catch(Exception e){
			    e.printStackTrace();
			    System.exit(-1);
			}
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

    public void insertCached(){
        
        
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
				
				Statement statement = null;
				Stack<String> cache = new Stack<String>();
				int index = 0;
				
				try{
				    statement = connection.createStatement();
				}
				catch(SQLException e){
				    e.printStackTrace();
				    break;
				}
				
				while (inputScanner.hasNext())
				{

					String parsableLine = inputScanner.next();
					
					System.err.println(parsableLine);
					
					if(parsableLine.contains("hist"))
					{
						// do nothing
						
					}
					else
					{
						if(parsableLine.contains("msg"))
						{
						    String stmt = "";
						    
							try
							{ 
							    String ts = format.format(new Date()); 
								int sensorId = Integer.parseInt(parseSingleElement(parsableLine, "id"));
								double value = Double.parseDouble(parseSingleElement(parsableLine, "watts"));
								
								if (value > 0){	    
								    
								    stmt = String.format("insert into energy_data values(\"%s\", '%d', '%f');", ts, sensorId, value);
								    statement.executeUpdate(stmt);  
								}
								
								//add any failed inserts.
								while (!cache.empty()){
								    stmt = cache.pop();
								    System.err.println(stmt);
								    statement.executeUpdate(stmt);  
								}
							}
							catch(SQLException se){
							    cache.push(stmt);  
							    try{
							        System.err.println("attempting reconnect");
                            		connection = DriverManager.getConnection(url, user, password);
                            		statement = connection.createStatement();
                        		}catch(Exception e){
								    System.err.println(e.getMessage());
                        		}
							}
							catch (NumberFormatException n)
							{
								n.printStackTrace();
							}
							catch (Exception e){
							  
							    System.err.println(e.getMessage());
							    e.printStackTrace();
							}
							if (parsableLine.contains("</msg>"))
							{

								
							}
						}
					}
			    } //end of inputScanner.hasNext()
			default:
			    break;
		}//end of switch
	}

	public String parseSingleElement(String m, String t)
	{
		int start = m.indexOf("<" + t + ">") + t.length() + 2;
		int end = m.indexOf("</" + t + ">");
		return (m.substring(start, end));
	}

}
