

<ul class="nav nav-tabs" id="myTab">
  <li class="active"><a href="#chart">chart</a></li>
  <li><a href="#raw">raw</a></li>
</ul>

<div class="tab-content">
  <div class="tab-pane active" id="chart">
    <div class="row">
        <div class="col-md-12" style="text-align:center">
             <h3><span class="from"></span> to <span class="to"></span></h3>
        </div>
    </div>
    
    <div class="row">
        
        
        <div class="col-md-1" style="height:300px; margin-top:130px;">
            <button id="earlier" type="button" class="btn btn-primary" > 
                <span class="glyphicon glyphicon-circle-arrow-left"></span> 
            </button>
        </div>
        <div class="col-md-10">
           
            <div id="energychart" style="height:300px;"></div>
        </div>
        <div class="col-md-1" style="height:300px; margin-top:130px;">
            <button id="later" type="button" class="btn btn-primary"> 
                <span class="glyphicon glyphicon-circle-arrow-right"></span> 
            </button>
        </div>
    </div>
  </div>
  <div class="tab-pane" id="raw">
    <table class="table table-bordered">
        <thead>
            <tr>
                <th>raw</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>{{data}}</td>
            </tr>
        </tbody>
    </table>  
  </div>
</div>

<script>
  $('#myTab a').click(function (e) {
    e.preventDefault()
    $(this).tab('show')
  })
</script>

<script type="text/javascript">
	$(function() {
	    readings = {}
	    series = [];
	    latest = 0;
	    earliest = Number.MAX_VALUE;
	    index = 0;
	    latestmax = 0;
	    requesting = false;
	    historyindex = 0;
	    
	    function update(data, shift){
	        
	        shift = typeof shift != 'undefined' ? shift: false;
	        
	        $.each(data, function(i, reading){
                var rgx = new RegExp("\/", 'g');
                da = reading.ts.replace(rgx, ":").split(":");
                d = new Date(da[0], da[1]-1, da[2], da[3], da[4], da[5]).getTime();    
                a = readings[reading.sensorId] || [];
                
                if (a.length > 1 && shift){
	                a.slice(1);
	            }
                if (latest < d){
                    latest = d;
                    //$("span.to").html(reading.ts); 
                }
                if (earliest > d){
                    earliest = d;
                    //$("span.from").html(reading.ts); 
                }
                //latestmax = Math.max(latest, latestmax);
                a.push([d, reading.watts]);
                readings[reading.sensorId] = a;
	        });
	         ld = new Date(latest);
	         ed = new Date(earliest);
	         $("span.to").html(ld.toDateString() + " " + ld.toLocaleTimeString()); 
	         $("span.from").html(ed.toDateString() + " " + ed.toLocaleTimeString()); 
	    }
	
	    update({{!data}});
	    
	    for(var key in readings){
	        series.push({'label':key,data:readings[key]})
	    }
	    
	    var plot = $.plot("#energychart", series,  {
	        xaxis:{mode:"time", timezone: "browser" }
	    });
	    
	    
	    $("#earlier").click(function(){
	        
	        
	        to          = earliest; 
	        from        = earliest - 10*60*1000;      
	        
	        console.log("earlier has been clicked, calling from " + from + " to " + to);
	        
	        fetch({ 
	                from:from, 
	                to: to,
	                success: function(data){
	                    if (data.length > 0){
	                        earliest = from;
	                        latest = to; 
	                        index-=1;
	                    }
	                    console.log("index is " + index);
	                }
	            }
	         );   
	    });
	    
	     $("#later").click(function(){
	    
	        if (index >= 0){
	            return;
	        }
	        
	        //if (latest <= 0)
	          //  latest = earliest;
	            
	        //if (latestmax > latest){   
	            from        = latest;  
                to          = latest + (10*60*1000); 
	            
	            fetch({
	                    from:from,
	                    to:to, 
	                    success:function(data){
	                        if (data.length > 0){
                                index += 1;
                                earliest  = from;
                                latest    = to;   
                                console.log("index is " + index); 
                            }       
	                    }
	            });   
	        //}
	    });
	    
	    fetch = function(options){
	        
	        if (requesting)
	            return;
	        requesting = true;
	        
	        data = {};
	            
	        if (options.from)
	            data['from'] = from/1000;
	            
	        if (options.to){
	            data['to'] = to/1000;
	        }
	         
	        $.ajax({
                    url: "/summary",
                    dataType: 'json', 
                    data: data,
                    timeout: 30000,
                    cache: false,
                    
                    success: function(data) {
                        
                        if (options.success){
                            options.success(data);
                        }  
                        
                        if (data && data.length > 0){
                            readings = {}
                            series = []; 
                            update(data);
                           
                            for(var key in readings){
                                series.push({'label':key,data:readings[key]})
                            }
    
                            plot = $.plot("#energychart", series,  {
                                xaxis:{mode:"time", timezone: "browser" }
                            });     
                        }
                    },
                    
                    
                    error: function(XMLHttpRequest, textStatus, errorThrown){
                       
                    },
                     
                    complete: function(XMLHttpRequest, textStatus){
                        requesting = false;
                    }
                });     
	    }
	    
        startpolling = function(frequency){
        
            setTimeout(function(){   
                  
                if (index != 0){
                    startpolling(frequency);    
                    return;
                }
                   
                $.ajax({
                    url: "/summary",
                    data: {from: (latest/1000)},
                    dataType: 'json', 
                    timeout: 30000,
                    cache: false,
                    
                    success: function(data) {   
                        if (index == 0){
                            update(data,true);
                            plot.setData(series);
	                        plot.setupGrid();
	                        plot.draw();
	                    }
	                },
                     
                    error: function(XMLHttpRequest, textStatus, errorThrown){
                       
                        switch(XMLHttpRequest.status){
                            case 0: //update server is down
                                frequency = 15000;
                                break;
                            case 502: //update server is down
				                frequency = 15000;
				                break;
				            case 500: //server error
				                frequency = 15000;
				                break;
                            case 403: //forbidden - unlikely to get access anytime soon
                                frequency = 60000;
                                break; 
                            default:
                                frequency = 2000;
                        }
                    },
                    
                    complete: function(){
                        startpolling(frequency);        
                    }
                });
            
            },frequency);
        }	  
        
	    startpolling(2000);
	});
</script>

<script type="text/javascript" src="./static/flot/jquery.flot.js"></script>
<script type="text/javascript" src="./static/flot/jquery.flot.time.js"></script>