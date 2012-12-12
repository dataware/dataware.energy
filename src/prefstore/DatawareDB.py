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
from time import * 

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

    
class DataDB(object):
    ''' classdocs '''
         
    #///////////////////////////////////////
    
    
    def __init__( self, configfile, section, name="DatawareDB"):
            
        #MysqlDb is not thread safe, so program may run more
        #than one connection. As such naming them is useful.
        self.name = name
        self.CONFIG_FILE = configfile
        self.SECTION_NAME = section
        
        Config = ConfigParser.ConfigParser()
        Config.read( self.CONFIG_FILE )
        log.info("%s", self.SECTION_NAME);
        
        
        self.hostname = Config.get( self.SECTION_NAME, "hostname" )
        self.username =  Config.get( self.SECTION_NAME, "username" )
        self.password =  Config.get( self.SECTION_NAME, "password" )
        self.DB_NAME = Config.get( self.SECTION_NAME, "dbname" )
        
        log.info("%s %s %s" % (self.hostname, self.username, self.DB_NAME));
        
        self.connected = False;
       
    
        self.TBL_DATAWARE_PROCESSORS = 'tblDatawareProcessors'
        self.TBL_DATAWARE_CATALOGS = 'tblDatawareCatalogs'
        self.TBL_DATAWARE_INSTALLS = 'tblDatawareInstalls'
        self.TBL_DATAWARE_EXECUTIONS = 'tblDatawareExecutions'
        self.TBL_USER_DETAILS = 'tblUserDetails'
       
        
        #///////////////////////////////////////
    
      
        self.createQueries = [ 
                   
            ( self.TBL_DATAWARE_PROCESSORS, """
                CREATE TABLE %s.%s (
                    access_token varchar(256) NOT NULL,
                    client_id varchar(256) NOT NULL,
                    resource_name varchar(256) NOT NULL,
                    user_id varchar(256) NOT NULL,
                    expiry_time bigint(20) unsigned NOT NULL,
                    query text NOT NULL,
                    checksum varchar(256) NOT NULL,
                    PRIMARY KEY (access_token),
                    UNIQUE KEY (client_id,user_id,resource_name,checksum)
                ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
            """  % ( self.DB_NAME, self.TBL_DATAWARE_PROCESSORS ) ),
            
            ( self.TBL_USER_DETAILS, """
                CREATE TABLE %s.%s (
                user_id varchar(256) NOT NULL,
                user_name varchar(64),
                email varchar(256),
                registered int(10) unsigned,        
                PRIMARY KEY (user_id), UNIQUE KEY `UNIQUE` (`user_name`)
                ) 
                DEFAULT CHARSET=latin1;
            """  % ( self.DB_NAME, self.TBL_USER_DETAILS ) ),  
            
            ( self.TBL_DATAWARE_CATALOGS, """ 
                CREATE TABLE %s.%s (
                    catalog_uri varchar(256) NOT NULL,                
                    resource_id varchar(256) NOT NULL,
                    resource_name varchar(256) NOT NULL,
                    registered int(10) unsigned DEFAULT NULL,
                    PRIMARY KEY (catalog_uri, resource_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
            """  % (self.DB_NAME, self.TBL_DATAWARE_CATALOGS ) ),  
            
            ( self.TBL_DATAWARE_INSTALLS, """ 
                CREATE TABLE %s.%s (
                    user_id varchar(256) NOT NULL,
                    catalog_uri varchar(256) NOT NULL,   
                    resource_name varchar(256) NOT NULL,             
                    install_token varchar(256),
                    state varchar(256) NOT NULL,
                    registered int(10) unsigned DEFAULT NULL,
                    PRIMARY KEY (user_id, resource_name),
                    FOREIGN KEY (catalog_uri) REFERENCES %s(catalog_uri) 
                    ON DELETE CASCADE ON UPDATE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
            """  % ( self.DB_NAME, self.TBL_DATAWARE_INSTALLS, self.TBL_DATAWARE_CATALOGS ) ),   
             
            ( self.TBL_DATAWARE_EXECUTIONS, """ 
                CREATE TABLE %s.%s (
                    execution_id int(11) AUTO_INCREMENT,
                    processor_id varchar(256) NOT NULL,                
                    parameters varchar(256) NOT NULL,
                    result text,
                    executed int(11) unsigned NOT NULL,
                    client_view_url varchar(256),
                    PRIMARY KEY (execution_id),
                    FOREIGN KEY (processor_id) REFERENCES %s(access_token) 
                    ON DELETE CASCADE ON UPDATE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
            """  % ( self.DB_NAME, self.TBL_DATAWARE_EXECUTIONS, self.TBL_DATAWARE_PROCESSORS ) ),
        ] 
        
    #///////////////////////////////////////
    

    def connect( self ):
        
        log.info( "%s: connecting to mysql database..." % self.name )

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
        log.info( "%s: Database reconnection process activated..." % self.name );
        self.close()
        self.connect()
        

    #///////////////////////////////////////
          
          
    @safety_mysql                
    def commit( self ) : 
        self.conn.commit();
        
        
    #///////////////////////////////////////
        

    def close( self ) :   
        if self.conn.open:
            log.info( "%s: disconnecting from mysql database..." % self.name );
            self.cursor.close();
            self.conn.close()
                     
   
    #///////////////////////////////////////
    
    
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
        
        
        
    #///////////////////////////////////////
    
    
    @safety_mysql                  
    def createTable( self, tableName ):
        
        log.warning( 
            "%s: missing system table detected: '%s'" 
            % ( self.name, tableName ) 
        );
        
        if tableName in self.createQueries :
            
            log.info( 
                "%s: --- creating system table '%s' " 
                % ( self.name, tableName )
            );  
              
            self.cursor.execute( self.createQueries[ tableName ] )
                              
    #////////////////////////////////////////////////////////////////////////////////////////////
    #///// this also needs the tpc token so can view results on clients site? //////////////////#
   
                                              
    @safety_mysql   
    def insert_execution(self, processor_id, parameters, result, executed, view_url):
       
        query = """
             INSERT INTO %s.%s (processor_id, parameters, result, executed, client_view_url) VALUES ( %s, %s, %s, %s, %s)
        """  % ( self.DB_NAME, self.TBL_DATAWARE_EXECUTIONS, '%s', '%s', '%s', '%s', '%s') 
        
        
        self.cursor.execute( 
            query, (  
                processor_id, 
                parameters,
                result,
                executed,
                view_url
            ) 
        )
        self.commit()
        return self.cursor.lastrowid
        
    @safety_mysql 
    def fetch_executions(self):
    
        query = """
            SELECT e.*, p.query, p.resource_name FROM %s.%s e, %s.%s p WHERE 
            p.access_token = e.processor_id;
         """ %  (self.DB_NAME, self.TBL_DATAWARE_EXECUTIONS, self.DB_NAME, self.TBL_DATAWARE_PROCESSORS) 
            
        self.cursor.execute( query )
        results = self.cursor.fetchall()
        return results
    
    @safety_mysql 
    def fetch_execution_by_id(self, id):
        
        query = """
            SELECT e.*, p.query, p.resource_name FROM %s.%s e, %s.%s p WHERE 
            p.access_token = e.processor_id AND e.execution_id = %d;
         """ %  (self.DB_NAME, self.TBL_DATAWARE_EXECUTIONS, self.DB_NAME, self.TBL_DATAWARE_PROCESSORS, id) 
            
        self.cursor.execute( query )
        results = self.cursor.fetchone()
        return results
    
    #////////////////////////////////////////////////////////////////////////////////////////////
    @safety_mysql   
    def insert_processor( self, access_token, client_id, resource_name, user_name, expiry_time, query_code ):
       
        #create a SHA checksum for the file
        checksum = hashlib.sha1( query_code ).hexdigest()
        
        query = """
             INSERT INTO %s.%s VALUES ( %s, %s, %s, %s, %s, %s, %s )
        """  % ( self.DB_NAME, self.TBL_DATAWARE_PROCESSORS, '%s', '%s', '%s', '%s', '%s', '%s', '%s' ) 
        
        self.cursor.execute( 
            query, ( 
                access_token, 
                client_id, 
                resource_name,
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
    def insert_catalog( self, catalog_uri, resource_id, resource_name):
            
        if ( catalog_uri ):
            
            log.info( 
                "%s %s: Inserting catalog '%s' in database with resource_id '%s' and name '%s'" 
                % ( self.name, "insert_catalog", catalog_uri, resource_id, resource_name ) 
            );
            
            query = """
                  INSERT INTO %s.%s ( catalog_uri, resource_id, resource_name, registered ) 
                  VALUES ( %s, %s, %s, %s )
              """  % ( self.DB_NAME, self.TBL_DATAWARE_CATALOGS, '%s', '%s', '%s', '%s', )
            
            state = self.generateAccessToken()
            self.cursor.execute( query, ( catalog_uri, resource_id, resource_name, time(), ) )
                
            return state;
        
        else:
            log.warning( 
                "%s %s: Catalog insert requested with incomplete details" 
                % (  self.name, "insert_catalog", ) 
            );
            return None;    
        
        
    #///////////////////////////////////////
    
    
    @safety_mysql                    
    def fetch_catalog( self, catalog_uri, resource_name ):
            
        if catalog_uri :
            query = """
                SELECT * FROM %s.%s t where catalog_uri = %s  AND resource_name = %s
            """  % ( self.DB_NAME, self.TBL_DATAWARE_CATALOGS, '%s', '%s' ) 
        
            self.cursor.execute( query, ( catalog_uri, resource_name) )
            row = self.cursor.fetchone()

            if not row is None:
                return row
            else :
                return None
        else :
            return None   
            
        
                
    #///////////////////////////////////////
    
    
    @safety_mysql                    
    def insert_install( self, user_id, catalog_uri, resource_name ):
            
        if ( user_id and catalog_uri ):
            
            log.info( 
                "%s %s: Initiating user '%s' installation to '%s' resource '%s' in database" 
                % ( self.name, "insert_install", user_id, catalog_uri, resource_name ) 
            );
            
            
            query = """
                  INSERT INTO %s.%s 
                  ( user_id, catalog_uri, resource_name, install_token, state, registered ) 
                  VALUES ( %s, %s, %s, null, %s, %s )
              """  % ( self.DB_NAME, self.TBL_DATAWARE_INSTALLS, '%s', '%s', '%s', '%s', '%s' )
            
            state = self.generateAccessToken()
            self.cursor.execute( query, 
                ( user_id, catalog_uri, resource_name, state, time(), ) )
                
            return state;
        
        else:
            log.warning( 
                "%s %s: Installation insert requested with incomplete details" 
                % (  self.name, "insert_catalog", ) 
            );
            return None;    
        

    #///////////////////////////////////////
    
    
    @safety_mysql                    
    def update_install( self, user_id, catalog_uri, install_token, state ):
        print "in updat einstall"
        
        if ( user_id and catalog_uri and install_token and state ):
            
            query = """
                  UPDATE %s.%s SET install_token=%s, registered=%s
                  WHERE user_id=%s AND catalog_uri=%s AND state=%s
              """  % ( self.DB_NAME, self.TBL_DATAWARE_INSTALLS, '%s', '%s', '%s', '%s', '%s')
            
            print "doing query"
               
            update = self.cursor.execute( query, 
                ( install_token, time(), user_id, catalog_uri, state, ) )

            if update > 0 :
                log.debug( 
                    "%s %s: Updating installation for user '%s' to catalog '%s', state '%s'" 
                    % ( self.name, "update_install", user_id, catalog_uri, state,) 
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
    def fetch_install( self, user_id, catalog_uri, resource_name ):
            
        if user_id and catalog_uri:
            query = """
                SELECT * FROM %s.%s t WHERE user_id = %s AND catalog_uri = %s AND resource_name = %s
            """  % ( self.DB_NAME, self.TBL_DATAWARE_INSTALLS, '%s', '%s', '%s' ) 
        
            self.cursor.execute( query, ( user_id, catalog_uri, resource_name ) )
            row = self.cursor.fetchone()

            if not row is None:
                return row
            else :
                return None
        else :
            return None   
    
    #///////////////////////////////////////////////
    
    @safety_mysql                    
    def fetch_catalog_installs(self, user_id):
        if user_id:   
            query = """
                SELECT * FROM %s.%s t WHERE user_id = %s
            """  % ( self.DB_NAME, self.TBL_DATAWARE_INSTALLS, '%s') 
        
            self.cursor.execute( query, ( user_id ) )
            rows = self.cursor.fetchall()
            if rows:
                return [dict['catalog_uri'] for dict in rows] 
            
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
            return self.cursor.fetchone()
            
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
    def fetch_user_by_id( self, user_id ) :

        if user_id :
            query = """
                SELECT * FROM %s.%s t where user_id = %s 
            """  % ( self.DB_NAME, self.TBL_USER_DETAILS, '%s' ) 
        
            self.cursor.execute( query, ( user_id, ) )
            row = self.cursor.fetchone()

            if not row is None:
                return row
            else :
                return None
        else :
            return None   
        
        
    @safety_mysql                
    def fetch_user_by_name( self, user_name ) :

        if user_name :
            query = """
                SELECT * FROM %s.%s t where user_name = %s 
            """  % ( self.DB_NAME, self.TBL_USER_DETAILS, '%s' ) 
        
            self.cursor.execute( query, ( user_name, ) )
            row = self.cursor.fetchone()

            if not row is None:
                return row
            else :
                return None
        else :
            return None     
            
    @safety_mysql                
    def fetch_user_by_email( self, email ) :

        if email :
            query = """
                SELECT * FROM %s.%s t where email = %s 
            """  % ( self.DB_NAME, self.TBL_USER_DETAILS, '%s' ) 
        
            self.cursor.execute( query, ( email, ) )
            row = self.cursor.fetchone()
            if not row is None:
                return row
            else :
                return None    
        else :
            return None     
        
        
    #///////////////////////////////////////
    
    @safety_mysql                
    def insert_user( self, user_id ):
        
        if user_id:
            
            log.info( 
                "%s %s: Adding user '%s' into database" 
                % ( self.name, "insert_user", user_id ) 
            );
            
            query = """
                INSERT INTO %s.%s 
                ( user_id, user_name, email, registered ) 
                VALUES ( %s, null, null, null )
            """  % ( self.DB_NAME, self.TBL_USER_DETAILS, '%s' ) 

            self.cursor.execute( query, ( user_id ) )
            return True;
        
        else:
            log.warning( 
                "%s %s: Was asked to add 'null' user to database" 
                % (  self.name, "insert_user", ) 
            );
            return False;
        
        
    #///////////////////////////////////////
    
    
    @safety_mysql                    
    def insert_registration( self, user_id, user_name, email ):
            
        if ( user_id and user_name and email ):
            
            log.info( 
                "%s %s: Updating user '%s' registration in database" 
                % ( self.name, "insert_registration", user_id ) 
            );
            
            query = """
                UPDATE %s.%s 
                SET user_name = %s, email = %s, registered= %s 
                WHERE user_id = %s
            """  % ( self.DB_NAME, self.TBL_USER_DETAILS, '%s', '%s', '%s', '%s' ) 
            log.info("query is %s %s %s %s %s" % (query, user_name, email, time(), user_id))
            self.cursor.execute( query, ( user_name, email, time(), user_id ) )
            return True;
        
        else:
            log.warning( 
                "%s %s: Registration requested with incomplete details" 
                % (  self.name, "insert_registration", ) 
            );
            return False;    

            
    #///////////////////////////////////////
    
    @safety_mysql                    
    def purgedata( self ):
        try:
            self.cursor.execute("DELETE FROM %s.%s" % ( self.DB_NAME, self.TBL_USER_DETAILS))
            self.cursor.execute("DELETE FROM %s.%s" % ( self.DB_NAME, self.TBL_DATAWARE_PROCESSORS))
            self.cursor.execute("DELETE FROM %s.%s" % ( self.DB_NAME, self.TBL_DATAWARE_CATALOGS))
            self.cursor.execute("DELETE FROM %s.%s" % ( self.DB_NAME, self.TBL_DATAWARE_INSTALLS))
            self.commit()
        except Exception, e:
            print e