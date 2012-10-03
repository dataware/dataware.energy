<!-- HEADER ------------------------------------------------------------------>
%include header user=user

<!---------------------------------------------------------------- 
	PAGE SCRIPTS
------------------------------------------------------------------>
<script type="text/javascript" src="./static/knockout/knockout-2.1.0.js"></script>
<script type="text/javascript" src="./static/d3/d3.min.js"></script>

<style>
  .chart rect {
      fill: steelblue;
      stroke: white;
   }
</style>


<body>

<!---------------------------------------------------------------- 
	HEADER SECTION
------------------------------------------------------------------>

<div class="container">
    <div class="well">
        <h1>Welcome to the resource manager live update</h1>
    </div>
    <a href='#' data-bind="click: function(){addSomeData()}">UPDATE</a>
	<!---------------------------------------------------------------- 
		SUMMARY SECTION
	------------------------------------------------------------------>
	
	
	
    <div id="bar-demo"></div>
    <h1> <span data-bind="text:name"></span></h1>
</div>


<script>
    $('#myTab a').click(function (e) {
        e.preventDefault();
        $(this).tab('show');
    });
    
   
    
</script>

<script>

  var t = 1297110663, v = 70; // start time (seconds since epoch)
  
  function myModel(data) {
        var self = this;
        
        this.black = false;
       
        ko.extenders.logChange = function(target, option){
        
            target.subscribe(function(newValue){
               console.log("option" + ":" + newValue);
            });
            return target;
            
        }
      
        this.hello=function(){console.log("eghehe")};
        
        this.items = ko.observableArray().extend({logChange: "oooh!"});
        
        this.name = ko.observable("Bod").extend({logChange: "first name"});
        
        this.toggleback= function(){
            if (!self.black)
                d3.select("body").transition().style("background-color", "black");
            else
                d3.select("body").transition().style("background-color", "white");
            
            self.black = !self.black;
        }
        //this.items.subscribe(function(x){console.log(x)});
  }
   
  
  mymodel = new myModel();       
  ko.applyBindings(mymodel);
  mymodel.items(d3.range(33).map(next)); // starting dataset
 
   
  console.log(mymodel.items());

  
 
        
  function next() {
   
    return {
      time: ++t,
      value: v = ~~Math.max(10, Math.min(90, v + 10 * (Math.random() - .5)))
    };
  }

  setInterval(function() {
   
    mymodel.items.shift();
    mymodel.items.push(next());
    mymodel.name(t + " hello");  
    redraw();
  }, 1500);


  var w = 20, h = 80;
  
  var x = d3.scale.linear()
     .domain([0, 1])
      .range([0, w]);
  
  var y = d3.scale.linear()
      .domain([0, 100]) 
      .rangeRound([0, h]);

  var chart = d3.select("#bar-demo").append("svg")
     .attr("class", "chart")
     .attr("width", w * 50)
     .attr("height", h);

  chart.selectAll("rect")
     .data(mymodel.items())
     .enter().append("rect")
     .attr("x", function(d, i) { return x(i) - .5; })
     .attr("y", function(d) { return h - y(d.value) - .5; })
     .attr("width", w)
     .attr("height", function(d) { return y(d.value); });

 
  
  function redraw(){
    
    
    //bind the chart to some data
    
    var rect =  chart.selectAll("rect")
                     .data( mymodel.items(), function(d){return d.time;}) //index on timestamp
   
    
    //insert the new data...
    rect.enter()
        .append("rect")
        .on("click", function(d, i){alert('ehllo!' + d + " " + i)})
        .attr("x", function(d, i) { return x(i+1) - .5; })
        .attr("y", function(d) { return h - y(d.value) - .5; })
        .attr("width", w)
        .attr("height", function(d) { return y(d.value); })
        .transition()
        .duration(1000)
        .attr("x", function(d, i) { return x(i) - .5; });
        
    //update current data
    rect.on("click", function(d, i){mymodel.toggleback()})
        .transition()
        .duration(1000)
        .attr("x", function(d, i) { return x(i) - .5; });
        
    //get rid of old items
    rect.exit()
        .remove();
        
    
  }
  
</script>

<!-- FOOTER ------------------------------------------------------------------>
%include footer