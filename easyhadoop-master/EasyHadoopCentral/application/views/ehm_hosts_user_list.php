<div class=span10>
	<div class="container">
		<h2><?php echo $common_change_passwd;?></h2>
		<form class="form-horizontal" method="post" action="<?php echo $this->config->base_url();?>index.php/user/updatepasswordaction/">
		<div class="control-group">
			<label class="control-label"><?php echo $common_current_passwd;?></label>
			<div class="controls">
				<input type="password" name="old_password" placeholder="<?php echo $common_current_passwd;?>">
			</div>
		</div>
		<div class="control-group">
			<label class="control-label"><?php echo $common_input_passwd;?></label>
			<div class="controls">
				<input type="password" name="new_password1" placeholder="<?php echo $common_input_passwd;?>">
			</div>
		</div>
		<div class="control-group">
			<label class="control-label"><?php echo $common_reinput_passwd;?></label>
			<div class="controls">
				<input type="password" name="new_password2" placeholder="<?php echo $common_reinput_passwd;?>">
			</div>
		</div>
		<div class="control-group">
			<div class="controls">
				<input type="submit" class="btn" name="submit"  value="<?php echo $common_submit;?>" />
			</div>
		</div>
		<input type="hidden" name="action" value="ChangePassword" />
		</form>
	</div>
</div>