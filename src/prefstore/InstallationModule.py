"""
Created on 12 April 2011
@author: jog
"""

from new import * #@UnusedWildImport
import base64
import hashlib
import json
import logging
import random
import re
import urllib
import urllib2

#setup logger for this module
log = logging.getLogger( "console_log" )

#///////////////////////////////////////////////


class ParameterException ( Exception ):
    def __init__(self, msg):
        self.msg = msg

#///////////////////////////////////////////////  


class CatalogException ( Exception ):
    def __init__(self, msg):
        self.msg = msg

        
#///////////////////////////////////////////////

        
class InstallationModule( object ) :
    
         
    #///////////////////////////////////////////////
    
    
    def __init__( self, resource_name, redirect_uri, datadb, web_proxy = None ):
        
        self.db = datadb;
        self.resource_name = resource_name
        self.redirect_uri = redirect_uri
        self.web_proxy = web_proxy  


    #///////////////////////////////////////////////

            
    def initiate_install( self, user_id, catalog_uri, resource_name, resource_uri ):
        
        #check that a valid catalog_uri has been supplied
        if not self._is_valid_uri( catalog_uri ):
            raise ParameterException( "invalid catalog URI" )
    
        #also confirm that its and endpoint (not a directory)
        if catalog_uri[ -1 ] == "/":
            raise ParameterException( "catalog URI must not end with /" )
        
        #obtain the resource_id assigned by the catalog - or
        #if it doesn't exist, register ourselves at the catalog
        resource_id = self._check_registration( catalog_uri, resource_name, resource_uri )
       
        #check to see if we have already made the install request
        install = self.db.fetch_install( user_id, catalog_uri, resource_name ) 
        
        #if we have, use the state details we already have:
        if ( install ):
            state = install[ "state" ]
            
        #otherwise initiate the request, leaving it pending in
        #the database and get a new state id.        
        else:
            state = self.db.insert_install( user_id, catalog_uri, resource_name ) 
            self.db.commit()
            
        #finally build the uri that we will redirect the user to
        data = urllib.urlencode({
            'resource_id': resource_id,
            'state': state,            
            'redirect_uri': self.redirect_uri, })
        
        url = "%s/resource_request?%s" % ( catalog_uri, data )
      
        return url 
            
    
    #///////////////////////////////////////////////


    def complete_install( self, user, state, code ):
        
        if not ( state and code ):
            raise ParameterException( 
                "Catalog has not returned the correct parameters" )
        
       
        #check to see if we have actually made the install request
        install = self.db.fetch_install_by_state( state ) 
        
        
        if not ( install ):
            raise ParameterException( 
                "Catalog has not returned a recognized state" )
        
       
        
        access_token = self._make_token_request( 
            install[ "catalog_uri"], 
            code )
        
     
        #need to have resourcename/code/state too else will update all?
        
        result = self.db.update_install( 
            install[ "user_id" ], 
            install[ "catalog_uri" ], 
            access_token,
            state ) 
        
        
        self.db.commit()

    #///////////////////////////////////////////////
    
        
    def fail_install( self, user, state ):
        
        if not ( state ):
            raise ParameterException( 
                "Catalog has not returned the correct parameters" )
    
        #check to see if we have already made the install request
        install = self.db.fetch_install_by_state( state ) 
        
        if not ( install ):
            raise ParameterException( 
                "Catalog has not returned a recognized state" )
            
        self.db.delete_install( install[ "user_id" ], install[ "catalog_uri"] )
        
             
    #///////////////////////////////////////////////


    def _make_token_request( self, catalog_uri, code ):
   
        #so now we need to swap the authorization code for an access 
        #token by a GET request to the appropriate endpoint. The endpoint
        #returns a json response.
        try:
            data = urllib.urlencode({
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri,
                'code': code, })
            url = "%s/resource_access?%s" % ( catalog_uri, data )
            
            req = urllib2.Request( url )
            response = urllib2.urlopen( req )
            output = response.read()
            
            access_token = self._parse_access_results( output )
            print "finished getting access_token %s" % access_token
            
            return access_token
        
        except urllib2.URLError:
            raise CatalogException( "Could not contact the catalog to get access token" )
        
        
    #///////////////////////////////////////////////
            
    
    def _parse_access_results( self, output ):
           
        #parse the json response from the provider
        try:
            output = json.loads( output.replace( '\r\n','\n' ), strict=False )
        except:
            raise CatalogException( "Invalid json returned by catalog" )
    
        #determine whether the registration has been successful
        try:
            success = output[ "success" ]
        except:
            raise CatalogException( "Catalog has not returned successfully" )
    
        #if it has then extract the access_token that will be used
        if not success:
            try:
                error = "%s: %s" % ( 
                    output[ "error" ], 
                    output[ "error_description" ], )
            except:
                error = "Unknown problems at catalog accepting request"
                
            raise CatalogException( error );
        
        #attempt to extract the resource_id
        try:
            return output[ "access_token" ]
        except:
            raise CatalogException( "Catalog failed to return an access_token" ) 
        
    
    #///////////////////////////////////////////////
    
        
    def _check_registration( self, catalog_uri, resource_name, resource_uri ):
    
        #determine if we have already registered at this resource - must check the resource_name too!
        catalog = self.db.fetch_catalog( catalog_uri, resource_name )
        
        #if so simply return the resource_id the catalog gave us...
        if catalog:
            log.info("ALREADY REGISTERED SO RETURNING resource id %s", catalog[ "resource_id" ])
            return catalog[ "resource_id" ]
        
        #and if not register ourselves with the catalog, and get one...
        else:
            log.info("NEW REGISTRATION, MAKING REGISTRATION REQUEST")
            catalog_response = self._make_registration_request( catalog_uri, resource_name, resource_uri )
            log.info(catalog_response)
            resource_id = self._parse_registration_results( catalog_response )
            log.info("INSERTING %s %s %s" % (catalog_uri, resource_id, resource_name))
            self.db.insert_catalog( catalog_uri, resource_id, resource_name )
            self.db.commit()
            log.info("RETURNING %s" % resource_id)
            return resource_id
        

    #///////////////////////////////////////////////


    def _is_valid_uri( self, uri ):
        
        if not uri: return False
        
        regex = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE )
        
        return regex.search( uri )


    #///////////////////////////////////////////////

            
    def _make_registration_request( self, catalog_uri, resource_name, resource_uri ):
        
        #if necessary setup a proxy
        if ( self.web_proxy  ):
            proxy = urllib2.ProxyHandler( self.web_proxy )
            opener = urllib2.build_opener( proxy )
            urllib2.install_opener( opener )
        
        #communicate with the catalog and obtain the
        #resource_id that they assign us   
        try:
            data = urllib.urlencode({
                'resource_name': resource_name,
                'redirect_uri': resource_uri, })
            url = "%s/resource_register" % ( catalog_uri, )
            req = urllib2.Request( url, data )
            response = urllib2.urlopen( req )
            resource_id = response.read()
            return resource_id
    
        except urllib2.URLError:
            raise CatalogException( "Could not contact supplied catalog" )
       
        
    #///////////////////////////////////////////////
    
            
    def _parse_registration_results( self, output ):
           
        #parse the json response from the provider
        try:
            output = json.loads( output.replace( '\r\n','\n' ), strict=False )
        except:
            raise CatalogException( "Invalid json returned by catalog" )
    
        #determine whether the registration has been successful
        try:
            success = output[ "success" ]
        except:
            raise CatalogException( "Catalog has not returned successfully" )
    
        #if it has then extract the access_token that will be used
        if not success:
            try:
                error = "%s: %s" % ( 
                    output[ "error" ], 
                    output[ "error_description" ], )
            except:
                error = "Unknown problems at catalog accepting request"
                
            raise CatalogException( error );
        
        #attempt to extract the resource_id
        try:
            return output[ "resource_id" ]
        except:
            raise CatalogException( "Catalog failed to return resource id" ) 

         
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

        
    
    