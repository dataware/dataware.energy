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
import java.util.Random;

import java.util.Date;
import java.util.Stack;
import java.util.TimeZone;
import java.text.SimpleDateFormat;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;

import java.io.BufferedWriter;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.File;
import java.io.FileWriter;
import java.nio.channels.FileChannel;
import org.ini4j.Wini; 

public class Monitor implements Runnable, SerialPortEventListener{

    static CommPortIdentifier	    portId;
    static int ROLL_INTERVAL;
    
	@SuppressWarnings("rawtypes")
	static Enumeration			portList;
	Scanner						inputScanner;
	SerialPort					serialPort;
	Thread						readThread;
    Connection                  connection;
    SimpleDateFormat format      = new SimpleDateFormat("yyyy/MM/dd:HH:mm:ss");
    SimpleDateFormat dirformat   = new SimpleDateFormat("yyyy-MM-dd:HH:mm:ss");
    Date                         start;
    Random random                = new Random(System.currentTimeMillis()); 
    String                       datafile, datadir, filename;
    
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
			    Wini ini        = new Wini(new File(iniFile));
		        datadir         =  ini.get("Data","directory");
	            filename        =  ini.get("Data", "filename");
	            ROLL_INTERVAL   = Integer.valueOf(ini.get("Data", "rollinterval"));
			    createNewFile();
			}catch(Exception e){
			    e.printStackTrace();
			    System.exit(-1);
			}
			serialPort = (SerialPort)portId.open("SimpleReadApp", 2000);
			inputScanner = new Scanner(serialPort.getInputStream());
			serialPort.addEventListener(this);
			serialPort.notifyOnDataAvailable(true);
			serialPort.setSerialPortParams(57600, SerialPort.DATABITS_8, SerialPort.STOPBITS_1, SerialPort.PARITY_NONE);
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

    public void createNewFile() throws IOException{
       
        start = new Date();
		format.format(start);
		String directory =  String.format("%s/%s",datadir,dirformat.format(start));
		datafile = String.format("%s/%s/%s",datadir,dirformat.format(start),filename);
		File f = new File(directory);
		f.mkdirs();
		
		File dfile = new File(datafile);
        dfile.createNewFile();
	    File tmp = new File(dfile.getParentFile(), dfile.getName()+".tmp");
		FileWriter fw = new FileWriter(tmp, true);
		BufferedWriter bw = new BufferedWriter(fw);
  		bw.write("ts,sensorId,watts");
		bw.close();
		tmp.renameTo(dfile);
    }   
    
    public void copyFile(File src, File dst) throws IOException{
        if (!dst.exists()){
            dst.createNewFile();
        }
        FileChannel source = null;
        FileChannel destination = null;
        
        try{
            source = new FileInputStream(src).getChannel();
            destination = new FileOutputStream(dst).getChannel();
            destination.transferFrom(source,0,source.size());
        }finally{
            if (source != null){
                source.close();
            }
            if (destination != null){
                destination.close();
            }
        }
    }
    
	public void run()
	{

	}

    public void insertCached(){
        
        
    }
    
	public void serialEvent(SerialPortEvent event)
	{
		format.setTimeZone(TimeZone.getTimeZone("Europe/London"));
		
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
							    double v1 = random.nextDouble() * 500;	
   								double v2 = random.nextDouble() * 500;
  								double v3 = random.nextDouble() * 500;
								
								if (value >= 0){	
								    
								    String csv  = String.format("\n%s,%d,%f",ts,sensorId,v1); 
  								    csv += String.format("\n%s,%d,%f",ts,66,v2); 
     								csv += String.format("\n%s,%d,%f",ts,22,v3);
     								      
								    try{ //atomic write
								      
								      if ( (new Date().getTime() - start.getTime())/1000 > ROLL_INTERVAL){
								        System.err.println("rolling logs");
								        createNewFile();
								      }
								      
								      File in  = new File(datafile);
								      File out = new File(in.getParentFile(), in.getName()+".tmp");
								      copyFile(in, out);  
								      
								      //write to tmp copy  
								      FileWriter fw = new FileWriter(out, true);
								      BufferedWriter bw = new BufferedWriter(fw);
  								      bw.write(csv);
								      bw.close();
								      
								      //rename (atomic) to original
								      out.renameTo(in);
								      
								    }
								    catch(IOException e){
									    System.err.println("failed to create/write file " + e.getMessage());
         							}   
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
