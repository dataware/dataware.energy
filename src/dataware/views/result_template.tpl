<!-- HEADER ------------------------------------------------------------------>
%include header user=user

<h1> Execution result </h1>
 <table class="table table-condensed table-striped table-bordered">
    <thead>
        <tr>
            % for key in keys:
            <th>{{key}}</th>
            %end  
        </tr>   
    </thead>                
    <tbody> 
            % for row in result:
            <tr>
             % for key in keys:
               <td>{{row[key]}}</td>
             %end   
            </tr> 
         %end
    </tbody>
</table>  