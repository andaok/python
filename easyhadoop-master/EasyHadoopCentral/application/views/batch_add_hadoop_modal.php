<style type="text/css">
#error_batch_rack
{
	padding-left:15px;
	color:Red;
}
</style>

<div id="batch_add_hadoop_node" class="modal hide fade" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
<form action="<?php echo $this->config->base_url();?>index.php/manage/batchaddhadoopnode/" method="POST">
	<div class="modal-header">
		<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
		<h3 id="myModalLabel"><?php echo $common_add_node?></h3>
	</div>
	<div class="modal-body">
		<div class="alert alert-error"><?php echo $common_add_node_tips?></div>
		<table>
			<tr>
				<td>
				<label><?php echo $common_ip_addr;?></label><textarea name="ipaddr"></textarea><br />
				</td>
				<td>
				Each IP address per line
				</td>
			</tr>
		</table>
		<table>
			<tr>
				<td><label><?php echo $common_root_user;?></label><input type="text" name="ssh_user" value="root" disabled />
				<input type="hidden" name="ssh_user" value="root" />
				</td>
				<td><label><?php echo $common_root_pass;?></label><input type="text" name="ssh_pass" placeholder="ssh_pass" />
				</td>
			</tr>
			<tr>
				<td>
				<label><?php echo $common_role_name;?></label>
				</td>
				<td>
					<label><?php echo $common_rackaware_position;?></label>
				</td>
			</tr>
			<tr>
				<td>
					<input type="checkbox"  name="role[]" value="namenode" />Namenode<br />
					<input type="checkbox"  name="role[]" value="datanode" />Datanode<br />
					<input type="checkbox"  name="role[]" value="secondarynamenode" />SecondaryNamenode<br />
					<input type="checkbox"  name="role[]" value="jobtracker" />Jobtracker<br />
					<input type="checkbox"  name="role[]" value="tasktracker" />Tasktracker<br />
				</td>
				<td>
					<input type="text" name="rack" id="rack" placeholder="Rack number" /><br />
					<span id="error_batch_rack"><?php echo "Need numeric";?></span>
					<script type="text/javascript">
					$(document).ready(function () {
						$("#error_batch_rack").hide();
							$("#rack").blur(function () {
								var $val = $("#rack").val();
								var code;
								for (var i = 0; i < $val.length; i++) {
								var code = $val.charAt(i).charCodeAt(0);
								if (code < 48 || code > 57) {
									$("#error_batch_rack").show();
									break;
								}
								else {
									$("#error_batch_rack").hide();
								}
							}
						});
					});
					</script>
				</td>
			</tr>
		</table>
	</div>
	<div class="modal-footer">
		<button class="btn" data-dismiss="modal"><?php echo $common_close;?></button>
		<button type="submit" class="btn btn-primary"><?php echo $common_submit;?></button>
	</div>
</form>
</div>