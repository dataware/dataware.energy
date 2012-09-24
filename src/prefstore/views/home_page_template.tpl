<!-- HEADER ------------------------------------------------------------------>
%include header user=user

<!---------------------------------------------------------------- 
	PAGE SCRIPTS
------------------------------------------------------------------>
<script src="./static/d3/d3.min.js"></script>
<script src="./static/d3/extras/d3.layout.cloud.js"></script>

<body>

<!---------------------------------------------------------------- 
	HEADER SECTION
------------------------------------------------------------------>

<div class="container">
    <div class="well">
        <h1>Welcome to the resource manager.<small> Browse and manage your data resources </small></h1>
    </div>

	<!---------------------------------------------------------------- 
		SUMMARY SECTION
	------------------------------------------------------------------>
	%if user:
	     
        
		<ul class="nav nav-tabs" id="myTab">
            <li class="active"><a href="#browsing">Browsing</a></li>
            <li><a href="#energy">Energy</a></li>
        </ul>
        
            <div class="tab-content">
                <div class="tab-pane active" id="browsing">
                    <div class="row">
                        <div class="span8">
                            <div id="example" style="width: 550px; height: 350px;"></div>
                        </div>
                        <div class="span4" id="details">
                            <div class="well">
                            Some details here about this url - pulled from server!
                            <ul>
                                <li>Owner:</li>
                                <li>Macaddr</li>
                                <li>total number of times browsed</li>
                                <li> A graph of browsing history / popularity? </li>
                            </ul>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="tab-pane" id="energy">b</div>
            </div>
        
   
        <a href="install">Share your data</a>
    
	%end
	
	
	
</div>


<script>
    $('#myTab a').click(function (e) {
    e.preventDefault();
    $(this).tab('show');
    })
    
   

</script>
<script type="text/javascript">
      $('#details').hide();
     
      function wordclicked(url){
        $('#details').show().effect('bounce', {times: 4}, 300);
      }
    
      $("#example").jQCloud({{!urls}});

</script>



<!-- FOOTER ------------------------------------------------------------------>
%include footer