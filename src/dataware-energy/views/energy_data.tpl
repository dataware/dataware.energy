
<span class="from"></span> to <span class="to"></span>

<ul class="nav nav-tabs" id="myTab">
  <li class="active"><a href="#chart">chart</a></li>
  <li><a href="#raw">raw</a></li>
</ul>

<div class="tab-content">
  <div class="tab-pane active" id="chart">
    <div class="row">
        <div class="col-md-12">
            <div id="energychart" style="height:300px;"></div>
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
	   
	    function update(data, shift=false){
	        $.each(data, function(i, reading){
                var rgx = new RegExp("\/", 'g');
                da = reading.ts.replace(rgx, ":").split(":");
                d = new Date(da[0], da[1]-1, da[2], da[3], da[4], da[5]).getTime();    
                a = readings[reading.sensorid] || [];
                
                if (a.length > 1 && shift){
	                a.slice(1);
	            }
                if (latest < d){
                    latest = d;
                    $("span.to").html(reading.ts); 
                }
                if (earliest > d){
                    earliest = d;
                    $("span.from").html(reading.ts); 
                }
            
                a.push([d, reading.watts]);
                readings[reading.sensorid] = a;
	        });
	    }
	
	    update({{!data}});
	    
	    for(var key in readings){
	        series.push({'label':key,data:readings[key]})
	    }
	    
	    var plot = $.plot("#energychart", series,  {
	        xaxis:{mode:"time", timezone: "browser" }
	    });
	    
        startpolling = function(frequency){
        
            console.log("starting polling!")
        
            setTimeout(function(){    
                $.ajax({
                    url: "/summary?from=" + (latest/1000),
                    dataType: 'json', 
                    timeout: 30000,
                    cache: false,
                    
                    success: function(data) {
                        update(data,true);
                        plot.setData(series);
	                    plot.setupGrid();
	                    plot.draw();
                       
                       /* $.each(data, function(i, reading){
	                        var rgx = new RegExp("\/", 'g');
	                        da = reading.ts.replace(rgx, ":").split(":");
	                        d = new Date(da[0], da[1]-1, da[2], da[3], da[4], da[5]).getTime();  
	                        latest = Math.max(latest,d);
	                        a = readings[reading.sensorid] || [];
	                        
	                        if (a.length > 1){
	                            a.slice(1);
	                        }
	                        a.push([d, reading.watts]);
	                        readings[reading.sensorid] = a;
	                    });
                        console.log(data);
                        //series[0].data = series[0].data.slice(1);
	                   // series[0].data.push([lastdate, Math.random() * 300]);
	                     */
                    },
                     
                    error: function(XMLHttpRequest, textStatus, errorThrown){
                       
                        switch(XMLHttpRequest.status){
                            case 0: //update server is down
                                frequency = 15000;
                                break;
                            case 502: //update server is down
				                frequency = 15000;
				                break;
                            case 403: //forbidden - unlikely to get access anytime soon
                                frequency = 60000;
                                break; 
                            default:
                                frequency = 500;
                        }
                    },
                    
                    complete: function(){
                        startpolling(frequency);        
                    }
                });
            
            },frequency);
        }	  
        
	    startpolling(5000);
	});
</script>

<script type="text/javascript" src="./static/flot/jquery.flot.js"></script>
<script type="text/javascript" src="./static/flot/jquery.flot.time.js"></script>