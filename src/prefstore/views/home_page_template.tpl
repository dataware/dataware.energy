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
      
		<ul class="nav nav-pills" data-bind="foreach:resources">
            <li data-bind="css:{active: $parent.selectedResource().resource_name() == resource_name()}">
                <a data-bind="attr:{href: '#' + resource_name()}, click:function(){$parent.selectedResource($data);}, text:resource_name"></a>
            </li>
        </ul>
    
        <div class="row">
            <div class="span10">
                        
                <div data-bind="if: selectedResource().installed() == 0">
                    <div class="alert alert-info">
                        <a data-bind="attr:{href:selectedResource().install_url}">Share your data</a>
                    </div>
                </div>
                

               <div data-bind="if: selectedResource().installed() == 1">
                  <div class="alert alert-success">
                  You are sharing this data with <a data-bind="attr:{href:selectedResource().catalog_uri()}"> <strong> <span data-bind="text:selectedResource().catalog_uri()"></span></strong></a>
                  </div>
               </div>        
             </div>
        </div>
        <div class="row">
            <div class="span10">
                <div class="myview"></div>
            </div>
        </div>
        
    </div>
	%end
</div>

<!-- FOOTER ------------------------------------------------------------------>
%include footer