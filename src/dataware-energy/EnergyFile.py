import hashlib
import logging
import base64
import random
import string
import time
import datetime
import ConfigParser
from squawk import Query
from squawk import CSVParser
import csv
import sqlite3
import os
log = logging.getLogger( "console_log" )


class EnergyFile(object):
    ''' classdocs '''
    sqldb = None
    sp = 0
    dialect = None
    datafile = None
    tablename = None
    
    #///////////////////////////////////////
    
    def __init__( self, configfile, section):
        self.CONFIG_FILE = configfile
        self.SECTION_NAME = section

        Config = ConfigParser.ConfigParser()
        Config.read( self.CONFIG_FILE )
        datadir     = Config.get( self.SECTION_NAME, "directory" )
        dataname    = Config.get(self.SECTION_NAME, "filename") 
       
        self.datafile = os.path.join(datadir,dataname)
        self.sqldb = sqlite3.connect(":memory:")
        inhead, intail = os.path.split(self.datafile)
        self.tablename = os.path.splitext(intail)[0]
        start = time.time()
        log.error("reading in energy file %s, table %s" % (self.datafile,self.tablename))
        self._csv_to_sqldb(self.datafile, self.tablename)
        end = time.time()
        log.error("done %f" % (end-start))
       
    def _csv_to_sqldb(self, infilename, table_name):
        self.dialect = csv.Sniffer().sniff(open(infilename, "rt").readline())
        inf = csv.reader(open(infilename, "rt"), self.dialect)
        column_names = inf.next()
        colstr = ",".join(column_names)   
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
    
    def update(self, infilename, table_name):
        
        #manage memory - if updates fail, recreate database from latest file
        
        if self.sp <= 0:
            return
       
        flen = os.path.getsize(infilename)
      
        if self.sp > flen:
            print "regenerating table from file!!"
            self._csv_to_sqldb(self.datafile, self.tablename)
            return
             
        if self.sp < flen:
            myfile = open(infilename, "rt")
            inf = csv.reader(myfile, self.dialect)
            myfile.seek(self.sp+1)
            for l in inf:
                if len(l) > 0:
                    sql = "insert into %s values (%s);" % (table_name, self._quote_list_as_str(l))
                    self.sqldb.execute(sql)    
                        
            myfile.seek(0, os.SEEK_END)
            self.sp = myfile.tell()
    
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
        #sqldb = sqlite3.connect(":memory:") 
        self.update(self.datafile,self.tablename)
        curs = self.sqldb.cursor()
        
        try:
            curs.execute(query)
        except sqlite.OperationalError, soe:
            #rebuild here!!
            raise
        except Exception, e:
            raise
            
        rows = curs.fetchall()
        desc = curs.description
        
        if desc:
            names = [d[0] for d in desc]
            return  [dict(map(None,names,y)) for y in rows]
        
        return rows
        
          
    
    def execute_query_old(self, query):
        #this loads the data into memory!
        #maybe retrieve table here? or assume known.
        source = CSVParser(dbfile)
        q = Query(query)
        result = []
        
        for row in q(source): 
            result.append(row)
        
        return result
        
    def _latest_ts(self):
        query = """
                select max(ts) as ts from energy"""

        result = self.execute_query(query)      
      
        if result is []:
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
        with open(dbfile, 'a') as f:
            f.write('ts,sensorId,watts')
        #startduration = time.mktime(cts.timetuple()) - items*60
        
        #for x in range(0, items):
            #tt = time.mktime(cts.timetuple())
        #    atime = datetime.datetime.fromtimestamp(startduration + x*60).strftime("%Y/%m/%d:%H:%M:%S")        
        #    reading = random.randrange(100,300)
        
        startduration = time.mktime(cts.timetuple()) - items*3
	r1 = random.randrange(200,300);
        r2 = random.randrange(50,200);
        r3 = random.randrange(0,100);
        
	for x in range(0, items):
            #tt = time.mktime(cts.timetuple())
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
	       	  f.write('\n%s,%d,%f' % (atime, 88, r1))  
	       	  f.write('\n%s,%d,%f' % (atime, 77, r2))  
	       	  f.write('\n%s,%d,%f' % (atime, 66, r3))    
            except Exception, e:
                print e    
                
    def fetch_schema(self, table):
        return {}
