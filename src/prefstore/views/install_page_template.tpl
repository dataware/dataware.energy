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

	function install_resource() {
		$.ajax({
			type: 'GET',
			url: '/install_request?catalog_uri=' +  $("#catalog_uri").val(),
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

<div class="sub_header">
	<div class="page-name">DATAWARE CATALOG INSTALLTION</div>
	<div class="page-description">WE JUST NEED TO KNOW YOUR CATALOG ADDRESS...</div>
</div>


<!---------------------------------------------------------------- 
	CONTENT SECTION
------------------------------------------------------------------>
<div class="main">

	<div style="margin:25px auto; padding:15px; border:1px dotted #cccccc; width:400px; height:185px;">
		<div> 
			<img src="./static/dwlogofull.png" width="220px"/>
		</div>
		<div style="text-align:left; font-style:italic; font-family:georgia; font-size:12px; color: #888888; margin:10px 0px 18px 7px;">
			In order to install your prefstore as an app in your Dataware Catalog, please
			supply the address of your catalog:
		</div>
		<div id="loggedOutBox" >
        <form action="javascript:install_resource()">
			<div style="padding:0 10 0 8; float:left; border:0px dotted; font-size:12px; font-family:georgia; color:#555555;">
	            
	            <div style="margin-top:5px;">
					Catalog URI:
				</div>
		        <div >
			        <input id="catalog_uri" class="text" name="catalog_uri" type="text" size="42" />
					<input type="submit" value="Install >>" style="float:bottom; " />
				</div>
			</div>
				

			
			<input type="hidden" name="submission" value="True" />
		</form>
		</div>
	</div>	
</div>

<!-- FOOTER ------------------------------------------------------------------>
%include footer