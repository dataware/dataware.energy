'''
Created on 8 May 2011

@author: psxjog
'''

from WebSearch import * #@UnusedWildImport
import PrefstoreDB
import datetime
import threading
import time
import logging

log = logging.getLogger( "console_log" )


#///////////////////////////////////////////////


class WebCountUpdater( threading.Thread ):
    
    #the length of time seconds between updating web term counts
    INTERVAL_DURATION = 60 * 10
    GOOGLE_APP_KEY = "AIzaSyBI8AxzRpN70njcpuOW9EaaRikxd-mc-1M&cx=017576662512468239146:omuauf_lfve"
    BING_KEY = "580DDBFFD1A4581F90038B9D5B80BA065FEFE4E7"
  
  
    #///////////////////////////////////////////////
        
        
    def __init__( self, web_proxy = None ):
        
        if ( web_proxy ):
            self.search = WebSearch( proxy=web_proxy, bing_key=self.BING_KEY )
        else:
            self.search = WebSearch( bing_key=self.BING_KEY )
                    
        self.database = PrefstoreDB.PrefDB( "webdb" );    
        threading.Thread.__init__( self )
 
 
    #///////////////////////////////////////////////
 
 
    def fetchCounts( self, terms ): 
        
        termsUpdated = 0;
        termsBlacklisted = 0;

        for term in terms:
            try:
                count = self.search.getBingTotal( term )

                # If we have no webcount then blacklist the term as useless
                if count is None:
                    self.database.blacklistTerm( term )
                    termsBlacklisted += 1 
                    
                # Otherwise update its freshly determined webcount    
                else:
                    self.database.updateTermCount( term, count )
                    termsUpdated += 1
                
                self.database.commit()

            except:
                log.error( "Error fetching web count for term %s: %s" % ( term, sys.exc_info()[0] ) )

        log.info( 
            "Web Count Update: Complete - %d terms, %d updated, %d blacklisted" % \
            ( len( terms) , termsUpdated, termsBlacklisted ) 
        )
        
        self.database.commit()
        
        
    #///////////////////////////////////////////////
             
             
    def getNextUpdate( self ):
        return self.nextUpdate
        
        
    #///////////////////////////////////////////////
             
             
    def run( self ):
        while True:
            
            self.database.connect()
            missingCountList = self.database.getMissingCounts();
        
            if missingCountList:
                log.info( "Web Count Update: %d terms require counts" % len( missingCountList ) )
                self.fetchCounts( missingCountList )
            else:
                log.info( "Web Count Update: all terms have counts" )
                
            self.nextUpdate = time.time() + self.INTERVAL_DURATION
             
            log.info( 
                "Web Count Update: next update at %s " 
                % datetime.datetime.fromtimestamp( self.nextUpdate )
            )

            self.database.close()
            time.sleep( self.INTERVAL_DURATION )
        