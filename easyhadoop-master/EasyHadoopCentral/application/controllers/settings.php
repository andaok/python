<?php

class Settings extends CI_Controller
{

	public function __construct()
	{
		parent::__construct();
		if(!$this->session->userdata('login') || $this->session->userdata('login') == FALSE)
		{
			redirect($this->config->base_url() . 'index.php/user/login/');
		}
	}

	public function Index()
	{
		#Generate header
		$this->lang->load('commons');
		$data['common_lang_set'] = $this->lang->line('common_lang_set');
		$data['common_title'] = $this->lang->line('common_title');
		$this->load->view('header',$data);
		
		#generate navigation bar
		$data['common_index_page'] = $this->lang->line('common_index_page');
		$data['common_node_manager'] = $this->lang->line('common_node_manager');
		$data['common_node_monitor'] = $this->lang->line('common_node_monitor');
		$data['common_install'] = $this->lang->line('common_install');
		$data['common_host_settings'] = $this->lang->line('common_host_settings');
		$data['common_node_operate'] = $this->lang->line('common_node_operate');
		$data['common_user_admin'] = $this->lang->line('common_user_admin');
		$data['common_log_out'] = $this->lang->line('common_log_out');
		$data['common_hadoop_node_operate'] = $this->lang->line('common_hadoop_node_operate');
		$data['common_hbase_node_operate'] = $this->lang->line('common_hbase_node_operate');
		$data['common_hadoop_host_settings'] = $this->lang->line('common_hadoop_host_settings');
		$data['common_hbase_host_settings'] = $this->lang->line('common_hbase_host_settings');
		$data['common_install_hadoop'] = $this->lang->line('common_install_hadoop');
		$data['common_install_hbase'] = $this->lang->line('common_install_hbase');
		$data['common_hdfs_manage'] = $this->lang->line('common_hdfs_manage');
		$this->load->view('nav_bar', $data);
		
		$this->load->view('div_fluid');
		$this->load->view('div_row_fluid');
		
		$data['common_hadoop_settings'] = $this->lang->line('common_hadoop_settings');
		
		$this->load->view('ehm_hosts_settings_nav', $data);
		
		$data['common_hostname'] = $this->lang->line('common_hostname');
		$data['common_ip_addr'] = $this->lang->line('common_ip_addr');
		$data['common_node_role'] = $this->lang->line('common_node_role');
		$data['common_create_time'] = $this->lang->line('common_create_time');
		$data['common_action'] = $this->lang->line('common_action');
		
		$data['common_golbal_settings'] = $this->lang->line('common_golbal_settings');
		$data['common_node_settings'] = $this->lang->line('common_node_settings');
		$data['common_gs_comment'] = $this->lang->line('common_gs_comment');
		$data['common_ns_comment'] = $this->lang->line('common_ns_comment');
		$data['common_ns_manage'] = $this->lang->line('common_ns_manage');
		$data['common_gs_manage'] = $this->lang->line('common_gs_manage');
		$data['common_setting_generate_tool'] = $this->lang->line('common_setting_generate_tool');
		$data['common_push_global_settings'] = $this->lang->line('common_push_global_settings');
		$data['common_push_node_settings'] = $this->lang->line('common_push_node_settings');
		$data['common_add_gs_settings'] = $this->lang->line('common_add_gs_settings');
		$data['common_add_ns_settings'] = $this->lang->line('common_add_ns_settings');
		$data['common_view_rackaware'] = $this->lang->line('common_view_rackaware');
		$data['common_rackaware'] = $this->lang->line('common_rackaware');
		$data['common_push_rackaware'] = $this->lang->line('common_push_rackaware');
		$data['common_view_hosts'] = $this->lang->line('common_view_hosts');
		$data['common_push_hosts'] = $this->lang->line('common_push_hosts');
		$data['common_edit_time'] = $this->lang->line('common_edit_time');
		$data['common_close'] = $this->lang->line('common_close');
		$data['common_edit'] = $this->lang->line('common_edit');
		$data['common_remove'] = $this->lang->line('common_remove');
		$data['common_modify_settings'] = $this->lang->line('common_modify_settings');
		$data['common_remove_settings'] = $this->lang->line('common_remove_settings');
		
		#generate settings lists
		$this->load->model('ehm_settings_model','sets');
		$this->load->model('ehm_hosts_model', 'hosts');
		$data['result_general'] = $this->sets->get_general_settings_list();
		$data['all_hosts'] = $this->hosts->get_all_hosts();
		
		$data['common_submit'] = $this->lang->line('common_submit');
		$data['common_global_setting_tips'] = $this->lang->line('common_global_setting_tips');
		$data['common_node_setting_tips'] = $this->lang->line('common_node_setting_tips');
		$data['common_add_settings'] = $this->lang->line('common_add_settings');
		$data['common_filename'] = $this->lang->line('common_filename');
		$data['common_content'] = $this->lang->line('common_content');
		$data['common_close'] = $this->lang->line('common_close');
		
		#generate node setting tab
		$this->load->model('ehm_settings_model','sets');
		$this->load->library('pagination');
		$config['base_url'] = $this->config->base_url() . 'index.php/settings/index/';
		$config['total_rows'] = $this->sets->count_node_settings();
		$config['per_page'] = 20;
		$offset = $this->uri->segment(3,0);
		if($offset == 0):
			$offset = 0;
		else:
			$offset = ($offset / $config['per_page']) * $config['per_page'];
		endif;
		$this->pagination->initialize($config);
		$data['pagination'] = $this->pagination->create_links();
		$data['result_node'] = $this->sets->get_node_settings_list($config['per_page'], $offset);
		
		
		$this->load->view('ehm_hosts_settings_list', $data);
		
		$this->load->view('view_etc_hosts_modal',$data);
		$this->load->view('add_general_settings_modal',$data);
		$this->load->view('add_node_settings_modal',$data);
		$this->load->view('push_etc_hosts_modal', $data);
		$this->load->view('push_general_settings_modal', $data);
		$this->load->view('view_rackaware_modal', $data);
		$this->load->view('push_rackaware_modal', $data);
		$this->load->view('push_node_settings_modal', $data);
		
		$this->load->view('div_end');
		$this->load->view('div_end');
		
		#generaet footer
		$this->load->view('footer', $data);
	}
	
