"""
Created on 12 April 2011
@author: jog
"""
from __future__ import division
from bottle import *                #@UnusedWildImport
from ProcessingModule import *      #@UnusedWildImport
from InstallationModule import *    #@UnusedWildImport
from DatawareDB import *            #@UnusedWildImport
from HomeuserDB import *           #@UnusedWildImport
import time                         #@Reimport
import OpenIDManager
import logging.handlers
import math

#//////////////////////////////////////////////////////////
# SETUP LOGGING FOR THIS MODULE
#//////////////////////////////////////////////////////////

log = logging.getLogger( "console_log" )
data_log = logging.getLogger( "data_log" )

class std_writer( object ):
    def __init__( self, msg ):
        self.msg = msg
    
    def write(self, data):
        data = data.replace( '\n', '' ) \
                   .replace( '\t', '' )
        if len( data ) > 0 :
            log.error( self.msg + ": " + data )
        
        
#//////////////////////////////////////////////////////////
# DATAWARE WEB-API CALLS
#//////////////////////////////////////////////////////////


def format_success( url, ):
   
    return json.dumps({
        'success':True, 
        'redirect':url,  
    })
        

#///////////////////////////////////////////////


def format_failure( cause, error, ):
   
    return json.dumps({ 
        'success':False, 
        'cause':cause,        
        'error':error,  
    })
        

#///////////////////////////////////////////////
 
 
@route( '/install', method = "GET", )
def install():

    try:
        user = check_login()
        if ( not user ): redirect( ROOT_PAGE )
    except RegisterException, e:
        redirect( "/register" )
    except LoginException, e:
        return error( e.msg )
    except Exception, e:
        return error( e )        
        
    return template( 'install_page_template', user=user ) 
    

#///////////////////////////////////////////////
 
 
@route( '/install_request', method = "GET" )
def install_request():
    
    try:
        user = check_login()
        if ( not user ): redirect( ROOT_PAGE )
    except RegisterException, e:
        redirect( "/register" )
    except LoginException, e:
        return error( e.msg )
    except Exception, e:
        return error( e )        

    catalog_uri = request.GET.get( "catalog_uri", None )
    
    try:
        url = im.initiate_install( user[ "user_id" ], catalog_uri  )
        return format_success( url )
    except ParameterException, e:
        return format_failure( "resource", e.msg )
    except CatalogException, e:    
        return format_failure( "catalog", e.msg )
        
         
#///////////////////////////////////////////////


@route( '/install_complete', method = "GET" )
def install_complete():
    
    try:
        user = check_login()
    except RegisterException, e:
        redirect( "/register" )
    except LoginException, e:
        return error( e.msg )
    except Exception, e:
        return error( e )  
    
    error = request.GET.get( "error", None )
    state = request.GET.get( "state", None )
    code = request.GET.get( "code", None )
        
    if ( error ):
        try:
            im.fail_install( user, state )
            #TODO: tell the user that the installation failed (a redirect?)
            return "installation failed: %s" % \
                ( request.GET.get( "error_description", "unspecified error" ) )
                
        except ParameterException, e:
            return e.msg

    else:
        #complete the install, swapping the authorization code
        #we've received from the catalog, for the access_token
        try:
            im.complete_install( user, state, code )
            
        except ParameterException, e:
            #TODO: make this more explanatory
            return e.msg
        
        except CatalogException, e:
            #TODO: make this more explanatory
            return e.msg
        
        except Exception, e:
            return error( e )
        
        #TODO: tell the user that the installation succeeded (a redirect?)
        return "installation success"

        
@route( "/static/:filename" )
def user_get_static_file( filename ):
    
    return static_file( filename, root='static/' )



@route( "/static/:path#.+#" )

def user_get_static_file( path ):
   
    return static_file( path, root='static/' )



#//////////////////////////////////////////////////////////
# 3RD PARTY PROCESSOR SPECIFIC WEB-API CALLS
#//////////////////////////////////////////////////////////
   
    
@route( '/invoke_processor', method = "POST")
def invoke_processor():
    
    try:
        access_token = request.forms.get( 'access_token' )
        jsonParams = request.forms.get( 'parameters' )
        result = pm.invoke_processor( 
            access_token, 
            jsonParams )
        return result
    except Exception, e:
        raise e
     

