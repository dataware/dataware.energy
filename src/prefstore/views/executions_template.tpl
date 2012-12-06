<!-- HEADER ------------------------------------------------------------------>
%include header user=user

<h1> Executions performed </h1>
 % for execution in executions:
 <form action={{execution['client_view_url']}} method=post>
     <input type="hidden" name="processor_id" value="{{execution['processor_id']}}">
     <div class="row">
        <div class="span2">
            {{execution['processor_id']}}
        </div>
        <div class="span2">
            {{execution['parameters']}}
        </div>
         <div class="span2">
            {{execution['executed']}}
        </div>
        <div class="span2">
            <button class="btn btn-primary" type="submit">View!</button>
        </div>
     </div>
 </form>
 %end
 