'''    
Created on 12 April 2011
@author: jog
'''

import MySQLdb
import ConfigParser
import hashlib
import logging
import base64
import random
import string
import time

log = logging.getLogger( "console_log" )


#///////////////////////////////////////


def safety_mysql( fn ) :
    """ I have included this decorator because there are no 
    gaurantees the user has mySQL setup so that it won't time out. 
    If it has, this function remedies it, by trying (one shot) to
    reconnect to the database.
    """

    def wrapper( self, *args, **kwargs ) :
        try:
            return fn( self, *args, **kwargs )
        except MySQLdb.Error, e:
            if e[ 0 ] == 2006:
                self.reconnect()
                return fn( self, *args, **kwargs )
            else:
                raise e   
    return wrapper


#///////////////////////////////////////


class ResourceDB(object):
    ''' classdocs '''
    
    #///////////////////////////////////////
    
    def __init__( self, configfile, section, name = "ResourceDB" ):
            
        #MysqlDb is not thread safe, so program may run more
        #than one connection. As such naming them is useful.
        self.name = name
        self.CONFIG_FILE = configfile
        self.SECTION_NAME = section
        
        Config = ConfigParser.ConfigParser()
        Config.read( self.CONFIG_FILE )
        self.hostname = Config.get( self.SECTION_NAME, "hostname" )
        self.username =  Config.get( self.SECTION_NAME, "username" )
        self.password =  Config.get( self.SECTION_NAME, "password" )
        self.DB_NAME = Config.get( self.SECTION_NAME, "dbname" )
        
        self.connected = False;
        
        self.TBL_SKELETON = 'skeleton_data'
        
         #///////////////////////////////////////
    
        self.createQueries = [ 
                   
            ( self.TBL_SKELETON, """
                CREATE TABLE %s.%s (
                    ts int(11), 
                    name varchar(19), 
                    value int(11), 
                    PRIMARY KEY (ts,name)
                ) DEFAULT CHARSET=latin1;
            """  % ( self.DB_NAME , self.TBL_SKELETON ) ),
           
        ] 
        
    #///////////////////////////////////////
    
        
    def connect( self ):
        
        log.debug( "%s: connecting to mysql database..." % self.name )

        self.conn = MySQLdb.connect( 
            host=self.hostname,
            user=self.username,
            passwd=self.password,
            db=self.DB_NAME
        )
 
        self.cursor = self.conn.cursor( MySQLdb.cursors.DictCursor )
        self.connected = True
                    
                    
    #///////////////////////////////////////
    
    
    def reconnect( self ):
        
        log.debug( "%s: Database reconnection process activated..." % self.name );
        self.close()
        self.connect()
        

    #///////////////////////////////////////
          
    
    @safety_mysql
    def commit( self ) : 
        self.conn.commit();
        
        
    #///////////////////////////////////////
        
          
    def close( self ) :   
        if self.conn.open:
            log.debug( "%s: disconnecting from mysql database..." % self.name );
            self.cursor.close();
            self.conn.close();
                
                       
    #/////////////////////////////////////////////////////////////////////////////////////////////
    
    
    @safety_mysql
    def check_tables( self ):
        
        log.info( "%s: checking system table integrity..." % self.name );
        
        #-- first check that the database itself exists        
        self.cursor.execute ( """
            SELECT 1
            FROM information_schema.`SCHEMATA`
            WHERE schema_name='%s'
        """ % self.DB_NAME )
                
        row = self.cursor.fetchone()

        if ( row is None ):
            log.info( "%s: database does not exist - creating..." % self.name );    
            self.cursor.execute ( "CREATE DATABASE IF NOT EXISTS catalog" )
        
        
        #-- then check it is populated with the required tables            
        self.cursor.execute ( """
            SELECT table_name
            FROM information_schema.`TABLES`
            WHERE table_schema='%s'
        """ % self.DB_NAME )
        
        tables = [ row[ "table_name" ].lower() for row in self.cursor.fetchall() ]
 
        #if they don't exist for some reason, create them.    
        for item in self.createQueries:
            if not item[ 0 ].lower() in tables : 
                log.warning( "%s: Creating missing system table: '%s'" % ( self.name, item[ 0 ] ) );
                self.cursor.execute( item[ 1 ] )

        self.commit()
    
        
    #/////////////////////////////////////////////////////////////////////////////////////////////
    @safety_mysql
    def execute_query(self, query):
    
        log.info("exec query: %s" % query)
        self.cursor.execute( query )
        
        row = self.cursor.fetchall()

        if not row is None:
            return row
        else :
            return None    
    
    
    @safety_mysql                
    def fetch_summary( self) :
        
        query = """
            SELECT * FROM %s.%s ORDER BY ts DESC LIMIT 100
        """  % ( self.DB_NAME, self.TBL_SKELETON) 
   
	
        self.cursor.execute( query )
        row = self.cursor.fetchall()

        if not row is None:
            return row
        else :
            return []

    @safety_mysql
    def fetch_schema(self, table):
        query = """
                            SELECT column_name, data_type, is_nullable, character_maximum_length, numeric_precision 
                            FROM information_schema.COLUMNS 
                            WHERE table_name='%s' 
                            AND table_schema = '%s'
                            """ % (table, self.DB_NAME)
        self.cursor.execute( query )                    
        results = self.cursor.fetchall()
        return results

    @safety_mysql                
    def generate_data( self) :
        query = """
            INSERT INTO  %s.%s (ts, name, value) VALUES (%s, %s, %s)
        """  % ( self.DB_NAME, self.TBL_SKELETON, '%s', '%s', '%s') 
   
        [self.cursor.execute(query, (int(time.time()), 
                                        "".join([random.choice(string.letters[:26]) for i in xrange(12)]), 
                                        random.randint(0,1000))) for z in xrange(100)]
             
        self.commit()