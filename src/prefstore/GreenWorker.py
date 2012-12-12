import threading
import urllib2
import urllib
import json

class GreenWorker():

    def __init__(self, pm):
        self.queue = queue.Queue()
        self.pm = pm
    
    def add(self, request):
         self.queue.put_nowait(request)
               
    def run(self):
        while True:
            try:
            
                request = self.queue.get()
                
                result = self.pm.invoke_processor_sql( 
                    request['access_token'], 
                    request['jsonParams'],
                    request['view_url']
                )
                
                if not(result is None):
                    url = request['result_url']
                    data = urllib.urlencode(json.loads(result))
                    req = urllib2.Request(url,data)
                    f = urllib2.urlopen(req)
                    response = f.read()
                    f.close()
                    print "sent worker response"
            except Exception, e:   
                print e
                    
            finally:
                #self.work_queue.task_done()
                print "done.."