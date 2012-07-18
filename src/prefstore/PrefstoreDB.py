'''    
Created on 12 April 2011
@author: jog
'''

import MySQLdb
import logging
import ConfigParser
from time import * #@UnusedWildImport
import sys
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


class PrefDB( object ):
    ''' classdocs '''
    
    DB_NAME = 'prefstore'
    TBL_TERM_APPEARANCES = 'tblTermAppearances'
    TBL_TERM_DICTIONARY = 'tblTermDictionary'
    TBL_TERM_BLACKLIST = 'tblTermBlacklist'
    TBL_USER_DETAILS = 'tblUserDetails'
    
    VIEW_TERM_SUMMARIES = 'viewTermSummaries'    
    
    CONFIG_FILE = "prefstore.cfg"
    SECTION_NAME = "PrefstoreDB"


    #///////////////////////////////////////

 
    createQueries = [
               
        ( TBL_TERM_DICTIONARY, """
            CREATE TABLE %s.%s (
            term varchar(128) NOT NULL,
            term_id int(10) unsigned NOT NULL AUTO_INCREMENT,
            mtime int(10) unsigned NOT NULL,
            count int(10) unsigned,
            ctime int(10) unsigned,
            PRIMARY KEY (term_id), UNIQUE KEY `UNIQUE` (`term`) )
            ENGINE=InnoDB DEFAULT CHARSET=latin1;
        """  % ( DB_NAME, TBL_TERM_DICTIONARY ) ),
        
        ( TBL_TERM_BLACKLIST, """
            CREATE TABLE %s.%s (
            term varchar(128) NOT NULL,
            term_id int(10) unsigned NOT NULL AUTO_INCREMENT,
            PRIMARY KEY (term_id), UNIQUE KEY `UNIQUE` (`term`) )
            ENGINE=InnoDB DEFAULT CHARSET=latin1;
        """  % ( DB_NAME, TBL_TERM_BLACKLIST ) ),
        
        ( TBL_USER_DETAILS, """
            CREATE TABLE %s.%s (
            user_id varchar(256) NOT NULL,
            user_name varchar(64),
            email varchar(256),
            total_documents int(10) unsigned NOT NULL,
            last_distill int(10) unsigned NOT NULL,
            last_message int(10) unsigned NOT NULL,
            total_term_appearances bigint(20) NOT NULL DEFAULT 0,
            registered int(10) unsigned,        
            PRIMARY KEY (user_id), UNIQUE KEY `UNIQUE` (`user_name`) ) 
            ENGINE=InnoDB DEFAULT CHARSET=latin1;
        """  % ( DB_NAME, TBL_USER_DETAILS ) ),  
        
        ( TBL_TERM_APPEARANCES, """
            CREATE TABLE %s.%s (
            user_id varchar(256) NOT NULL,
            term varchar(128) NOT NULL,
            doc_appearances bigint(20) unsigned NOT NULL,
            total_appearances bigint(20) unsigned NOT NULL,
            last_seen int(10) unsigned NOT NULL,
            PRIMARY KEY (user_id, term),
            FOREIGN KEY (user_id) REFERENCES %s(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (term) REFERENCES %s(term) ON DELETE CASCADE ON UPDATE CASCADE )
            ENGINE=InnoDB DEFAULT CHARSET=latin1;
            
        """  % ( DB_NAME, TBL_TERM_APPEARANCES, TBL_USER_DETAILS, TBL_TERM_DICTIONARY ) ), 
        
        ( VIEW_TERM_SUMMARIES, """
            CREATE VIEW %s.%s AS
            SELECT
              user_id,
              MIN( last_seen ) min_last_seen,
              MAX( last_seen ) max_last_seen,
              MAX( total_appearances ) max_apperances,
              MIN( total_appearances ) min_apperances,
              MAX( doc_appearances ) max_documents,
              MIN( doc_appearances ) min_documents,
              COUNT( term ) unique_terms,
              SUM( total_appearances ) total_term_appearances,
              SUM( doc_appearances ) total_documents              
            FROM prefstore.tblTermAppearances
            GROUP BY user_id
        """  % ( DB_NAME, VIEW_TERM_SUMMARIES ) ),          
    ] 
    
    
    #///////////////////////////////////////
    
    
    def __init__( self, name = "PrefstoreDB" ):
            
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
        
        
    #///////////////////////////////////////
    
    
    @safety_mysql
    def create_table( self, tableName ):
        
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
                ( user_id, user_name, email, total_documents, last_distill, 
                last_message, total_term_appearances, registered ) 
                VALUES ( %s, null, null, 0, 0, 0, 0, null )
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
            
            
    #///////////////////////////////////////


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
            
            
    #///////////////////////////////////////


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
    def fetch_user_summary( self, user_id ) :

        if user_id :
            query = """
                SELECT * FROM %s.%s t where user_id = %s 
            """  % ( self.DB_NAME, self.VIEW_TERM_SUMMARIES, '%s' ) 
        
            self.cursor.execute( query, ( user_id, ) )
            row = self.cursor.fetchone()
            if not row is None:
                return row
            else :
                return None
        else :
            return None     
            
            
                    
    #///////////////////////////////////////
                    
                    
    @safety_mysql                                    
    def incrementUserInfo(self, 
            user_id = None, 
            total_term_appearances = 1, 
            mtime = None ) :

        if user_id and mtime:
  
            query = """
                UPDATE %s.%s 
                SET total_documents = total_documents + 1, 
                    total_term_appearances = total_term_appearances + %s,
                    last_distill = %s,
                    last_message = %s
                WHERE user_id = %s
            """  % ( self.DB_NAME, self.TBL_USER_DETAILS, '%s', '%s', '%s', '%s' )
           
            update = self.cursor.execute( 
                query, ( total_term_appearances, mtime, int( time() ), user_id ) )

            if update > 0 :
                log.debug( 
                    "%s: Updated user info for %s" 
                    % ( self.name, user_id )  
                )
                return True
            else:
                log.warning( 
                    "%s: trying to update an unknown user" 
                    % self.name 
                )
                return False
        else :
            log.warning( 
                "%s: attempting to update User with incomplete data" 
                % self.name 
            )
            return False
        
        
        
    #//////////////////////////////////////////////////////////
    # WEB UPDATER CALLS
    #//////////////////////////////////////////////////////////               
        

    @safety_mysql                
    def getMissingCounts( self ):
        
        query = """
            SELECT term FROM %s.%s where count IS NULL 
        """  % ( self.DB_NAME, self.TBL_TERM_DICTIONARY ) 
        self.cursor.execute( query  )
        
        resultSet = [ row[ 'term' ] for row in self.cursor.fetchall() ]
        return resultSet
    
    
    #///////////////////////////////////////
                   

    @safety_mysql                        
    def updateTermCount( self, term, count ):
        
        if term: 
            query = "UPDATE %s.%s SET count = %s, ctime = %s WHERE term = %s" % \
                ( self.DB_NAME, self.TBL_TERM_DICTIONARY, '%s', '%s', '%s' ) 
            
            log.debug( 
                "%s %s: Updating dictionary term '%s' with web count '%d'" 
                % ( self.name, "updateTermCount", term, count ) 
            );
            
            self.cursor.execute( query, ( count, time(), term )  )
            
            return True
        else:
            return False
   
    
    #///////////////////////////////////////   
    
    
    @safety_mysql                
    def insertDictionaryTerm( self, term = None ):

        try:     
            if term:
                log.debug( 
                    "%s %s: Creating new dictionary term '%s' " 
                    % ( self.name, "insertDictionaryTerm", term ) 
                );
               
                query = """
                    INSERT INTO %s.%s ( term, mtime, count, ctime ) 
                    VALUES ( %s, %s, null, null )
                """  % ( self.DB_NAME, self.TBL_TERM_DICTIONARY, '%s', '%s' ) 
               
                self.cursor.execute( query, ( term, int( time() ) ) )
                
            else:
                log.warning(
                    "%s %s: Trying to create new dictionary term '%s' : ignoring..." 
                    % ( self.name, "insertDictionaryTerm", term ) 
                );
                     
        except:
            log.error( "error %s" % sys.exc_info()[0] )


    #///////////////////////////////////////   
    
    
    @safety_mysql                
    def insertDictionaryTerms( self, fv = None ):

        if not ( fv and len( fv ) > 0 ):
            log.warning(
                "%s %s: Trying to create empty empty list of dictionary terms : ignoring..." 
                % ( self.name, "insertDictionaryTerm" ) 
            );   
            return None
             
        try:     
            query = """
                INSERT IGNORE INTO %s.%s ( term, mtime, count, ctime ) 
                values ( %s, %d, null, null )
            """ % ( self.DB_NAME, self.TBL_TERM_DICTIONARY, "%s", int( time() ) )

            return self.cursor.executemany( query,  [ ( t, ) for t in fv.keys() ] )
            
        except:
            log.error( "error %s" % sys.exc_info()[0] )
            return None 

             
    #///////////////////////////////////////
            
            
    @safety_mysql                    
    def deleteDictionaryTerm( self, term = None ):
        
        log.debug( 
            "%s %s: Deleting term '%s' " 
            % ( self.name, "deleteDictionaryTerm", term ) 
        );
        
        query = "DELETE FROM %s.%s WHERE term = %s"  % ( self.DB_NAME, self.TBL_TERM_DICTIONARY, '%s' ) 
        self.cursor.execute( query, ( term ) )

                  
    #///////////////////////////////////////
              
                
    @safety_mysql                
    def updateTermAppearance( self, user_id = None, term = None, freq = 0 ):
        
        try:
            if term and user_id:
                
                log.debug( 
                    "%s %s: Updating term '%s' for user '%s': +%d appearances" 
                    % ( self.name, "updateTermAppearance", term, user_id, freq ) 
                );
                
                query = """
                    INSERT INTO %s.%s ( user_id, term, doc_appearances, total_appearances, last_seen ) 
                    VALUES ( %s, %s, %s, %s, %s )
                    ON DUPLICATE KEY UPDATE 
                    doc_appearances = doc_appearances + 1, 
                    total_appearances = total_appearances + %s,
                    last_seen = %s
                """  % ( self.DB_NAME, self.TBL_TERM_APPEARANCES, '%s', '%s', '%s', '%s', '%s', '%s', '%s' )
                
                self.cursor.execute( query, ( user_id, term, 1, freq, int( time() ), freq, int( time() ) ) )
                  
            else:
                log.warning( 
                    "%s %s: Updating term '%s' for user '%s': ignoring..." 
                    % ( self.name, "updateTermAppearance" , term, user_id, freq ) 
                );
            
        except Exception, e:
            log.error(
                "%s %s: error %s" 
                % ( self.name, "updateTermAppearance" , sys.exc_info()[0] ) 
            )
            

    #///////////////////////////////////////
       
  
    @safety_mysql                
    def updateTermAppearances( self, user_id = None, fv = None ) :
        """ This method is quite convoluted, due to trying to optimize the
        time it takes to do batch updates (which is extremely slow on mysql).
        Batch Inserts are quick, so that is harnessed here. In fact you can
        end up with is the ridiculous situation where it is better to send a 
        "batch insert into on duplicate key update" than a batch "update"...
        even when you know that every single change is an update. There is 
        also a supreme gotcha - unless the "VALUES" part of the insert 
        statement is in lowercase mysqldb will send the batch insert as 
        individual insert statements, annhialating efficiency gains. Absurd.
        """
        if not ( user_id and fv ):
            log.warning(
                "%s %s: Invariance failure in updateTermAppearances: ignoring..." 
                % ( self.name, "insertDictionaryTerm" ) )
            return
        
        try:    
            #convert the results into a list of tuples ready for processing
            insert_tuples = [ ( user_id, k, 1, v, int( time() ) ) for k,v in fv.items() ] 

            #insert the new tuples (updating if they alredy exist)
            query = """
                INSERT INTO %s.%s ( user_id, term, doc_appearances, total_appearances, last_seen ) 
                values ( %s, %s, %s, %s, %s )
                ON DUPLICATE KEY UPDATE
                doc_appearances = doc_appearances + VALUES( doc_appearances ),
                total_appearances = total_appearances + VALUES( total_appearances ),
                last_seen = VALUES( last_seen )
            """  % ( self.DB_NAME, self.TBL_TERM_APPEARANCES, '%s', '%s', '%s', '%s', '%s' ) 
            
            self.cursor.executemany( query, insert_tuples )
            
        except:
            log.error( "error %s" % sys.exc_info()[0] ) 
            
            
                    
    #///////////////////////////////////////             
              
              
    @safety_mysql                
    def getTermAppearance( self, user_id, term ):
        
        if user_id and term :
            query = """
                SELECT * FROM %s.%s t where user_id = %s and term = %s 
            """  % ( self.DB_NAME, self.TBL_TERM_APPEARANCES, '%s', '%s' ) 
        
            self.cursor.execute( query, ( user_id, term ) )
            row = self.cursor.fetchone()
            if not row is None:
                return row
            else :
                return None
    
            
    #///////////////////////////////////////          
    
        
    @safety_mysql                
    def getTermCount( self, term = None ):
        
        if term:
            
            query = "SELECT count FROM %s.%s WHERE term = %s"  \
                % ( self.DB_NAME, self.TBL_TERM_DICTIONARY, '%s' ) 

            self.cursor.execute( query, ( term, ) )
 
            row = self.cursor.fetchone()
            if row == None : 
                return None
            else :
                return row[ 'count' ]
        else:
            return None
          
    
    #///////////////////////////////////////          


    @safety_mysql                
    def getTermCountList( self, fv = None ):
         
        if fv:
            #convert terms into an appropriate escape string
            formatStrings = ','.join( ['%s'] * len( fv ) )
            query = "SELECT term, count FROM %s.%s where term IN (%s)" % \
                (  self.DB_NAME, self.TBL_TERM_DICTIONARY, formatStrings )
                
            #get the web counts from the db for those terms
            self.cursor.execute( query, tuple( fv ) )
            
            #convert those results into a dictionary and return it
            return dict( [ ( row.get( 'term' ), row.get( 'count' ) ) for row in self.cursor.fetchall() ] )
        else:
            return None          
    
    
    #///////////////////////////////////////          


    @safety_mysql                
    def matchExistingTerms( self, terms = None ):
        
        """
            Takes an array of terms and removes those that have not
            already been seen before, and are hence recorded in the db. 
            The result is returned as a list - which could well be empty.
        """
        if terms:
            #convert terms into an appropriate escape string
            formatStrings = ','.join( ['%s'] * len( terms ) )
            query = "SELECT term FROM %s.%s where term IN (%s)" % \
                (  self.DB_NAME, self.TBL_TERM_DICTIONARY, formatStrings )
                
            #get the web counts from the db for those terms
            self.cursor.execute( query, tuple( terms ) )
            
            #convert those results into a dictionary and return it
            return [ row.get( 'term' ) for row in self.cursor.fetchall() ] 
        else:
            return []
        
            
    #///////////////////////////////////////          


    @safety_mysql                
    def removeBlackListedTerms( self, fv = None ):
        """
            Takes a dict of terms and remove those in it that are 
            recorded in the databases blacklisted words. 
        """
       
        if fv:
            
            terms = [ t for t in fv ] 
            #convert terms into an appropriate escape string
            formatStrings = ','.join( ['%s'] * len( terms ) )
            
            query = "SELECT term FROM %s.%s where term IN (%s)" % \
                ( self.DB_NAME, self.TBL_TERM_BLACKLIST, formatStrings )
                
            #get the web counts from the db for those terms
            self.cursor.execute( query, tuple( terms ) )
             
            #convert those results into a dictionary and return it
            for row in self.cursor.fetchall():
                del fv[ row.get( 'term' ) ]
           
            log.debug( 
                "%s %s: Removing %d terms from distillation" 
                % ( self.name, "removeBlackListed", len( self.cursor.fetchall() ) ) 
            );
        
        
    #///////////////////////////////////////
       
       
    @safety_mysql                       
    def blacklistTerm( self, term ):   
                
        log.info( "Blacklisting term '%s' " % ( term ) );
        self.deleteDictionaryTerm( term )
        
        try:     
            if term:
                log.debug( 
                    "%s %s: Blocking new  term '%s' " 
                    % ( self.name, "blacklistTerm", term ) 
                );
                
                query = """
                    INSERT INTO %s.%s ( term ) 
                    VALUES ( %s )
                """  % ( self.DB_NAME, self.TBL_TERM_BLACKLIST, '%s' ) 
                
                self.cursor.execute( query, ( term ) )
                
            else:
                log.debug( 
                    "%s %s: Blocking new term '%s' : ignoring..." 
                    % ( self.name, "blacklistTerm", term ) 
                )
                     
        except:
            log.error( 
                "%s %s: Error %s" 
                % ( self.name, "blacklistTerm",sys.exc_info()[0] ) 
            )


    #///////////////////////////////////////////////


    @safety_mysql   
    def update_tfidf( self ):
        """
            This is currently just a debugging test function
        """
        
        f = open( 'doc_similarity.py', 'r' )
        code = f.read()
        
        query = """
            UPDATE %s.%s SET query=%s WHERE access_token=4444
        """  % ( self.DB_NAME, self.TBL_DATAWARE_PROCESSORS, '%s' ) 
        self.cursor.execute( query, code )
        self.commit()
        

    #///////////////////////////////////////


    @safety_mysql                
    def fetch_terms( self, 
        user_id, 
        order_by='total appearances',
        direction='DESC',
        LIMIT=1000,
        MIN_WEB_PREVALENCE=50000,
        TOTAL_WEB_DOCUMENTS=25000000000
    ) :
        FIELDS = { 
            "alphabetical order":"term", 
            "total appearances":"total_appearances", 
            "doc appearances":"doc_appearances",
            "frequency":"total_appearances", 
            "web importance":"count",
            "relevance":"weight",
            "last seen":"last_seen",
        }
        
        if user_id and order_by in FIELDS.keys():

            query = """
                SELECT 
                    t.*, 
                    d.count,
                    ( t.total_appearances  / (d.count / %d ) ) weight  
                FROM %s.%s t, %s.%s d 
                WHERE user_id = %s
                AND t.term = d.term
                AND d.count > %d
                ORDER BY %s %s
                LIMIT %s
            """  % ( 
                TOTAL_WEB_DOCUMENTS,
                self.DB_NAME, self.TBL_TERM_APPEARANCES, 
                self.DB_NAME, self.TBL_TERM_DICTIONARY,
                '%s', 
                MIN_WEB_PREVALENCE, 
                FIELDS[ order_by ], 
                direction, 
                '%s' ) 
            
            self.cursor.execute( query, ( user_id, LIMIT ) )
            results = self.cursor.fetchall()
            
            if not results is None:
                return results
            else :
                return {}
        else :
            return {}     
        
        
    #///////////////////////////////////////


    @safety_mysql                
    def search_terms( self, 
        user_id, 
        search_term,
        match_type="exact" ) :
        
        MATCH_TYPES = {
            "exact":"t.term = '%s'" % ( search_term, ),
            "starts":"t.term LIKE '%s'" % (  search_term + "%%", ),
            "contains":"t.term LIKE '%s'" % ( "%%" + search_term + "%%", ), 
            "ends":"t.term LIKE '%s'" % ( "%%" + search_term, ),             
        }
        
        LIMIT = 500
        
        if user_id and search_term and match_type in MATCH_TYPES.keys():
            
            query = """
                SELECT t.*, d.count FROM %s.%s t, %s.%s d 
                WHERE user_id = %s
                AND t.term = d.term
                AND %s
                ORDER BY t.term
                LIMIT %s
            """  % ( 
                self.DB_NAME, self.TBL_TERM_APPEARANCES, 
                self.DB_NAME, self.TBL_TERM_DICTIONARY,
                '%s', MATCH_TYPES[ match_type ], LIMIT ) 

            self.cursor.execute( query, ( user_id ) )
            results = self.cursor.fetchall()
            
            if not results is None:
                return results
            else :
                return {}
        else :
            return {}    