<html>
<head>
<title>Prefstore - Word Cloud</title>

<link rel="stylesheet" type="text/css" href="./static/jqcloud.css" /> 
<link rel="stylesheet" type="text/css" href="./static/layout.css" /> 

<script type="text/javascript" src="./static/jquery-1.6.min.js"></script> 
<script type="text/javascript" src="./static/jqcloud-0.2.4.js"></script> 
<script type="text/javascript" src="http://www.google.com/jsapi"></script>

<script type="text/javascript">

	score_positions = {{ score_positions }}
	start = 0;
	next_div = 0;
	gap = 87

	$( document ).ready( function() {
		arrange_by_time();
	});

	function arrange_by_time() {
		start = $( "#box" ).position().top;
		for ( i = 0; i < score_positions.length; i++ ) {
			d = $( "#" + i )
			target = start + (  i * gap );
			d.animate( { 'top': target }, 300 );
		}
	}

	function arrange_by_score() {
		console.log( score_positions )
		start = $( "#box" ).position().top;
		for ( i = 0; i < score_positions.length; i++ ) {
			d = $( "#" + score_positions[ i ] )
			target = start + ( i * gap );
			d.animate( { 'top': target }, 1000 );
		}
	}


</script>

<style>
	.news_item {
		border-bottom:1px dotted gray; 
		width:650px;
		height:77px;
		position:absolute;

	}

	.news_box {
		padding-top:3px;
		margin-left:105px;
		border:0px solid;
	}

	.news_title {
		font-family:georgia;
		font-weight:bold;
		size:14px;
		color:#257dad;
		overflow:hidden;
		height:17px;
	}

	.news_time {
		margin-top:5px;
		font-family:arial;
		font-weight:none;
		font-size:11px;
		color:#257dad;
	}

	.news_blurb {
		margin-top:5px;
		font-size:11px;
		height:30px;
		overflow:hidden;
		color:gray;
	}

	.menu_item {
		float: right;
		width: 175px;
		height: 60px;
		text-align: left;
		padding-top: 30px;
		padding-left: 20px;
		padding-right: 20px;
		font-family: georgia;
		line-height: 120%;
	}

</style>

</head>


<body>
<div class="top">
	<div class="header">
		<div class="logo">
			<img src="./static/pslogofull.png"/>
		</div>
		
		%if user:
		<div id="logout" class="menu_item">
			News items for:<br/>
			<span class="top-menu-item"> {{ user["user_name"]}}</span>
		</div>
	</div>

	<!---------------------------------------------------------------- 
		CONTENT SECTION
	------------------------------------------------------------------>
	<div class="main" style="height:1000px; border 1px solid blue;">
		<a href="javascript:arrange_by_time()">most recent</a> | <a href="javascript:arrange_by_score()">prefstore scores</a>
		<br/><br/>
		<div id="box" style="margin:0px; padding 0px; float: left;">
			%import time
			%for i in range( len( stories ) ):
			<div id="{{ i }}" class="news_item">
				<div style="float:left; width:100px;">
					<span style="font-style:italic">{{ stories[ i ].get( "media" )[ stories[ i ].get( "media" ).rfind("/")+1:] }}</span><br/>
					<a href="{{ stories[ i ].get( 'link' ) }}" ><img src="./static/{{ stories[ i ].get( "media" )[ stories[ i ].get( "media" ).rfind("/")+1:] }}.jpg" style="height:60; border: 0px;"/></a>
				</div>
				<div class= "news_box">
					<div class="news_title">
						{{ stories[ i ].get( "title" )}}
					</div>
					<div class="news_blurb">{{ stories[ i ].get( "description" ) }}</div>
					<div class="news_time">
						{{ time.strftime( "%d %b %H:%M", time.gmtime( stories[ i ].get( "pubDate" ) ) ) }}
						<i>(score of {{ round( stories[ i ].get( "score" ) * 100, 2 ) }}%)</i> 
					</div>
				</div>
			</div>
			%end
		</div>
		<div style="margin-left:750px; font-size:12px; font-family: arial; ">
			<div class="news_title">average scores/category:</div>
			%for s in summary:
				<div style="margin-top:6px; border-bottom:1px dotted #aaaaaa">
					<div style="float:left; padding:4px; color:#7777aa; font-weight:bold;">
						yahoo {{ s[ "media" ][ s[ "media" ].rfind("/")+1:] }}:
					</div>
					<div style="margin-left:150px;  background-color:#f7f7ff; padding:4px; font-style:italic">
						{{ round( s[ "average" ] * 100, 2 ) }}%
					</div>
				</div>
			%end

		</div>
	</div>

<!-- FOOTER ------------------------------------------------------------------>

