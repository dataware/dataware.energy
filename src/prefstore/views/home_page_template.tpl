<!-- HEADER ------------------------------------------------------------------>
%include header user=user

<!---------------------------------------------------------------- 
	PAGE SCRIPTS
------------------------------------------------------------------>
<script type="text/javascript">
</script>


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
		<table class="table table-condensed table-striped table-bordered">
            <thead>
                <tr>
                    <th>Data</th>
                    <th>Summary</th>
                </tr>   
            </thead>                
           
            <tbody>   
                <tr>
                    <td> Urls </td>
                    <td> [some kind of summary] </td>
                </tr>  
                <tr>
                    <td> Energy </td>
                    <td> [some kind of summary] </td>
                </tr>  
            </tbody>
        </table>  
         <a href="install">Share your data</a>
	%end
</div>

<!-- FOOTER ------------------------------------------------------------------>
%include footer