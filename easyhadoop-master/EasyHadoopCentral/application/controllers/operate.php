<?php

class Operate extends CI_Controller
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
		
		$data['common_hadoop_operating'] = $this->lang->line('common_hadoop_operating');
		$data['common_job_operating'] = $this->lang->line('common_job_operating');
		
		$this->load->view('ehm_hosts_operate_nav', $data);
		
		$data['common_hostname'] = $this->lang->line('common_hostname');
		$data['common_ip_addr'] = $this->lang->line('common_ip_addr');
		$data['common_node_role'] = $this->lang->line('common_node_role');
		$data['common_create_time'] = $this->lang->line('common_create_time');
		$data['common_action'] = $this->lang->line('common_action');
		
		$data['common_view_logs'] = $this->lang->line('common_view_logs');
		$data['common_start'] = $this->lang->line('common_start');
		$data['common_stop'] = $this->lang->line('common_stop');
		$data['common_restart'] = $this->lang->line('common_restart');
		$data['common_close'] = $this->lang->line('common_close');
		
		$data['common_input_ip_hostname'] = $this->lang->line('common_input_ip_hostname');
		$data['common_submit_search'] = $this->lang->line('common_submit_search');
		$data['common_view_failed_nodes'] = $this->lang->line('common_view_failed_nodes');
		
		#generate pagination
		$this->load->model('ehm_hosts_model', 'hosts');
		$this->load->library('pagination');
		$config['base_url'] = $this->config->base_url() . 'index.php/operate/index/';
		$config['total_rows'] = $this->hosts->count_hosts($this->input->get('q',""));
		$config['per_page'] = 10;
		if($this->input->get('q',"")!="")
		$config['suffix'] = "?q=".$this->input->get('q',"");
		
		$offset = $this->uri->segment(3,0);
		if($offset == 0):
			$offset = 0;
		else:
			$offset = ($offset / $config['per_page']) * $config['per_page'];
		endif;
		$this->pagination->initialize($config);
		$data['pagination'] = $this->pagination->create_links();
		
		$data['results'] = $this->hosts->get_hosts_list($config['per_page'], $offset,$this->input->get('q',""));
		$data['q']=$this->input->get('q',"");
		
		$this->load->view('ehm_hosts_operate_list',$data);
		$this->load->view('format_namenode_modal', $data);
		
		$this->load->view('div_end');
		$this->load->view('div_end');
		
		#generaet footer
		$this->load->view('footer', $data);		
	}
	public function FailedList()
	{
		#Generate header
		$this->lang->load('commons');
		$data['common_lang_set'] = $this->lang->line('common_lang_set');
		$data['common_title'] = $this->lang->line('common_title');
		$data['common_hadoop_refresh_fail'] = $this->lang->line('common_hadoop_refresh_fail');
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
		
		$data['common_hadoop_operating'] = $this->lang->line('common_hadoop_operating');
		$data['common_job_operating'] = $this->lang->line('common_job_operating');
		
		$this->load->view('ehm_refresh_fail_operate_nav', $data);
		
		$data['common_hostname'] = $this->lang->line('common_hostname');
		$data['common_ip_addr'] = $this->lang->line('common_ip_addr');
		$data['common_node_role'] = $this->lang->line('common_node_role');
		$data['common_create_time'] = $this->lang->line('common_create_time');
		$data['common_action'] = $this->lang->line('common_action');
		
		#generate pagination
		$this->load->model('ehm_hosts_model', 'hosts');
		$this->load->library('pagination');
		$config['base_url'] = $this->config->base_url() . 'index.php/operate/index/';
		$config['total_rows'] = $this->hosts->count_hosts($this->input->get('q',""));
		$config['per_page'] = 2000;
		if($this->input->get('q',"")!="")
		$config['suffix'] = "?q=".$this->input->get('q',"");
		
		$offset = $this->uri->segment(3,0);
		if($offset == 0):
			$offset = 0;
		else:
			$offset = ($offset / $config['per_page']) * $config['per_page'];
		endif;
		$this->pagination->initialize($config);
		$data['pagination'] = $this->pagination->create_links();
		
		$data['results'] = $this->hosts->get_hosts_list($config['per_page'], $offset,$this->input->get('q',""));
		$data['q']=$this->input->get('q',"");
		
		$this->load->view('ehm_hosts_error_list',$data);
		
		$this->load->view('div_end');
		$this->load->view('div_end');
		
		#generaet footer
		$this->load->view('footer', $data);		
	}
	
	public function FormatNamenode()
	{
		$this->load->model('ehm_installation_model', 'install');
		$html = $this->install->format_namenode();
		echo str_replace("\n","<br />",$html);
	}
	
	public function ViewLogs()
	{
		$host_id = $this->uri->segment(3,0);
		$role = $this->uri->segment(4,0);
		
		$this->load->model('ehm_hosts_model', 'hosts');
		$this->load->model('ehm_management_model', 'manage');
		
		$result = $this->hosts->get_host_by_host_id($host_id);
		$hostname = $result->hostname;
		$ip = $result->ip;
		$role = $role;
		
		$html = $this->manage->view_common_logs($ip, $hostname, $role);
		$html = str_replace("\n", "<br />", $html);
		echo $html;
	}
	
	public function Start()
	{
		$host_id = $this->uri->segment(3,0);
		$role = $this->uri->segment(4,0);
		
		$this->load->model('ehm_hosts_model', 'hosts');
		$this->load->model('ehm_management_model', 'manage');
		
		$result = $this->hosts->get_host_by_host_id($host_id);
		$hostname = $result->hostname;
		$ip = $result->ip;
		$role = $role;
		
		$str = $this->manage->control_hadoop($ip, $role, "start");
		$url = $this->input->server('HTTP_REFERER');
		if($role == "namenode")
		{
			$str .= $this->manage->hdfs_mkdir($ip, '/tmp', 'hdfs', 'hadoop', '777');
			$str .= $this->manage->hdfs_mkdir($ip, '/user', 'hdfs', 'hadoop', 'ugo+w');
		}
		echo $str;
		redirect($url);
	}
	
	public function Stop()
	{
		$host_id = $this->uri->segment(3,0);
		$role = $this->uri->segment(4,0);
		
		$this->load->model('ehm_hosts_model', 'hosts');
		$this->load->model('ehm_management_model', 'manage');
		
		$result = $this->hosts->get_host_by_host_id($host_id);
		$hostname = $result->hostname;
		$ip = $result->ip;
		$role = $role;
		
		$str = $this->manage->control_hadoop($ip, $role, "stop");
		$url = $this->input->server('HTTP_REFERER');
		redirect($url);
	}
	
	public function Restart()
	{
		$host_id = $this->uri->segment(3,0);
		$role = $this->uri->segment(4,0);
		
		$this->load->model('ehm_hosts_model', 'hosts');
		$this->load->model('ehm_management_model', 'manage');
		
		$result = $this->hosts->get_host_by_host_id($host_id);
		$hostname = $result->hostname;
		$ip = $result->ip;
		$role = $role;
		
		$str = $this->manage->control_hadoop($ip, $role, "restart");
		$url = $this->input->server('HTTP_REFERER');
		redirect($url);
	}
	
	public function KillJobAction()
	{
		$job_id = $this->input->post('job_id',TRUE);

		$this->load->model('ehm_management_model', 'manage');
		
		$this->manage->kill_job($job_id);
		
		redirect($this->config->base_url() . 'index.php/operate/job/');
	}
	
	public function Job()
	{
		#Generate header
		$this->lang->load('commons');
		$data['common_lang_set'] = $this->lang->line('common_lang_set');
		$data['common_title'] = $this->lang->line('common_title');
		$data['common_submit'] = $this->lang->line('common_submit');
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
		
		$data['common_hadoop_operating'] = $this->lang->line('common_hadoop_operating');
		$data['common_job_operating'] = $this->lang->line('common_job_operating');
		
		$this->load->view('ehm_hosts_operate_nav', $data);
		
		$data['common_hostname'] = $this->lang->line('common_hostname');
		$data['common_ip_addr'] = $this->lang->line('common_ip_addr');
		$data['common_node_role'] = $this->lang->line('common_node_role');
		$data['common_create_time'] = $this->lang->line('common_create_time');
		$data['common_action'] = $this->lang->line('common_action');
		
		$data['common_active_job'] = $this->lang->line('common_active_job');
		$data['common_kill_job'] = $this->lang->line('common_kill_job');
		$data['common_job_id'] = $this->lang->line('common_job_id');
		$data['common_not_found_jobtracker'] = $this->lang->line('common_not_found_jobtracker');
		
		$this->load->model('ehm_management_model', 'manage');
		$data['job_list'] = $this->manage->get_job_list();
		
		$this->load->view('ehm_hosts_operate_job',$data);
		
		$this->load->view('div_end');
		$this->load->view('div_end');
		
		#generaet footer
		$this->load->view('footer', $data);
	}
	
	public function KillJobById()
	{
		$job_id = $this->input->post('job_id');
		$this->load->model('ehm_management_model', 'manage');
		$this->manage->kill_job($job_id);
		redirect($this->config->base_url() . 'index.php/operate/job/');
	}
}

?>