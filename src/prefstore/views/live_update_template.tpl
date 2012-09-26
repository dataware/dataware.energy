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
</div>


<script>
    $('#myTab a').click(function (e) {
        e.preventDefault();
        $(this).tab('show');
    });
    
   
    
</script>

<script>

  var t = 1297110663, v = 70; // start time (seconds since epoch)
  function UrlModel() {
        this.urls = ko.observableArray([{time: t++, value: v = ~~Math.max(10, Math.min(90, v + 10 * (Math.random() - .5)))}]); 
  }
   
  urls = new UrlModel();
  ko.applyBindings(urls);
  var data = urls.urls();
  
  //d3.range(33).map(next); // starting dataset
  
  console.log(urls);
   
  function next() {
    return {
      time: ++t,
      value: v = ~~Math.max(10, Math.min(90, v + 10 * (Math.random() - .5)))
    };
  }

  setInterval(function() {
    //data.shift();
    data.push(next());
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
     .attr("width", w * 30)
     .attr("height", h);

  chart.selectAll("rect")
     .data(data)
     .enter().append("rect")
     .attr("x", function(d, i) { return x(i) - .5; })
     .attr("y", function(d) { return h - y(d.value) - .5; })
     .attr("width", w)
     .attr("height", function(d) { return y(d.value); });


  function redraw(){
   chart.selectAll("rect")
     .data(data)
     .enter().append("rect")
     .attr("x", function(d, i) { return x(i) - .5; })
     .attr("y", function(d) { return h - y(d.value) - .5; })
     .attr("width", w)
     .attr("height", function(d) { return y(d.value); });
  
/*    chart.selectAll("rect")
    .data(data)
    .transition()
    .duration(1000)
    .attr("y", function(d) { return h - y(d.value) - .5; })
    .attr("height", function(d) { return y(d.value); });*/
  }

</script>

<!-- FOOTER ------------------------------------------------------------------>
%include footer