	public function HadoopSettings()
	{
		#Generate header
		$this->lang->load('commons');
		$data['common_lang_set'] = $this->lang->line('common_lang_set');
		$data['common_title'] = $this->lang->line('common_title');
		$this->load->view('header',$data);
		
		#generate navigation bar
		$data['common_index_page'] = $this->lang->line('common_index_page');
		$data['common_node_manager'] = $this->lang->line('common_node_manager');
		$data['common_node_monitor'] = $this->lang->line('common_node_monitor');
		$data['common_install'] = $this->lang->line('common_install');
		$data['common_host_settings'] = $this->lang->line('common_host_settings');
		$data['common_node_operate'] = $this->lang->line('common_node_operate');
		$data['common_user_admin'] = $this->lang->line('common_user_admin');
		$data['common_log_out'] = $this->lang->line('common_log_out');
		$data['common_hadoop_node_operate'] = $this->lang->line('common_hadoop_node_operate');
		$data['common_hbase_node_operate'] = $this->lang->line('common_hbase_node_operate');
		$data['common_hadoop_host_settings'] = $this->lang->line('common_hadoop_host_settings');
		$data['common_hbase_host_settings'] = $this->lang->line('common_hbase_host_settings');
		$data['common_install_hadoop'] = $this->lang->line('common_install_hadoop');
		$data['common_install_hbase'] = $this->lang->line('common_install_hbase');
		$data['common_hdfs_manage'] = $this->lang->line('common_hdfs_manage');
		$this->load->view('nav_bar', $data);
		
		$this->load->view('div_fluid');
		$this->load->view('div_row_fluid');
		
		$data['common_hadoop_settings'] = $this->lang->line('common_hadoop_settings');
		
		$this->load->view('ehm_hosts_settings_nav', $data);
		
		$data['common_hostname'] = $this->lang->line('common_hostname');
		$data['common_ip_addr'] = $this->lang->line('common_ip_addr');
		$data['common_node_role'] = $this->lang->line('common_node_role');
		$data['common_create_time'] = $this->lang->line('common_create_time');
		$data['common_action'] = $this->lang->line('common_action');
		$data['common_add_settings'] = $this->lang->line('common_add_settings');
		$data['common_filename'] = $this->lang->line('common_filename');
		$data['common_content'] = $this->lang->line('common_content');
		$data['common_close'] = $this->lang->line('common_close');
		
		#generate settings lists
		$this->load->model('ehm_settings_model', 'sets');
		$category = $this->sets->get_hadoop_settings_category();
		$data['category'] = $category;
		
		$this->load->view('hadoop_settings_collapse',$data);
		
		$this->load->view('div_end');
		$this->load->view('div_end');
		
		#generaet footer
		$this->load->view('footer', $data);
	}
	
	public function UpdateGeneralSettings()
	{
		$set_id = $this->input->post('set_id');
		$filename = $this->input->post('filename');
		$content = $this->input->post('content');
		$ip = "0";
		
		$this->load->model('ehm_settings_model', 'sets');
		$this->sets->update_settings($set_id, $filename, $content, $ip);
		
		redirect($this->config->base_url() . 'index.php/settings/index/');
	}
	
	public function DeleteSettings()
	{
		$set_id = $this->input->post('set_id');
		$this->load->model('ehm_settings_model', 'sets');
		$this->sets->delete_settings($set_id);
		
		redirect($this->config->base_url() . 'index.php/settings/index/');
	}
	
