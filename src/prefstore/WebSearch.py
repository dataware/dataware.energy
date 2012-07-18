'''
Created on 18 Apr 2011

@author: psxjog
'''

import urllib
import json
import logging
import sys

#setup logger for this module
log = logging.getLogger( "console_log" )


class WebSearch( object ):
    
    _PROXY = None 
    _GOOGLE_KEY = None 
    _BING_KEY = None
    
    
    #///////////////////////////////////////

    
    def __init__( 
        self, 
        proxy = None, 
        bing_key = None, 
        google_key = None ):        
        
        if not proxy is None:
            self._PROXY =  {'http': proxy }
        if not bing_key is None:
            self._BING_KEY = bing_key 
        if not google_key is None:
            self._GOOGLE_KEY = google_key
         

        
    #///////////////////////////////////////////////       


    def getGoogleTotal( self, term ):
    
        # retrieve hits from bing for this query term
        result = urllib.urlopen( 
            "https://www.googleapis.com/customsearch/v1?key=%s&q=%s" % 
            ( self._GOOGLE_KEY, term ), 
            proxies=self._PROXY 
        )
        
        # collate the result
        output = "";
        for line in result.readlines() : 
            output += line;
        
        try:
            # ...and turn it into json
            jsonOutput = json.loads( output )
        
            #exception handling
            error = jsonOutput.get( 'error' ) 
            if error is None:
                return jsonOutput.get( 'totalResults' )
            else:
                log.error( 
                    "Error %d from Google: %s" %
                    ( error.get( 'code' ), error.get('message') ) 
                )
                return None
            
        except:
            log.error( "Google formatting error %s" % sys.exc_info()[0] )
            return None    
    
    
    #///////////////////////////////////////////////


    def getBingTotal( self, term ):

        # Retrieve hits from bing for this query term
        result = urllib.urlopen(
            "http://api.search.live.net/json.aspx?Appid=%s&query=%s&sources=web" % 
            ( self._BING_KEY, term ), 
            proxies=self._PROXY )
    
        # Collate the result
        output = "";
        for line in result.readlines() : 
            output += line;
    
        # ...and turn it into json
        jsonOutput = json.loads( output ).get( 'SearchResponse' )
    
        # do some error checking
        errors = jsonOutput.get( 'Errors' ) 
        if not errors is None:
            for e in errors :
                log.error( "Error %d from Bing: %s" %
                    ( e.get( 'Code' ), e.get('Message') ) )  
            raise
        
        # and finally try and extract a web count
        try:
            total = jsonOutput.get( "Web" ).get( "Total" )
            return total
        except:
            return None


    #///////////////////////////////////////////////


    def getBingImage( self, term ):

        # Retrieve hits from bing for this query term
        result = urllib.urlopen(
            "http://api.search.live.net/json.aspx?Appid=%s&query=%s&sources=Image&Image.Count=20&Image.Offset=0&Adult=Strict&Image.Filters=Aspect:square" % 
            ( self._BING_KEY, term ), 
            proxies=self._PROXY )    
        
        # Collate the result
        output = "";
        for line in result.readlines() : 
            output += line;
    
        # ...and turn it into json
        jsonOutput = json.loads( output ).get( 'SearchResponse' )
    
        # do some error checking
        errors = jsonOutput.get( 'Errors' ) 
        if not errors is None:
            for e in errors :
                log.error( "Error %d from Bing: %s" %
                    ( e.get( 'Code' ), e.get('Message') ) )  
            raise
        
        # and finally extract the image result
        try:

            urls = [  i.get( "Thumbnail" ).get( "Url" ) 
                for i in jsonOutput.get( "Image" ).get( "Results" ) ]
            return urls
        except:
            return None
