<!-- HEADER ------------------------------------------------------------------>
%include header user=user

<!---------------------------------------------------------------- 
	PAGE SCRIPTS
------------------------------------------------------------------>
<!-- Include required JS files -->
<script type="text/javascript" src="./static/jquery-1.6.min.js"></script> 
<script type="text/javascript" src="static/jquery-impromptu.3.2.js"></script>

<link href="static/impromptu.css" rel="stylesheet" type="text/css" />

<script type="text/javascript">

	/**
	 * Function that redirects the user to the server's openid login
	 */ 
	function login( provider ) {
		window.open( "login?provider=" + provider, "_self" )
	}


	////////////////////////////////////////////////////

	function install_resource(resource_name) {
		$.ajax({
			type: 'GET',
			url: '/install_request?catalog_uri=' +  $("#catalog_uri").val() + '&resource_name=' + resource_name,
			success: function( data, status  ) {

				data = eval( '(' + data + ')' );
				if ( data.success ) {
					window.location = data.redirect;
				} else {
					error_box( data.error );
				}
			},
			error: function( data, status ) {
				error_box( "We are currently unable to process this installation. Please try again later." );
			}
		});
	}

	////////////////////////////////////////////////////

	function error_box( error ) {
		msg = "<span class='error_box'>ERROR:</span>&nbsp;&nbsp;" + error
		$.prompt( msg,  {  buttons: { Continue: true }, } )
	}

</script>

<!---------------------------------------------------------------- 
	HEADER SECTION
------------------------------------------------------------------>




<!---------------------------------------------------------------- 
	CONTENT SECTION
------------------------------------------------------------------>
<div class="container">
    <div class="row">
        <div class="span12">
            <div class="alert alert-info">
                When you sign up your resource to a catalog, you will be able to share your data with others.  The catalog will provide you with facilities to manage which third parties can access which elements of your data.  If you do not have a catalog set up we'd recommend <a href='http://{{catalog_uri}}'>this one </a>
            </div>
        </div>
    </div>

    <div class="row">
        <div class="span4 offset4 well">
            <legend> Choose a catalog </legend>
            <form action="javascript:install_resource('{{resource_name}}')">
                <input type="hidden" name="submission" value="True" />
                <select name="catalog_uri" class="span4" id="catalog_uri">
                    <option>{{catalog_uri}}</option>
                </select>
                <button class="btn btn-warning" type="submit">Use!</button>
            </form>
        </div>
    </div>
</div>


<!-- FOOTER ------------------------------------------------------------------>
%include footer
