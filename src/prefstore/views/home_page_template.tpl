<!-- HEADER ------------------------------------------------------------------>
%include header user=user

<!---------------------------------------------------------------- 
	PAGE SCRIPTS
------------------------------------------------------------------>
<script type="text/javascript" src="./static/knockout/knockout-2.1.0.js"></script>

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
                        <div data-bind="if:selectedUrl()">
                            <div class="span4" id="details">
                                <div class="well">
                                    <h4> <span data-bind="text:selectedUrl().url"></h4>
                                    <h4><small><span data-bind="text:requestText()"></small></h4>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="tab-pane" id="energy">b</div>
            </div>
        
            %if installs:
                You are sharing this data with
                 %for catalog in installs:
                    <a href="{{catalog}}">{{catalog}}</a>
                 %end
            %else:
                <a href="install">Share your data</a>
            %end
	%end
</div>


<script>
    $('#myTab a').click(function (e) {
        e.preventDefault();
        $(this).tab('show');
    });
</script>

<script>
        
    function UrlModel(){
        var self = this;
        this.selectedUrl = ko.observable();
        
        this.requestText = ko.computed(function(){
            if (self.selectedUrl())
                return self.selectedUrl().requests  + " requests";
            return "";
        });
    }
    
    var urlModel = new UrlModel();
    ko.applyBindings(urlModel);

</script>

<script type="text/javascript">


      /*$('#details').hide();*/
     
      function wordclicked(url){
        urlModel.selectedUrl(url);
        console.log(url);
        console.log(url.macaddrs);
       // $('#details').show().effect('bounce', {times: 4}, 300);
      }
    
      $("#example").jQCloud({{!urls}});
</script>


<!-- FOOTER ------------------------------------------------------------------>
%include footer