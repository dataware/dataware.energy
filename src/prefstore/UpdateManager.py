from gevent.event import Event
#from bottle import *  

class UpdateManager(object):
     
    def __init__(self):
        self.event    = Event()
        self.messages = []
        
    def trigger(self, message):
        try:  
            self.messages.append(message);    
            self.event.set()
            self.event.clear() 
        except Exception, e:   
            log.error("exception notifying") 
            print e
            
    def latest(self):
        return self.messages[-1]
        
    def queuelen(self):
        return len(self.messages)            
    