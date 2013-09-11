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

<div class="sub_header">
	<div class="page-name">SUMMARY</div>
	<div class="page-description">SEE ALL YOUR DETAILS, AND CONNECT TO YOUR DATASPHERE</div>
</div>


<!---------------------------------------------------------------- 
	CONTENT SECTION
------------------------------------------------------------------>
<div class="main">

	<div style="margin:15px auto; font-family:georgia; padding:15px; border:0px dotted #cccccc; width:400px;">
		
		<div class="table_category">
			<div class="table_image">
				<img src="./static/icon_person.png">
			</div>
			<div class="table_content" >
				<div class="table_item">
					<div class="table_field_name">Username:</div>
					<div class="table_field_value">{{user[ "user_name" ]}}</div>
				</div>
				<div class="table_item">
					<div class="table_field_name">Email:</div>
					<div class="table_field_value">{{user[ "email" ]}}</div>
				</div>
				<div class="table_item">
					<div class="table_field_name">Datasphere:</div>
					<div class="table_field_value"><i>unconnected</i></div>
				</div>
			</div>
		</div>

		<div class="table_category">
			<div class="table_image">
				<img src="./static/icon_distill.png" style="width:50px">
			</div>
			<div class="table_content" >
					<div class="table_item">
					<div class="table_field_name">First Registered:</div>
					<div class="table_field_value"> {{user[ "registered_str" ]}} </div>
				</div>

				<div class="table_item">
					<div class="table_field_name">Last Distillation:</div>
					<div class="table_field_value"> {{user[ "last_distill_str" ]}} </div>
				</div>

				<div class="table_item">
					<div class="table_field_name">Total Docs Distilled:</div>
					<div class="table_field_value"> {{user[ "total_documents" ]}} </div>
				</div>
			</div>
		</div>

		<div class="table_category">
			<div class="table_image">
				<img src="./static/icon_cogs.png">
				</div>
			<div class="table_content" >


				<div class="table_item">
					<div class="table_field_name">Unique Terms Seen:</div>
					<div class="table_field_value">
					%if summary:
						{{summary[ "unique_terms"]}} 
					%else:
						<span>0</span>
					%end
					</div>
				</div>

				<div class="table_item">
					<div class="table_field_name">Total Terms Counted:</div>
					<div class="table_field_value"> {{user[ "total_term_appearances"]}} </div>
				</div>

				
				<div class="table_item">
					<div class="table_field_name">Average Terms / Doc:</div>
					<div class="table_field_value"> {{user[ "average_appearances" ]}} </div>
				</div>
			</div>
		</div>
	</div>	
</div>




<!-- FOOTER ------------------------------------------------------------------>
%include footer