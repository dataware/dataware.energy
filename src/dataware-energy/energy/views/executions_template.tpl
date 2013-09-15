<!-- HEADER ------------------------------------------------------------------>
%include header user=user
<script>
$(function(){
   
    var em = new ExecutionModel();
    em.loadData({{!executions}}); //this needs to be an ajax call to ensure liveness.
    ko.applyBindings(em, $(".myexecutions")[0]);
});


</script>

<div class="container">
    <div class="myexecutions">
        <div class="row">
            <div class="span12">
                <table class="table table-condensed table-striped table-bordered">
                    <thead>
                        <tr>
                            <th>Query</th>
                            <th>Resource</th>
                            <th>Execution time</th>
                            <th>View on client</th>
                        </tr>   
                    </thead>                
                    <tbody data-bind='{ foreach: executions}'>
                        <tr>
                            <td data-bind="text:query"></td>
                            <td width="150"><span data-bind="text:resource_name"></span></td>  
                            <td width="150"><span data-bind="text:executed"></span></td>
                            <td width="150">
                                <form data-bind="attr:{action:client_view_url}" method=post>
                                    <input type="hidden" name="processor_id" data-bind="value:processor_id">
                                    <button class="btn btn-primary" type="submit">View!</button>
                                </form>
                            </td>   
                        </tr>   
                    </tbody>
                </table> 
            </div>
        </div>
    </div>
</div>
%include footer
 