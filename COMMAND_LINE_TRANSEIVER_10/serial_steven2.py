import serial as sl  
import time  
import datetime  
  
ser = sl.Serial('/dev/tty.usbserial-1410',9600)   
  
flag = 1;  
tflag = 0;  
  
oldMinute=100000.;  
bufsize=0;  
while True: # Run loop indefinitely   
        ts = datetime.datetime.now();  
        if (flag==1): #Open a new file every day  
                datafile = open('./data_'+str(ts.year)+'_'+str(ts.month)+'_'+str(ts.day)+'.dat','w');  
                datafile.write('#time      light \n');  
                old_Day=ts.day;  
                flag=0;  
  
        Minute = ts.minute/60.;  
        Hour = ts.hour;  
        timeout = Hour + Minute;  
  
        MHP = ts.minute%1.; # Planning to change this line of code such that it writes every 5 or 10 minutes  
        print(MHP)  
          
        if (MHP < 1.e-5): # Write data to file every minute  
                if(Minute!=oldMinute):  
                        tflag = 1;  
                        oldMinute=Minute;  
        if( tflag == 1):  
                ser.write(b'0') #Send data to arduino. Activate arduino read pin and write to serial  
                while (ser.inWaiting()<0): #Do while loop waiting for data   
                        time.sleep(0.1)  
                data1= ser.readline()  
                datafile.write(' '+str(timeout)+'\t'+str(data1))  
                tflag = 0;  
                print(timeout)  
        time.sleep(10)  
        if (ts.day != old_Day): # Close file after day is finished  
                datafile.close();  
                flag=1;  