	public function UpdateNodeSettings()
	{
		$set_id = $this->input->post('set_id');
		$filename = $this->input->post('filename');
		$content = $this->input->post('content');
		$ip = $this->input->post('ip');
		
		$this->load->model('ehm_settings_model', 'sets');
		$this->sets->update_settings($set_id, $filename, $content, $ip);
		
		redirect($this->config->base_url() . 'index.php/settings/index/');
	}
	
	public function ViewHosts()
	{
		$this->load->model('ehm_settings_model', 'sets');
		$str = $this->sets->get_etc_hosts_list();
		$str = str_replace("\n", '<br />', $str);
		echo  $str;
	}
	
	public function ViewSettings()
	{
		$this->load->model('ehm_settings_model', 'sets');
		$set_id = $this->uri->segment(3,0);
		
		$result = $this->sets->get_settings_by_id($set_id);
		$data['result'] = $result;
	}
	
	public function AddSettings()
	{
		$filename = $this->input->post('filename');
		$content = $this->input->post('content');
		$ip = $this->input->post('ip');
		
		$this->load->model('ehm_settings_model', 'sets');
		$this->sets->insert_settings($filename, $content, $ip);
		
		redirect($this->config->base_url() . 'index.php/settings/index/');
	}
	
	public function PushEtcHost()
	{
		$host_id = $this->uri->segment(3,0);
		$this->load->model('ehm_hosts_model', 'hosts');
		$result = $this->hosts->get_host_by_host_id($host_id);
		$ip = $result->ip;
		
		$this->load->model('ehm_settings_model', 'sets');
		$str = $this->sets->get_etc_hosts_list();
		
		$this->load->model('ehm_installation_model', 'install');
		echo $this->install->push_files($ip, '/etc/hosts', $str); #full path of /etc/hosts
	}
	
	public function PushGeneralSettings()
	{
		$host_id = $this->uri->segment(3,0);
		$set_id = $this->uri->segment(4,0);
		$this->load->model('ehm_hosts_model', 'hosts');
		$result = $this->hosts->get_host_by_host_id($host_id);
		$ip = $result->ip;
		
		$this->load->model('ehm_settings_model', 'sets');
		$result = $this->sets->get_settings_by_id($set_id);
		$set_id = $result->set_id;
		$filename = $result->filename;
		$content = $result->content;
		
		$this->load->model('ehm_installation_model', 'install');
		echo $this->install->push_setting_files($ip, $this->config->item('conf_folder') . $filename, $content);#full path of hadoop setting file
	}
	
	public function PushNodeSettings()
	{
		$set_id = $this->uri->segment(3,0);
		$this->load->model('ehm_settings_model', 'sets');
		$result = $this->sets->get_settings_by_id($set_id);
		$ip = $result->ip;
		$content = $result->content;
		$filename = $result->filename;
		
		$this->load->model('ehm_installation_model', 'install');
		echo $this->install->push_setting_files($ip, $this->config->item('conf_folder') . $filename, $content);
	}
	
	public function ViewRackAware()
	{
		$this->load->model('ehm_hosts_model', 'hosts');
		$rack = $this->hosts->make_rackaware();
		$str = str_replace("\n","<br />", $rack['content']);
		$str = str_replace("\t","&nbsp;&nbsp;&nbsp;&nbsp;",$str);
		echo $str;
	}
	
	public function PushRackAware()
	{
		$this->load->model('ehm_hosts_model', 'hosts');
		$result = $this->hosts->get_jobtracker_list();
		$result = $result[0];
		$ip = $result->ip;
		$rack = $this->hosts->make_rackaware();
		$this->load->model('ehm_installation_model', 'install');
		echo $this->install->push_rackaware($ip, $rack);
	}
	
	public function GenerateSettings()
	{
		$name = $this->input->post('name');
		$value = $this->input->post('value');
		$desc = $this->input->post('desc');
		$filename = $this->input->post('filename');
		
		$this->load->model('ehm_auxiliary_model', 'aux');
		$setting = $this->aux->generate_settings($name, $value, $desc, $filename);
		
		#Generate header
		$this->lang->load('commons');
		$data['common_lang_set'] = $this->lang->line('common_lang_set');
		$data['common_title'] = $this->lang->line('common_title');
		$this->load->view('header',$data);
		
		$filename = $setting['filename'];
		
		$xml = str_replace(">","&gt;", str_replace("<", "&lt;",$setting['xml']));
		$xml = str_replace(" ","&nbsp;", str_replace("\n","<br>\n",$xml));
		
		$data['filename'] = $filename;
		$data['xml'] = $xml;
		$this->load->view('view_generated_settings', $data);
		
		#generaet footer
		$this->load->view('footer', $data);
	}

}

?>