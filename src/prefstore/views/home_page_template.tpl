<!-- HEADER ------------------------------------------------------------------>
%include header user=user

<script>
$(function(){
    var rm = new ResourceModel();
    ko.applyBindings(rm, $(".mydata")[0]);
})
</script>

<div class="container">

    <div class="well">
        <h1>Welcome to the resource manager.<small> Browse and manage your data resources </small></h1>
    </div>

	%if user:
    <div class="mydata">       
		<ul class="nav nav-tabs" id="myTab">
            <li class="active"><a href="#browsing" data-bind="click:function(){selectedResource('urls');}">Browsing</a></li>
            <li><a href="#energy" data-bind="click:function(){selectedResource('energy')}">Energy</a></li>
        </ul>
        
            <div class="tab-content">
                <div class="tab-pane active" id="browsing">
                    <div class="row">
                        <div class="span8">
                            <div id="example" style="width: 550px; height: 350px;"></div>
                        </div>
                        <div data-bind="if:selectedUrl() ">
                            <div class="span4" id="details">
                                <div class="well">
                                    <h4> <span data-bind="text:selectedUrl().url"></h4>
                                    <h4><small><span data-bind="text:requestText()"></small></h4>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="tab-pane" id="energy">
                    <legend> share </legend>
                     <a  data-bind="attr:{href:install_url}">Share your data</a>
                </div>
            </div>
        
            %if installs:
                You are sharing this data with
                 %for catalog in installs:
                    <a href="{{catalog}}">{{catalog}}</a>
                 %end
            %else:
                <a  data-bind="attr:{href:install_url}">Share your data</a>
            %end
	%end
	</div>
</div>


<script>
    $('#myTab a').click(function (e) {
        e.preventDefault();
        $(this).tab('show');
    });
</script>



<script type="text/javascript">


      /*$('#details').hide();*/
     
      function wordclicked(url){
        //urlModel.selectedUrl(url);
        console.log(url);
        console.log(url.macaddrs);
       // $('#details').show().effect('bounce', {times: 4}, 300);
      }
    
      $("#example").jQCloud({{!urls}});
</script>

<!-- FOOTER ------------------------------------------------------------------>
%include footer