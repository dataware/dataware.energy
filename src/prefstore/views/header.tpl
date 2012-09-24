<html>
<head>
<title>My dataware resources</title>

<link rel="stylesheet" type="text/css" href="./static/bootstrap/css/bootstrap.min.css" /> 
<link rel="stylesheet" type="text/css" href="./static/jqcloud.css" />
<script type="text/javascript" src="./static/jquery/jquery-1.8.2.min.js"></script>
<script type="text/javascript" src="./static/jquery/jquery-ui-1.8.23.min.js"></script>
<script type="text/javascript" src="./static/bootstrap/js/bootstrap.min.js"></script>

<script type="text/javascript" src="./static/jqcloud/jqcloud-1.0.1.min.js"></script> 
<script type="text/javascript" src="http://www.google.com/jsapi"></script>


<script>

	PREFSTORE = "http://hwresource.block49.net:9000/" 
	 
	$( document ).ready( function() {
		$( 'a.menu_button' ).click( function() {
			self.parent.location= PREFSTORE + $( this ).attr('id');
		});
	});
</script>

</head>

<body>
<div class="navbar">
    <div class="navbar-inner">
        <a class="brand" href="#">My dataware resources</a>
        <ul class="nav">
            <li><a href="#" class="menu_button" id="home">home</a></li>
            <li><a href="#" class="menu_button" id="summary">summary</a></li>
            
            %if user:
            <li><a href="#" class="menu_button" id="logout">logout</a></li>
            %else:
            <li><a href="#" class="menu_button" id="login">login/register</a></li>
            %end
        </ul>
    </div>
</div>