#///////////////////////////////////////////////
 
 
@route( '/permit_processor', method = "POST" )
def permit_processor():

    #we receive a resource_token and resource_id that matches us,
    #proving that the message is from the catalog, along with 
    #details of the query the client is proposing...
    try:
        install_token = request.forms.get( 'install_token' )
        client_id = request.forms.get( 'client_id' )
        query = request.forms.get( 'query' ).replace( '\r\n','\n' )
        expiry_time = request.forms.get( 'expiry_time' )        

        result = pm.permit_processor( 
            install_token,
            client_id,
            query,
            expiry_time 
        )
        
        #the result, if successful, will include an processing_token
        return result
    
    except Exception, e:
        raise e
          

#///////////////////////////////////////////////
 
 
@route( 'revoke_processor', method = "POST" )
def revoke_processor( user_name = None ):
    
    try:
        install_token = request.forms.get( 'install_token' )
        access_token = request.forms.get( 'access_token' )

        result = pm.revoke_processor( 
            install_token=install_token,
            access_token=access_token,
        )
        
        return result
    
    except Exception, e:
        raise e


    
#//////////////////////////////////////////////////////////
# OPENID SPECIFIC WEB-API CALLS
#//////////////////////////////////////////////////////////


@route( '/login', method = "GET" )
def openID_login():

    try: 
        username = request.GET[ 'username' ]    
    except: 
        username = None
     
    try:      
        provider = request.GET[ 'provider' ]
    except: 
        return template( 'login_page_template', user=None )
    
    try:
        url = OpenIDManager.process(
            realm=REALM,
            return_to=REALM + "/checkauth",
            provider=provider,
            username=username
        )
    except Exception, e:
        return error( e )
    
    #Here we do a javascript redirect. A 302 redirect won't work
    #if the calling page is within a frame (due to the requirements
    #of some openid providers who forbid frame embedding), and the 
    #template engine does some odd url encoding that causes problems.
    return "<script>self.parent.location = '%s'</script>" % (url,)
    

#///////////////////////////////////////////////

 
@route( "/checkauth", method = "GET" )
def authenticate():
    
    o = OpenIDManager.Response( request.GET )
    
    #check to see if the user logged in succesfully
    if ( o.is_success() ):
        
        user_id = o.get_user_id()
         
        #if so check we received a viable claimed_id
        if user_id:
            
            try:
                
                user = datadb.fetch_user_by_id( user_id )
              
                #if this is a new user add them
                if ( not user ):
                    datadb.insert_user( o.get_user_id() )
                    datadb.commit()
                    user_name = None
                else :
                    user_name = user[ "user_name" ]
                
                set_authentication_cookie( user_id, user_name  )
                
            except Exception, e:
                return error( e )
            
            
        #if they don't something has gone horribly wrong, so mop up
        else:
            delete_authentication_cookie()

    #else make sure the user is still logged out
    else:
        delete_authentication_cookie()
        
    return "<script>self.parent.location = '%s'</script>" % ( REALM + ROOT_PAGE,)
       
       
#///////////////////////////////////////////////


@route( "/login_local", method = "GET" )
def login_local():
    
    user_name = request.GET.get( "user_name", None )   
    try:
        user = datadb.fetch_user_by_name( user_name )
        set_authentication_cookie( user[ "user_id" ], user_name  )
                
    except Exception, e:
        return error( e )
        
    return "<script>self.parent.location = '%s'</script>" % ( REALM + ROOT_PAGE,)
       
       
#///////////////////////////////////////////////


@route('/logout')
def logout():
    
    delete_authentication_cookie()
    redirect( ROOT_PAGE )
    
        
#///////////////////////////////////////////////
 
         
def delete_authentication_cookie():
    
    response.delete_cookie( 
        key=EXTENSION_COOKIE,
    )
            
#///////////////////////////////////////////////


def set_authentication_cookie( user_id, user_name = None ):
    
    #if the user has no "user_name" it means that they
    #haven't registered an account yet    
    if ( not user_name ):
        json = '{"user_id":"%s","user_name":null}' \
            % ( user_id, )
        
    else:
        json = '{"user_id":"%s","user_name":"%s"}' \
            % ( user_id, user_name )
         
    response.set_cookie( EXTENSION_COOKIE, json )
                            

#//////////////////////////////////////////////////////////
# PREFSTORE SPECIFIC WEB-API CALLS
#//////////////////////////////////////////////////////////


class LoginException ( Exception ):
    
    def __init__(self, msg):
        self.msg = msg


#///////////////////////////////////////////////  


class RegisterException ( Exception ):
    """Base class for RegisterException in this module."""
    
    pass

    
#///////////////////////////////////////////////


def valid_email( str ):
    
    return re.search( "^[A-Za-z0-9%._+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}$", str )


