import threading
import urllib2
import urllib
import json

class Worker(threading.Thread):

    def __init__(self, work_queue, pm):
        #super(self).__init__()
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.pm = pm
        
    def run(self):
        while True:
            try:
                request = self.work_queue.get()
                print "REQUEST IS"
                print request
                
                result = self.pm.invoke_processor_sql( 
                    request['access_token'], 
                    request['jsonParams'],
                    request['view_url']
                )
                
                if not(result is None):
                    url = request['result_url']
                    data = urllib.urlencode(json.loads(result))
                    req = urllib2.Request(url,data)
                    print "sending %s" % json.loads(result)
                    f = urllib2.urlopen(req)
                    response = f.read()
                    print response
                    f.close()
            except Exception, e:   
                print e
                    
            finally:
                self.work_queue.task_done()