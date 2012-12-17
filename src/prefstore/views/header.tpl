<html>
<head>
<title>My dataware resources</title>

<link rel="stylesheet" type="text/css" href="./static/bootstrap/css/bootstrap.min.css" /> 
<link rel="stylesheet" type="text/css" href="./static/jqcloud.css" />
<script type="text/javascript" src="./static/jquery/jquery-1.8.2.min.js"></script>
<script type="text/javascript" src="./static/jquery/jquery-ui-1.8.23.min.js"></script>
<script type="text/javascript" src="./static/knockout/knockout-2.1.0.js"></script>
<script type="text/javascript" src="./static/knockout/knockout-postbox.min.js"></script>
<script type="text/javascript" src="./static/bootstrap/js/bootstrap.min.js"></script>
<script type="text/javascript" src="./static/bootstrap/js/bootstrap-notify.js"></script>
<script type="text/javascript" src="./static/jqcloud/jqcloud-1.0.1.min.js"></script> 
<script type="text/javascript" src="http://www.google.com/jsapi"></script>


<script>
    var NotificationModel = function(){
        
        var self = this;
        
        this.events = ko.observableArray([]);
        
        this.lastEvent = ko.observable("").publishOn("myevents");
         
        /*
         * subscribe to the events observable array and publish the last
         * element, to be viewed by other view models.  Note that this currently
         * sends a reference.  To create a deep copy we could do ko.toJSON and recreate
         * at the other end.
         */
        this.events.subscribe(function(newValue){
            console.log(this.events()[this.events().length -1]);
            this.lastEvent(this.events()[this.events().length -1]);
            
            
        },this);
        
        
        this.read = function(message){
            self.events.remove(message);
        };
        
        this.startpolling = function(frequency){
            
            setTimeout(function(){
        
                $.ajax({
                    url: "/stream",
                    dataType: 'json', 
                    timeout: 30000,
                    cache: false,
                    
                    success: function(data) {
                        frequency = 500;
                        console.log(data);
                        
                        self.events.push(data);
                        //self.latestEvent(data.message);
                        $('.top-right').notify({
                         message: { text: data.message }
                        }).show();
                    },
                     
                    error: function(XMLHttpRequest, textStatus, errorThrown){
                        switch(XMLHttpRequest.status){
                            case 502: //update server is down
                            case 403: //forbidden - unlikely to get access anytime soon
                                frequency = 60000;
                                break; 
                            default:
                                frequency = 500;
                        }
                    },
                    
                    complete: function(){
                        self.startpolling(frequency);        
                    }
                });
            
            },frequency);
        }
    }
</script>
<script>

 function ResourceModel(){
        
        var self = this;
        
        this.selectedResource = ko.observable("urls");
        
        this.selectedUrl = ko.observable("");
        
        this.event = ko.observable().subscribeTo("myevents", true);
        
        
        this.install_url = ko.computed(function(){
            return "install?resource_name=" + self.selectedResource(); 
        });
        
        this.requestText = ko.computed(function(){
            if (self.selectedUrl())
                return self.selectedUrl().requests  + " requests";
            return "";
        });
    } 
</script>

<script>
    function ExecutionModel(){
       
        
        var self = this;
         
        this.executions = ko.observableArray([]);
        
        this.tsToString = function(ts){
            function pad(n) { return n < 10 ? '0' + n : n }
             
            a = new Date(ts);
            
            months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
            
            year = a.getFullYear();
            month = months[a.getMonth()];
            day = a.getDate();
        
            hour = pad(a.getUTCHours());
            min = pad(a.getUTCMinutes());
            sec = pad(a.getUTCSeconds());
            return  day+' '+month+' '+year + "," + hour + ":" + min + ":" + sec;
        }
        
        //filter out all execution events from the pool of all events.
        this.loadData = function(data){
            $.each(data, function(i, execution){
                execution.result = $.parseJSON(execution.result);
                execution.executed = self.tsToString( execution.executed * 1000);
                self.executions.push(execution);
            });    
        };
        
        ko.postbox.subscribe("myevents", function(newValue) {
            if (newValue.type == "execution"){
                console.log(newValue.data);
                execution = $.parseJSON(newValue.data);
                //turn the result to an object too..
                execution.result = $.parseJSON(execution.result);
                execution.executed = self.tsToString( execution.executed * 1000);
                console.log(execution);
                this.executions.push(execution);
            }
        }, this);
        
        this.executions.subscribe(function(newValue){console.log(this.executions())},this);
    }
</script> 

<script>

	PREFSTORE = "http://hwresource.block49.net:9000/" 
	 
	$( document ).ready( function() {
		$( 'a.menu_button' ).click( function() {
			self.parent.location=  $( this ).attr('id');
		});
		
		var nm = new NotificationModel();
		//var rm = new ResourceModel();
		
		ko.applyBindings(nm,$(".navbar-inner")[0]);
        //ko.applyBindings(rm, $(".mydata")[0]);
        
        
        nm.startpolling();
	});
</script>

</head>

<body>
<div class="navbar">
    <div class="navbar-inner">
        <a class="brand" href="#">My dataware resources</a>
        <ul class="nav">
            <li><a href="#" class="menu_button" id="home">home</a></li>
            
            %if user:
            <li><a href="#" class="menu_button" id="view_executions">executions</a></li>
            <li><a href="#" class="menu_button" id="logout">logout</a></li>
            %else:
            <li><a href="#" class="menu_button" id="login">login/register</a></li>
            %end
        </ul>
        <ul class="nav pull-right">                            
            <li class="dropdown">
                <a class="dropdown-toggle" id="dLabel" role="button" data-toggle="dropdown" data-target="#" href="#"> 
                <span class="badge badge-success" data-bind="text:events().length"></span>
                    <b class="caret"></b>
                </a>
                <ul class="dropdown-menu" role="menu" aria-labelledby="dLabel" data-bind="{foreach: events}">
                    <li> 
                        <a href="#" data-bind="click:function(){$parent.read($data);}"> 
                        <span data-bind="text:message"></span> 
                        </a>
                    </li>
                </ul>
            </li>                  
        </ul>
    </div>
</div>

<div class="container">
    <div class="row">
        <div class="span4 offset8">
            <div class='notifications top-right'></div>
        </div>
    </div>
</div>