#///////////////////////////////////////////////


def valid_name( str ):

    return re.search( "^[A-Za-z0-9 ']{3,64}$", str )


#///////////////////////////////////////////////
    
@route('/queryurl', method = "GET")  
def query_url():
    try:
        return 0
        #homedb.fetch_urls()
    except Exception, e:
        return error( e )

@route( '/register', method = "GET" )
def user_register():
    
    try:
        log.info("extracting  id...");
        user_id = extract_user_id()
        log.info("got id %s" % user_id);
    except LoginException, e:
        return error( e.msg )
    except Exception, e:
        return error( e )
    
    errors = {}
    
    #if the user has submitted registration info, parse it
    try: 
        request.GET[ "submission" ]
        submission = True;
    except:
        submission = False
        
    if ( submission ): 
        #validate the user_name supplied by the user
        try:
            user_name = request.GET[ "user_name" ]
            if ( not valid_name( user_name ) ):
                errors[ 'user_name' ] = "Must be 3-64 legal characters"
            else: 
                match = datadb.fetch_user_by_name( user_name ) 
                if ( not match is None ):
                    errors[ 'user_name' ] = "That name has already been taken"                    
        except:
            errors[ 'user_name' ] = "You must supply a valid user name"
    
        #validate the email address supplied by the user
        try:
            email = request.GET[ "email" ]
            if ( not valid_email( email ) ):
                errors[ 'email' ] = "The supplied email address is invalid"
            else: 
                match = datadb.fetch_user_by_email( email ) 
                if ( not match is None ):
                    errors[ 'email' ] = "That email has already been taken"
        except:
            errors[ 'email' ] = "You must supply a valid email"


        #if everything is okay so far, add the data to the database    
        if ( len( errors ) == 0 ):
            try:
                log.info("inserting registration...");
                match = datadb.insert_registration( user_id, user_name, email) 
                log.info("done inserting registration..., commiting");
                datadb.commit()
                log.info("committed");
            except Exception, e:
                return error( e )

            #update the cookie with the new details
            set_authentication_cookie( user_id, user_name )
            
            #return the user to the home page
            redirect( ROOT_PAGE )

    #if this is the first visit to the page, or there are errors    
    else:
        email = ""
        user_name = ""
        
    return template( 
        'register_page_template', 
        user=None, 
        email=email,
        user_name=user_name,
        errors=errors ) 
    

#///////////////////////////////////////////////


def error( e ):
    
    return  "An error has occurred: %s" % ( e )

      
#///////////////////////////////////////////////  
    
    
def extract_user_id():
    
    cookie = request.get_cookie( EXTENSION_COOKIE )
        
    #is the user logged in? First check we have a cookie...
    if cookie:
        #and that it contains suitably formatted data
        try:
            data = json.loads( cookie )
        except:
            delete_authentication_cookie()
            raise LoginException( "Your login data is corrupted. Resetting." )
        
        #and then that it contains a valid user_id
        try:
            user_id =  data[ "user_id" ]
            return user_id
        except:
            delete_authentication_cookie()
            raise LoginException( "You are logged in but have no user_id. Resetting." )
    else:
        None

  
#///////////////////////////////////////////////  
    
    
def check_login():

    #first try and extract the user_id from the cookie. 
    #n.b. this can generate LoginExceptions
    user_id =extract_user_id()
    
    if ( user_id ) :
        
        #we should have a record of this id, from when it was authenticated
        user = datadb.fetch_user_by_id( user_id )
        
        if ( not user ):
            delete_authentication_cookie()
            raise LoginException( "We have no record of the id supplied. Resetting." )
        
        #and finally lets check to see if the user has registered their details
        if ( user[ "user_name" ] is None ):
            raise RegisterException()
        
        return user
        
    #if the user has made it this far, their page can be processed accordingly
    else:
        return None   
    
 
#///////////////////////////////////////////////  
    
    
@route( '/', method = "GET" )     
@route( '/home', method = "GET" )
def home( ):

    try:
        user = check_login()
    except RegisterException, e:
        redirect( "/register" ) 
    except LoginException, e:
        return error( e.msg )
  
    if ( not user ):
        summary = None
    else:
        user[ "registered_str" ] = time.strftime( "%d %b %Y %H:%M", time.gmtime( user[ "registered" ] ) )
        user[ "last_distill_str" ] = time.strftime( "%d %b %Y %H:%M")
        
       
        user[ "average_appearances" ] = 0
        user[ "total_documents" ] = 0
        user[ "total_term_appearances" ] = 0   
        
        summary = None #datadb.fetch_user_summary( user[ "user_id" ] )

    return template( 'home_page_template', user=user, summary=summary );
    
    
