"""
Created on 12 April 2011
@author: jog
"""

from new import * #@UnusedWildImport
import json
import base64
import random
import __builtin__
import sys
import MySQLdb
import hashlib
import logging
import time
import SqlParser

#setup logger for this module
log = logging.getLogger( "console_log" )

    
#///////////////////////////////////////////////


class ProcessingModule( object ) :

    #set of commands that are permissable within the sandbox's e
    #excecution environment (list borrowed from the "CAPE" sandbox )
    ALLOWED_BUILTINS = [
        'abs', 'bool', 'callable', 'chr', 'cmp', 'coerce', 'complex', 
        'dict', 'divmod', 'enumerate', 'filter', 'float', 'getattr', 
        'hasattr', 'hash', 'hex', 'int', 'intern', 'isinstance',
        'issubclass', 'iter', 'len', 'list', 'locals', 'long', 'map',
        'max', 'min', 'oct', 'ord', 'pow', 'range', 'reduce', 'repr',
        'round', 'slice', 'str', 'sum', 'tuple', 'type', 'unichr',
        'unicode', 'xrange', 'zip'
    ]
    
    #///////////////////////////////////////////////
    
    
    def __init__( self, datadb, resourcedb, um):
        self.db = datadb;       
        self.resourcedb = resourcedb;
        self.sandbox_builtins = __builtin__.__dict__.copy()
        self.um = um;
        
        for command in __builtin__.__dict__ :
            if command not in self.ALLOWED_BUILTINS :
                del self.sandbox_builtins[ command ]
        
         
    #///////////////////////////////////////////////


    def format_register_success( self, access_token = None ):
        
        if ( access_token ) :
            json_response = { 'success': True, 'access_token': access_token }
        else : 
            json_response = { 'success': True }
        
        return json.dumps( json_response );
           
         
    #///////////////////////////////////////////////


    def format_register_failure( self, error, msg ):
        
        json_response = { 
            'success': False,
            'error':error,
            'error_description':msg
        } 
        
        return json.dumps( json_response );
          
        
    #///////////////////////////////////////////////
    
    
    def format_process_success( self, result = None):
        
        if ( result ) :
            json_response = { 'success': True, 'return': result}
        else : 
            json_response = { 'success': True }
        
        return json.dumps( json_response );
    
              
    #///////////////////////////////////////////////


    def format_process_failure( self, error, msg ):
      
        json_response = { 
            'success': False,
            'error':error,
            'error_description':msg
        } 
        
        return json.dumps( json_response );
          

    def test_processor( self, user, query, jsonParams ):
    
        try:
            parameters = json.loads( jsonParams ) if jsonParams else {}
        except:
            return self.format_process_failure(
                "access_exception",
                "incorrectly formatted JSON parameters"
            ) 
        try:
            sandbox = self.setup_sandbox( user, query )

        #TODO: Should probably log exceptions like these                           
        except Exception, e:
            return self.format_process_failure(
                "processing_exception",
                "Compile-time failure - %s:%s" % 
                ( type( e ).__name__,  e )
            ) 

        #finally invoke the function
        try:
            result = sandbox.run( parameters )
            return self.format_process_success( result )
        
        #and catch any problems that occur in processing
        except:
           
            return self.format_process_failure(
                "processing_exception",
                "Run-time failure - %s " % str( sys.exc_info() )
            ) 

   
    #run by a user to test output of a proposed query (submitted by a third-party client)
        
    def invoke_test_processor_sql(self, query):
        
        try:
        
            result = json.dumps(self.resourcedb.execute_query(query))        
            
            return self.format_process_success(result)
          
        except:
           
            return self.format_process_failure(
                "processing_exception",
                "Run-time failure"
            )     
   
    def invoke_processor_sql(self, processor_token, jsonParams, view_url):
        print "invoking processor in pm"
        
        if processor_token is None :
            
            return self.format_process_failure(
                "access_exception",
                "Access token has not been supplied"
            ) 

        try:
        
            parameters = json.loads( jsonParams ) if jsonParams else {}
        
        except:
            return self.format_process_failure(
                "access_exception",
                "incorrectly formatted JSON parameters"
            ) 
    
       
        try:
            
            request = self.db.fetch_processor( processor_token )
            print "got request"
            print request
            
            if request is None:
                return self.format_process_failure(
                    "access_exception",
                    "Invalid access token"
                )
             
            #obtain relevent info from the request object    
            user = request[ "user_id" ]
            query = request[ "query" ]
            processor_id = request["access_token"]
            resource_name = request["resource_name"]
            
        except:
            return self.format_process_failure(
                "access_exception",
                "Database problems are currently being experienced"
            ) 

        try:
            if self._check_constraints(resource_name, query):
            
                execution_time = time.time()
                result = json.dumps(self.resourcedb.execute_query(query))
               
                
                try:
                  
                    execution_id = self.db.insert_execution(processor_id=processor_id,
                                             parameters=jsonParams, 
                                             result=result, 
                                             executed=execution_time,
                                             view_url=view_url)
                                    
                    execution = self.db.fetch_execution_by_id(execution_id)
                                           
                    self.um.trigger({    
                                    "type": "execution",
                                    "user":  user, 
                                    "message": "a new execution has been undertaken!",
                                    "data": json.dumps(execution)                       
                                    })
                            
                except:
                    log.error("failed to store the execution details : processor_id %s parameters: %s " % 
                              (processor_id, jsonParams))
                    
                    return self.format_process_failure(
                        "processing_exception",
                        "failed to store the execution details :"
                     )     
                
                
                return self.format_process_success(result)
            
            else:
                 return self.format_process_failure(
                    "processing_exception",
                    "your query violates constraints"
                )     
   
        except:
           
            return self.format_process_failure(
                "processing_exception",
                "Run-time failure"
            )     
   
    
    #///////////////////////////////////////////////
     
    def invoke_processor( self, processor_token, jsonParams):
        
        if processor_token is None :
            return self.format_process_failure(
                "access_exception",
                "Access token has not been supplied"
            ) 

        try:
            parameters = json.loads( jsonParams ) if jsonParams else {}
        except:
            return self.format_process_failure(
                "access_exception",
                "incorrectly formatted JSON parameters"
            ) 
    
       
        try:
            request = self.db.fetch_processor( processor_token )
            if request is None:
                return self.format_process_failure(
                    "access_exception",
                    "Invalid access token"
                )
             
            #obtain relevent info from the request object    
            user = request[ "user_id" ]
            query = request[ "query" ]
            processor_id = request["access_token"]
            resource_name = request["resource_name"]
            
            #get the processor id here...
            
        except:
            return self.format_process_failure(
                "access_exception",
                "Database problems are currently being experienced"
            ) 

        try:
            sandbox = self.setup_sandbox( user, query )

        #TODO: Should probably log exceptions like these                           
        except Exception, e:
            return self.format_process_failure(
                "processing_exception",
                "Compile-time failure - %s:%s" % 
                ( type( e ).__name__,  e )
            ) 

        #finally invoke the function
        try:
            execution_time = time.time()
            result = sandbox.run( parameters ) 
           
            try:
                self.db.insert_execution(processor_id=processor_id,parameters=jsonParams, result=json.dumps(result), executed=execution_time)
            except:
                log.error("failed to store the execution details : processor_id %s parameters: %s " % (processor_id, jsonParams))
            
            return self.format_process_success(result )
        
        #and catch any problems that occur in processing
        except:
           
            return self.format_process_failure(
                "processing_exception",
                "Run-time failure - %s " % str( sys.exc_info() )
            ) 

            
    #///////////////////////////////////////////////
    
    
    def setup_sandbox( self, user, query ) :
        
        #setup sandbox module for running query in
        #TODO: THIS NEEDS A LOT MORE TIGHTENING UP! 
        sandbox = module( "sandbox" )
        #sandbox.__dict__[ '__builtins__' ] = self.sandbox_builtins
        sandbox.db = self.db
        sandbox.resourcedb = self.resourcedb
        #setup constants available to the query
        sandbox.user = user

        #load the query function into memory
        exec query in sandbox.__dict__
        
        return sandbox
        
            
    #///////////////////////////////////////////////
    
        
    def permit_processor( self, install_token, client_id, resource_name, query, expiry_time ): 
        
        #check that the shared_secret is correct for this user_id
        try:
            
            
            install = self.db.authenticate( install_token )
            

            if ( not install ) or install[ "user_id" ] == None:
                return self.format_register_failure(
                    "permit_failure",
                    "no user found corresponding to that install_token"
                ) 
        except:    
            return self.format_register_failure(
                "permit_failure",
                "Database problems are currently being experienced"
            ) 
        
        #check that the client_id exists and is valid
        if not ( client_id ):
            return self.format_register_failure(
                "permit_failure",
                "A valid client ID has not been provided"
            )  
        
        # TODO now..
        # check sql fields against resource schema
        # check that the sql is syntactically correct
        
        if not self._check_constraints(resource_name, query):
            return self.format_register_failure(
                    "permit_failure",
                    "your query violates constraints"
            )
             
        #check that the requested query is syntactically correct
        #try:
        #    compile( query, '', 'exec' )
        #except Exception, e:
        #    return self.format_register_failure(
        #        "permit_failure",
        #        "Compilation error: %s" % str( e )
        #    ) 
            
        #TODO: check that the expiry time is valid
        #TODO: check that the resource_id is correct (i.e. us)
        #TODO: should check code here to confirm that it is valid 
        #TODO: this could be done by comparisng the checksum for acceptable queries?
        #TODO: this will require sandboxing, and all sorts...
       
        #so far so good. Time to generate an access token
       
        access_token = self.generateAccessToken()
        
        log.info("generated access token %s" % access_token)
        
        try:
            self.db.insert_processor( 
                access_token, 
                client_id, 
                resource_name,
                install[ "user_id" ],
                expiry_time, 
                query 
            )      
            return self.format_register_success( access_token ) 
        
        #if the token already exists an Integrity Error will be thrown
        except MySQLdb.IntegrityError:
            return self.format_register_failure(
                "permit_failure",
                "An identical request already exists"
            ) 
              
        except:    
            return self.format_register_failure(
                "permit_failure",
                "Database problems are currently being experienced"
            ) 
            
                
    #///////////////////////////////////////////////
    
    
    def revoke_processor( self, install_token, access_token ):
        
        log.error("in revoke processor!")
        
        #check that the shared_secret is correct for this user_id
        try:
            if not access_token :
                return self.format_register_failure(
                    "revoke_failure",
                    "A processor_token has not been supplied"
                ) 
            log.error("getting install!")
            install = self.db.authenticate( install_token )
            log.error("got install!")
            
            if ( not install ) or install[ "user_id" ] == None:
                return self.format_register_failure(
                    "revoke_failure",
                    "no user found corresponding to that install_token"
                ) 
            log.error("deleting processor!")
            if self.db.delete_processor( install[ "user_id" ], access_token ) :
                log.error("deleteed processor!")
                return self.format_register_success()
             #don't we also have to delete the install?    
            else :
                return self.format_register_failure(
                    "revoke_failure",
                    "Request with that request_token could not found"
                ) 
        except:    
            return self.format_register_failure(
                "revoke_failure",
                "Database problems are currently being experienced"
            ) 
            
            
    #///////////////////////////////////////////////
    
    # All this does at the moment is to check that the table being queried matches a resource
    # that a user has shared with the catalog.
    
    def _check_constraints(self, resource_name, query):
        myresources = [resource_name]            
        
        tables = SqlParser.extract_tables(query)  
        
        
        print "tables is .."
        print tables
        print "my resources is:"
        print myresources
        
        if len(tables) == 0:
            return False
            
        return set(tables).issubset(myresources)
                   
    def generateAccessToken( self ):
        
        token = base64.b64encode(  
            hashlib.sha256( 
                str( random.getrandbits( 256 ) ) 
            ).digest() 
        )  
            
        #replace plus signs with asterisks. Plus signs are reserved
        #characters in ajax transmissions, so just cause problems
        return token.replace( '+', '*' ) 

        
    
    
