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
    console.log({{!data}});
	$(function() {
	    d1 = []
	    //d2 = []
	    $.each({{!data}}, function(i, reading){
	        da = reading.ts.replace("\/", ":", "g").split(":");
	        d = new Date(da[0], da[1], da[2], da[3], da[4], da[5]).getTime();
	        d1.push([d, reading.watts]);
	        //d2.push([d, reading.watts * 2]);
	    });
	    $.plot("#energychart", [d1, /*d2*/],  {
	            xaxis:{mode:"time", timezone: "browser" }
	    });
	});
</script>

<script type="text/javascript" src="./static/flot/jquery.flot.js"></script>
<script type="text/javascript" src="./static/flot/jquery.flot.time.js"></script>