#///////////////////////////////////////////////  
    
    
@route('/summary')
def summary():
  
    try:
        user = check_login()
    except RegisterException, e:
        redirect( "/register" ) 
    except LoginException, e:
        return error( e.msg )
    except Exception, e:
        return error( e )     
    
    #if the user doesn't exist or is not logged in,
    #then send them home. naughty user.
    if ( not user ) : redirect( ROOT_PAGE )

    user[ "registered_str" ] = time.strftime( "%d %b %Y %H:%M", time.gmtime( user[ "registered" ] ) )
    user[ "last_distill_str" ] = time.strftime( "%d %b %Y %H:%M")
    user[ "average_appearances" ] = 0
    user[ "total_documents" ] = 0
    user[ "total_term_appearances" ] = 0
    summary = None # datadb.fetch_user_summary( user[ "user_id" ] )

    return template( 'summary_page_template', user=user, summary=summary );
    
    

            
#//////////////////////////////////////////////////////////
# MAIN FUNCTION
#//////////////////////////////////////////////////////////


if __name__ == '__main__' :

    #-------------------------------
    # setup logging
    #-------------------------------
    log.setLevel( logging.DEBUG )
    data_log.setLevel( logging.DEBUG )    

    # create handlers
    #LOCAL
    ch = logging.StreamHandler(sys.stdout)
    
    #ch = logging.handlers.TimedRotatingFileHandler( 
    #    filename='logs/prefstore.log',
    #    when='midnight', 
    #    interval=21 )
    
    fh = logging.handlers.TimedRotatingFileHandler( 
        filename='logs/prefstore_data.log',
        when='midnight', 
        interval=21 )
        
    # create formatter and add it to the handlers
    formatter = logging.Formatter( '--- %(asctime)s [%(levelname)s] %(message)s' )
    ch.setFormatter( formatter )
    fh.setFormatter( formatter )    

    # add the handlers to the logger
    log.addHandler( ch )
    data_log.addHandler( fh )    
            
    # redirect standard outputs to prevent errors running the process
    # as a daemon (due to print statements in python socket libraries.
    sys.stdout = std_writer( "stdout" )
    sys.stderr = std_writer( "stderr" )
    
    #-------------------------------
    # constants
    #-------------------------------
    EXTENSION_COOKIE = "prefstore_logged_in"
    PORT = 9000
    HOST = "0.0.0.0"  
    BOTTLE_QUIET = True 
    ROOT_PAGE = "/"
    RESOURCE_NAME = "homework"
    RESOURCE_URI = "http://hwresource.block49.net:9000"
    #REALM = "http://www.prefstore.org"
    REALM = "http://hwresource.block49.net:9000"
    #WEB_PROXY = "http://mainproxy.nottingham.ac.uk:8080"
            
    #-------------------------------
    # declare initialization in logs
    #-------------------------------        
    print "-"*40
    print "PREFSTORE IGNITION"
    print "PORT = %s" % PORT
    print "HOST = %s" % HOST
    print "REALM = %s" % REALM
    print "BOTTLE_QUIET = %s" % BOTTLE_QUIET
    print "-"*40
    
    #---------------------------------
    # Initialization
    #---------------------------------
    try:
       
        
        homedb = HomeDB()
        homedb.connect()
        homedb.check_tables()
        
        datadb = DataDB()
        datadb.connect()
        datadb.check_tables()
        
        log.info("created datadb!!");
        
        log.info( "database initialization completed... [SUCCESS]" );
        
    except Exception, e:
        log.error( "database initialization error: %s" % ( e, ) )
        exit()
         
    #---------------------------------
    # module initialization
    #---------------------------------
    try:    
        pm = ProcessingModule( datadb, homedb )
        im = InstallationModule( RESOURCE_NAME, RESOURCE_URI, datadb )
        log.info( "module initialization completed... [SUCCESS]" );
    except Exception, e:
        log.error( "module initialization error: %s" % ( e, ) )
    
      
    #---------------------------------
    # Web Server initialization
    #---------------------------------
    try:
        debug( True )
        run( host=HOST, port=PORT, quiet=BOTTLE_QUIET )
    except Exception, e:  
        log.error( "Web Server Exception: %s" % ( e, ) )
        exit()
   
    #---------------------------------
    # Initialization Complete
    #---------------------------------
    log.info("Catalog Firing on all cylinders...")
    log.info("-"*40)

    
   
