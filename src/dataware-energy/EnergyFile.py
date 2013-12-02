import hashlib
import logging
import base64
import random
import string
import time
import datetime
import ConfigParser
import csv
import sqlite3
import os

log = logging.getLogger( "console_log" )


class EnergyFile(object):
    ''' classdocs '''
    sqldb           = None
    sp              = 0
    dialect         = None
    datafile        = None
    datadir         = None
    dataname        = None
    tablename       = None
    lastupdate      = None
    ROLL_INTERVAL   = None
    
    #///////////////////////////////////////
    
    def __init__( self, configfile, section):
        self.CONFIG_FILE = configfile
        self.SECTION_NAME = section

        Config = ConfigParser.ConfigParser()
        Config.read( self.CONFIG_FILE )
        self.datadir        = Config.get( self.SECTION_NAME, "directory" )
        self.dataname       = Config.get(self.SECTION_NAME, "filename") 
        self.ROLL_INTERVAL  = int(Config.get(self.SECTION_NAME, "rollinterval")) * 3600
        print "Roll interval is %d seconds" % self.ROLL_INTERVAL
        self.sqldb          = sqlite3.connect(":memory:")
        success = self._set_file(index=1, drop=True)
        self._set_file(index = 0, drop= not(success))
        
        #self._set_file(index = 1, drop=False)
    
    def _set_file(self, index, drop=True):
    
        files = sorted([f for f in os.listdir(self.datadir) if self._is_match(os.path.join(self.datadir,f))], reverse=True) 
        
        if len(files) > index:
            self.lastupdate = time.time()
            latestfile  = os.path.join(self.datadir, files[index], self.dataname)  
            
            if self.datafile is None or latestfile != self.datafile:
                self.datafile    = os.path.join(self.datadir, files[index], self.dataname)  
                inhead, intail   = os.path.split(self.datafile)
                self.tablename   = os.path.splitext(intail)[0]
                start = time.time()
                self._csv_to_sqldb(self.datafile, self.tablename, drop)
                end = time.time()
                log.error("read in file in %f seconds" % (end-start))
                return True
        return False    
        
    def _is_match(self,f):
        if not os.path.isdir(f):
            return False
        inhead, intail = os.path.split(f)
        dirname = os.path.splitext(intail)[0]
        try:
            datetime.datetime.strptime(dirname, "%Y-%m-%d:%H:%M:%S")
            return True
        except ValueError, err:
            return False
        
    def _csv_to_sqldb(self, infilename, table_name, drop=True):
        self.dialect = csv.Sniffer().sniff(open(infilename, "rt").readline())
        inf = csv.reader(open(infilename, "rt"), self.dialect)
        column_names = inf.next()
        colstr = ",".join(column_names)   
        if drop:
            try:
                self.sqldb.execute("drop table %s;" % table_name)
            except:
                pass
                
            self.sqldb.execute("create table %s (%s);" % (table_name, colstr))
    
        for l in inf:
            if len(l) > 0:
                sql = "insert into %s values (%s);" % (table_name, self._quote_list_as_str(l))
                self.sqldb.execute(sql)
        self.sqldb.commit()
        self.sp = os.path.getsize(infilename)
    
    def update(self):
        
            
        if self.lastupdate is None or (self.lastupdate is not None and time.time() - self.lastupdate  > self.ROLL_INTERVAL):
             self._set_file(index=0,drop=True)
             return
        
        flen = os.path.getsize(self.datafile)
        
        if self.sp > 0 and self.sp < flen:
            myfile = open(self.datafile, "rt")
            inf = csv.reader(myfile, self.dialect)
            myfile.seek(self.sp+1)
            for l in inf:
                if len(l) > 0:
                    sql = "insert into %s values (%s);" % (self.tablename, self._quote_list_as_str(l))
                    self.sqldb.execute(sql)    
                        
            myfile.seek(0, os.SEEK_END)
            self.sp = myfile.tell() 
        elif self.sp > flen: #file has rotated, append the new one!
            print "doing file reload here! sp is %d and flen is %d" % (self.sp, flen)
            self._set_file(index=0,drop=False)
       
         
    def _quote_str(self,str):
        if len(str) == 0:
                return "''"
        if len(str) == 1:
                if str == "'":
                        return "''''"
                else:
                        return "'%s'" % str
        if str[0] != "'" or str[-1:] != "'":
                return "'%s'" % str.replace("'", "''")
        return str

    def _quote_list(self,l):
        return [self._quote_str(x) for x in l]

    def _quote_list_as_str(self,l):
        return ",".join(self._quote_list(l))

        
    def execute_query(self, query):
        
        self.update()
       
        curs = self.sqldb.cursor()
        
        try:
            curs.execute(query)
        except sqlite3.OperationalError, soe:
            return []
        except Exception, e:
            return []
      
        rows = curs.fetchall()
        desc = curs.description
        
        if desc:
            names = [d[0] for d in desc]
            return  [dict(map(None,names,y)) for y in rows]
        
        return rows
        
         
    def _latest_ts(self):
        query = """
                select max(ts) as ts from energy"""
        
       
        result = self.execute_query(query)      
        
     
        if result is None or len(result) == 0:
           
            return datetime.datetime.now()
         
        row = result[0]
        print "returning latest ts as %s" % datetime.datetime.strptime(row['ts'], "%Y/%m/%d:%H:%M:%S")
        return datetime.datetime.strptime(row['ts'], "%Y/%m/%d:%H:%M:%S")
        
    
    def fetch_summary(self, frm=None, to=None): 
        if to is not None:
            t2 = datetime.datetime.strptime(to, "%Y/%m/%d:%H:%M:%S")
        else:
            t2 = self._latest_ts()
            
        if frm is not None:
            t1 = datetime.datetime.strptime(frm, "%Y/%m/%d:%H:%M:%S") 
        else:
            t1 = datetime.datetime.fromtimestamp(time.mktime(t2.timetuple())- 1*60*60) 
        
        query = """
            select * from energy where ts > '%s' AND ts <= '%s' order by ts asc """ % (t1.strftime("%Y/%m/%d:%H:%M:%S") ,t2.strftime("%Y/%m/%d:%H:%M:%S") ) 
        
        results = self.execute_query( query )
        return results
    
    def generate_fake_data(self, items):
        cts = datetime.datetime.now()
        rightnow = cts.strftime("%Y/%m/%d:%H:%M:%S")
        #with open(dbfile, 'a') as f:
        #    f.write('ts,sensorId,watts')
       
        startduration = time.mktime(cts.timetuple()) - items*3
	r1 = random.randrange(200,300);
        r2 = random.randrange(50,200);
        r3 = random.randrange(0,100);
        dbfile = ""
    	for x in range(0, items):
    
          if (x % (self.ROLL_INTERVAL/3) == 0):
            directory = os.path.join(self.datadir,datetime.datetime.fromtimestamp(startduration + x*3).strftime("%Y-%m-%d:%H:%M:%S"))
        
            if not os.path.exists(directory):
                os.makedirs(directory)
        
            dbfile = os.path.join(self.datadir,directory,self.dataname)
          
            with open(dbfile, 'a') as f:
                f.write('ts,sensorId,watts')
                
       
          atime = datetime.datetime.fromtimestamp(startduration + x*3).strftime("%Y/%m/%d:%H:%M:%S")           
	    
	  r1min = -5 if r1 > 300 else -3  
	  r2min = -5 if r2 > 300 else -3 
	  r3min = -5 if r3 > 300 else -3 
	    
	  r1min = 2 if r1 <= 1 else r1min
	  r2min = 2 if r2 <= 1 else r2min
	  r3min = 2 if r3 <= 1 else r3min
	    
	  r1max = 5 if r1 < 100 else 3
	  r2max = 5 if r1 < 100 else 3
	  r3max = 5 if r1 < 100 else 3
	    
 	  r1 = r1 + random.randrange(r1min,r1max)
	  r2 = r2 + random.randrange(r2min,r2max)
	  r3 = r3 + random.randrange(r3min,r3max)
	    
	  try:
	    with open(dbfile, 'a') as f:
	      f.write('\n%s,%d,%f\n%s,%d,%f\n%s,%d,%f' % (atime, 88, r1, atime, 77, r2, atime, 66, r3))   
          except Exception, e:
              print e    
                
    def fetch_schema(self, table):
        return {}
