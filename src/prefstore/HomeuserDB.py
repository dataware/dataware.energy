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


class HomeDB( object ):
    ''' classdocs '''
    
    DB_NAME = 'Homework'
    TBL_TERM_URLS = 'DNSRequest'
    TBL_TERM_POWER = 'EnergyUse'  
    TBL_DATAWARE_PROCESSORS = 'tblDatawareProcessors'
    TBL_DATAWARE_CATALOGS = 'tblDatawareCatalogs'
    TBL_DATAWARE_INSTALLS = 'tblDatawareInstalls'
    
    CONFIG_FILE = "prefstore.cfg"
    SECTION_NAME = "HomeuserDB"


     #///////////////////////////////////////

  
    createQueries = [ 
               
        ( TBL_DATAWARE_PROCESSORS, """
            CREATE TABLE %s.%s (
                access_token varchar(256) NOT NULL,
                client_id varchar(256) NOT NULL,
                user_id varchar(256) NOT NULL,
                expiry_time int(11) unsigned NOT NULL,
                query text NOT NULL,
                checksum varchar(256) NOT NULL,
                PRIMARY KEY (access_token),
                UNIQUE KEY (client_id,user_id,checksum)
            ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
        """  % ( DB_NAME, TBL_DATAWARE_PROCESSORS ) ),
       
        ( TBL_DATAWARE_CATALOGS, """ 
            CREATE TABLE %s.%s (
                catalog_uri varchar(256) NOT NULL,                
                resource_id varchar(256) NOT NULL,
                registered int(10) unsigned DEFAULT NULL,
                PRIMARY KEY (catalog_uri)
            ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
        """  % ( DB_NAME, TBL_DATAWARE_CATALOGS ) ),  
        
        ( TBL_DATAWARE_INSTALLS, """ 
            CREATE TABLE %s.%s (
                user_id varchar(256) NOT NULL,
                catalog_uri varchar(256) NOT NULL,                
                install_token varchar(256),
                state varchar(256) NOT NULL,
                registered int(10) unsigned DEFAULT NULL,
                PRIMARY KEY (user_id),
                FOREIGN KEY (catalog_uri) REFERENCES %s(catalog_uri) 
                ON DELETE CASCADE ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
        """  % ( DB_NAME, TBL_DATAWARE_INSTALLS, TBL_DATAWARE_CATALOGS ) ),            
    ] 
    
    #///////////////////////////////////////
    
    
    def __init__( self, name = "HomeuserDB" ):
            
        #MysqlDb is not thread safe, so program may run more
        #than one connection. As such naming them is useful.
        self.name = name
        
        Config = ConfigParser.ConfigParser()
        Config.read( self.CONFIG_FILE )
        self.hostname = Config.get( self.SECTION_NAME, "hostname" )
        self.username =  Config.get( self.SECTION_NAME, "username" )
        self.password =  Config.get( self.SECTION_NAME, "password" )
        self.dbname = Config.get( self.SECTION_NAME, "dbname" )
        self.connected = False;
        
        
    #///////////////////////////////////////
    
        
    def connect( self ):
        
        log.debug( "%s: connecting to mysql database..." % self.name )

        self.conn = MySQLdb.connect( 
            host=self.hostname,
            user=self.username,
            passwd=self.password,
            db=self.dbname
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

        self.commit();
    
    
        #////////////////////////////////////////////////////////////////////////////////////////////


    @safety_mysql   
    def insert_processor( self, access_token, client_id, user_name, expiry_time, query_code ):
        log.info("query code %s" % query_code)
        #create a SHA checksum for the file
        checksum = hashlib.sha1( query_code ).hexdigest()
        log.info("checksum %s" % checksum)
        query = """
             INSERT INTO %s.%s VALUES ( %s, %s, %s, %s, %s, %s )
        """  % ( self.DB_NAME, self.TBL_DATAWARE_PROCESSORS, '%s', '%s', '%s', '%s', '%s', '%s' ) 
        
        #this is failing..
        log.info("am in the insert processor %s" % query)
        
        self.cursor.execute( 
            query, ( 
                access_token, 
                client_id, 
                user_name, 
                expiry_time, 
                query_code, 
                checksum 
            ) 
        )
        self.commit()
        
        
    
    #///////////////////////////////////////////////
    
    
    @safety_mysql       
    def delete_processor( self, user_id, access_token ):

        query = """
             DELETE FROM %s.%s WHERE user_id = %s AND access_token = %s
        """  % ( self.DB_NAME, self.TBL_DATAWARE_PROCESSORS, '%s', '%s' ) 

        self.cursor.execute( query, ( user_id, access_token, ) )
        self.commit()
                
        #how many rows have been affected?
        if ( self.cursor.rowcount == 0 ) : 
            return False
        else :
            return True 
        
    
    
    #///////////////////////////////////////////////
    
    
    @safety_mysql       
    def fetch_processor( self, access_token ):
        
        query = """
            SELECT * FROM %s.%s WHERE access_token = %s
        """  % ( self.DB_NAME, self.TBL_DATAWARE_PROCESSORS, '%s' ) 
        self.cursor.execute( query, access_token )
        row = self.cursor.fetchone()
        return row
    
    
    #///////////////////////////////////////
    
    
    @safety_mysql                    
    def insert_catalog( self, catalog_uri, resource_id ):
            
        if ( catalog_uri ):
            
            log.info( 
                "%s %s: Inserting catalog '%s' in database with resource_id '%s'" 
                % ( self.name, "insert_catalog", catalog_uri, resource_id ) 
            );
            
            query = """
                  INSERT INTO %s.%s ( catalog_uri, resource_id, registered ) 
                  VALUES ( %s, %s, %s )
              """  % ( self.DB_NAME, self.TBL_DATAWARE_CATALOGS, '%s', '%s', '%s', )
            
            state = self.generateAccessToken()
            log.info("query is %s %s %s %s" % (query, catalog_uri, resource_id, time.time()));
            self.cursor.execute( query, ( catalog_uri, resource_id, time.time(), ) )
                
            return state;
        
        else:
            log.warning( 
                "%s %s: Catalog insert requested with incomplete details" 
                % (  self.name, "insert_catalog", ) 
            );
            return None;    
        
        
    #///////////////////////////////////////
    
    
    @safety_mysql                    
    def fetch_catalog( self, catalog_uri ):
            
        if catalog_uri :
            query = """
                SELECT * FROM %s.%s t where catalog_uri = %s 
            """  % ( self.DB_NAME, self.TBL_DATAWARE_CATALOGS, '%s' ) 
        
            self.cursor.execute( query, ( catalog_uri, ) )
            row = self.cursor.fetchone()

            if not row is None:
                return row
            else :
                return None
        else :
            return None   
            
        
                
    #///////////////////////////////////////
    
    
    @safety_mysql                    
    def insert_install( self, user_id, catalog_uri ):
            
        if ( user_id and catalog_uri ):
            
            log.info( 
                "%s %s: Initiating user '%s' installation to '%s' in database" 
                % ( self.name, "insert_install", user_id, catalog_uri, ) 
            );
            
            
            query = """
                  INSERT INTO %s.%s 
                  ( user_id, catalog_uri, install_token, state, registered ) 
                  VALUES ( %s, %s, null, %s, %s )
              """  % ( self.DB_NAME, self.TBL_DATAWARE_INSTALLS, '%s', '%s', '%s', '%s' )
            
            state = self.generateAccessToken()
            self.cursor.execute( query, 
                ( user_id, catalog_uri, state, time.time(), ) )
                
            return state;
        
        else:
            log.warning( 
                "%s %s: Installation insert requested with incomplete details" 
                % (  self.name, "insert_catalog", ) 
            );
            return None;    
        

    #///////////////////////////////////////
    
    
    @safety_mysql                    
    def update_install( self, user_id, catalog_uri, install_token ):
            
        if ( user_id and catalog_uri and install_token ):
            
            query = """
                  UPDATE %s.%s SET install_token=%s, registered=%s
                  WHERE user_id=%s AND catalog_uri=%s
              """  % ( self.DB_NAME, self.TBL_DATAWARE_INSTALLS, '%s', '%s', '%s', '%s' )
           
            update = self.cursor.execute( query, 
                ( install_token, time.time(), user_id, catalog_uri, ) )

            if update > 0 :
                log.debug( 
                    "%s %s: Updating installation for user '%s' to catalog '%s'" 
                    % ( self.name, "update_install", user_id, catalog_uri, ) 
                );
                return True
            else:
                log.warning( 
                    "%s: trying to update an unknown installation for user '%s'" 
                    % (self.name, user_id ) 
                )
                return False                
        else:
            log.warning( 
                "%s %s: Installation update requested with incomplete details" 
                % (  self.name, "insert_catalog", ) 
            );
            
            return False;   
        

    #///////////////////////////////////////
    
    
    @safety_mysql                    
    def delete_install( self, user_id, catalog_uri ):
            
        if ( user_id and catalog_uri  ):
            
            query = """
                  DELETE FROM %s.%s 
                  WHERE user_id=%s AND catalog_uri=%s
              """  % ( self.DB_NAME, self.TBL_DATAWARE_INSTALLS, '%s', '%s' )
           
            self.cursor.execute( query, ( user_id, catalog_uri, ) )

            log.info( 
                "%s %s: Deleting user '%s' installation to '%s' database" 
                % ( self.name, "delete_install", user_id, catalog_uri, ) 
            );                
        else:
            log.warning( 
                "%s %s: Installation delete requested with incomplete details" 
                % (  self.name, "insert_catalog", ) 
            );
            
            return False;   
                
        
    #///////////////////////////////////////
    
    
    @safety_mysql                    
    def fetch_install_by_state( self, state ):
            
        if state :
            query = """
                SELECT * FROM %s.%s WHERE state = %s 
            """  % ( self.DB_NAME, self.TBL_DATAWARE_INSTALLS, '%s' ) 
        
            self.cursor.execute( query, ( state, ) )
            row = self.cursor.fetchone()

            if not row is None:
                return row
            else :
                return None
        else :
            return None
        
        
    #///////////////////////////////////////
    
    
    @safety_mysql                    
    def fetch_install( self, user_id, catalog_uri ):
            
        if user_id and catalog_uri:
            query = """
                SELECT * FROM %s.%s t WHERE user_id = %s AND catalog_uri = %s
            """  % ( self.DB_NAME, self.TBL_DATAWARE_INSTALLS, '%s', '%s' ) 
        
            self.cursor.execute( query, ( user_id, catalog_uri ) )
            row = self.cursor.fetchone()

            if not row is None:
                return row
            else :
                return None
        else :
            return None   
        
            
    #///////////////////////////////////////////////
    
    
    @safety_mysql       
    def authenticate( self, install_token ) :
       
        if install_token:
            query = """
                SELECT * FROM %s.%s WHERE install_token = %s  
            """  % ( self.DB_NAME, self.TBL_DATAWARE_INSTALLS, '%s' ) 

            self.cursor.execute( query, ( install_token, ) )
            row = self.cursor.fetchone()
            log.info("returning %s" % row)
            return row
            
        else:    
            return None


    #///////////////////////////////////////////////

             
    def generateAccessToken( self ):
        
        token = base64.b64encode(  
            hashlib.sha256( 
                str( random.getrandbits( 256 ) ) 
            ).digest() 
        )  
            
        #replace plus signs with asterisks. Plus signs are reserved
        #characters in ajax transmissions, so just cause problems
        return token.replace( '+', '*' ) 
        
    
    @safety_mysql                
    def fetch_urls( self) :

        query = """
            SELECT * FROM %s.%s t 
        """  % ( self.DB_NAME, self.TBL_TERM_URLS) 
    
        self.cursor.execute( query )
        row = self.cursor.fetchone()

        if not row is None:
            return row
        else :
            return None