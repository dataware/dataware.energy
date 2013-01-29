<!-- HEADER ------------------------------------------------------------------>
%include header user=user

<script>
$(function(){
    var rm = new ResourceModel();
    rm.loadResources({{!resources}});
    ko.applyBindings(rm, $(".mydata")[0]);
})
</script>

<div class="container">

    <div class="well">
        <h1>Welcome to the resource manager.<small> Browse and manage your data resources </small></h1>
    </div>
    
    %if user:
    <div class="mydata">       
		<ul class="nav nav-pills" id="myTab" data-bind="foreach:resources">
            <li data-bind="css:{active: $parent.selectedResource().resource_name() == resource_name()}">
                <a data-bind="attr:{href: '#' + resource_name()}, click:function(){$parent.selectedResource($data);}, text:resource_name"></a>
            </li>
        </ul>
        <div class="row">
            <div class="span10">
                <h3 data-bind="text:selectedResource().resource_name()"></h3>
        
                <p> Some sort of view of user <span data-bind="text:selectedResource().resource_name()"></span> data</p>
               
                <!-- pull in view of the data dynamically here -->
                
                <div data-bind="if: selectedResource().installed() == 0">
                    <a  data-bind="attr:{href:selectedResource().install_url}">Share your data</a>
                </div>
            
                <div data-bind="if: selectedResource().installed() == 1">
                    %for catalog in installs:
                        <a href="{{catalog}}">{{catalog}}</a>
                    %end  
                </div>
             </div>
        </div>
    </div>
	%end
</div>


<script>
    $('#myTab a').click(function (e) {
        e.preventDefault();
        $(this).tab('show');
    });
</script>

<!--<script type="text/javascript">

      /*$('#details').hide();*/
     
      function wordclicked(url){
        //urlModel.selectedUrl(url);
        console.log(url);
        console.log(url.macaddrs);
       // $('#details').show().effect('bounce', {times: 4}, 300);
      }
    
      $("#example").jQCloud({{!urls}});
</script>-->
<!-- FOOTER ------------------------------------------------------------------>
%include footer