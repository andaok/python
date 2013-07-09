<?php

class Ehm_management_model extends CI_Model
{
	public $ehm_host;
	public $ehm_port;
	public $socket;
	public $transport;
	public $protocol;
	public $ehm;

	public function __construct()
	{ 
		parent::__construct();
		$GLOBALS['THRIFT_ROOT'] = __DIR__ . "/../../libs/";
		include_once $GLOBALS['THRIFT_ROOT'] . 'packages/EasyHadoop/EasyHadoop.php';
		include_once $GLOBALS['THRIFT_ROOT'] . 'transport/TSocket.php';
		include_once $GLOBALS['THRIFT_ROOT'] . 'transport/TTransport.php';
		include_once $GLOBALS['THRIFT_ROOT'] . 'protocol/TBinaryProtocol.php';
	}

	public function kill_job($job_id)
	{
		$sql = 'select * from ehm_hosts where role like "namenode%"';
		$query = $this->db->query($sql);
		$result = $query->result();
		$ip = $result[0]->ip;
		
		$this->ehm_host = $ip;
		$this->ehm_port = $this->config->item('agent_thrift_port');
		$this->socket = new TSocket($this->ehm_host, $this->ehm_port);
		$this->socket->setSendTimeout(30000);
		$this->socket->setRecvTimeout(30000);
		$this->transport = new TBufferedTransport($this->socket);
		$this->protocol = new TBinaryProtocol($this->transport);
		$this->ehm = new EasyHadoopClient($this->protocol);
		
		$command = "sudo -u mapred hadoop job -kill ".$job_id;
		try
		{
			$this->transport->open();
			$str = $this->ehm->RunCommand($command);
			$this->transport->close();
		}
		catch(Exception $e)
		{
			$str = 'Caught exception: '.  $e->getMessage(). "\n";
		}
		return $str;
	}
	public function get_name_node()
	{
		$sql = 'select * from ehm_hosts where role like "namenode%"';
		$query = $this->db->query($sql);
		$result = $query->result();
		if(@$result[0]->ip != "")
			$ip = $result[0]->ip;
        return $ip;				
			
	
	}
	public function get_job_list()
	{
		$sql = 'select * from ehm_hosts where role like "namenode%"';
		$query = $this->db->query($sql);
		$result = $query->result();
		if(@$result[0]->ip != "")
			$ip = $result[0]->ip;
		else
			$ip = array();
		
		$this->ehm_host = $ip;
		$this->ehm_port = $this->config->item('agent_thrift_port');
		$this->socket = new TSocket($this->ehm_host, $this->ehm_port);
		$this->socket->setSendTimeout(30000);
		$this->socket->setRecvTimeout(30000);
		$this->transport = new TBufferedTransport($this->socket);
		$this->protocol = new TBinaryProtocol($this->transport);
		$this->ehm = new EasyHadoopClient($this->protocol);
		
		$command = "sudo -u mapred hadoop job -list";
		try
		{
			$this->transport->open();
			$str = $this->ehm->RunCommand($command);
			$str = explode("\n", $str);
			$this->transport->close();
		}
		catch(Exception $e)
		{
			$str = 'Caught exception: '.  $e->getMessage(). "\n";
		}
		return $str;
	}
	
	public function control_hadoop($host, $role , $operate) # $operate valid value is start or stop or restart
	{
		$this->ehm_host = $host;
		$this->ehm_port = $this->config->item('agent_thrift_port');
		$this->socket = new TSocket($this->ehm_host, $this->ehm_port);
		$this->socket->setSendTimeout(10000);
		$this->socket->setRecvTimeout(10000);
		$this->transport = new TBufferedTransport($this->socket);
		$this->protocol = new TBinaryProtocol($this->transport);
		$this->ehm = new EasyHadoopClient($this->protocol);
		
		switch($role)
		{
			case "namenode":
				$user = "hdfs";
				break;
			case "secondarynamenode":
				$user = "hdfs";
				break;
			case "datanode":
				$user = "hdfs";
				break;
			case "jobtracker":
				$user = "mapred";
				break;
			case "tasktracker":
				$user = "mapred";
				break;
		}
		
		if($operate == 'start' || $operate == 'stop')
		{
			$command = 'sudo -u '.$user.' /usr/sbin/hadoop-daemon.sh ' . $operate . ' ' . $role;
			try
			{
				$this->transport->open();
				$str = $this->ehm->RunCommand($command);
				$this->transport->close();
			}
			catch(Exception $e)
			{
				$str = 'Caught exception: '.  $e->getMessage(). "\n";
			}
		}
		elseif($operate == "restart")
		{
			try
			{
				$this->transport->open();
				$command = 'sudo -u '.$user.' /usr/sbin/hadoop-daemon.sh stop ' . $role;
				$str = $this->ehm->RunCommand($command);
				sleep(1);
				$command = 'sudo -u '.$user.' /usr/sbin/hadoop-daemon.sh start ' . $role;
				$str .= $this->ehm->RunCommand($command);
				$this->transport->close();
			}
			catch(Exception $e)
			{
				$str = 'Caught exception: '.  $e->getMessage(). "\n";
			}
		}
		else
		{
			return FALSE;
		}
		return $str;
	}
	
	public function view_common_logs($host, $hostname, $role)
	{
		$this->ehm_host = $host;
		$this->ehm_port = $this->config->item('agent_thrift_port');
		$this->socket = new TSocket($this->ehm_host, $this->ehm_port);
		$this->socket->setSendTimeout(30000);
		$this->socket->setRecvTimeout(30000);
		$this->transport = new TBufferedTransport($this->socket);
		$this->protocol = new TBinaryProtocol($this->transport);
		$this->ehm = new EasyHadoopClient($this->protocol);
		
		switch($role)
		{
			case "namenode":
				$user = "hdfs";
				break;
			case "secondarynamenode":
				$user = "hdfs";
				break;
			case "datanode":
				$user = "hdfs";
				break;
			case "jobtracker":
				$user = "mapred";
				break;
			case "tasktracker":
				$user = "mapred";
				break;
		}
		
		try
		{
			$this->transport->open();
			$command = "tail -n 200 /var/log/hadoop/".$user."/hadoop-".$user."-".$role."-".$hostname.".log";
			$str = $this->ehm->RunCommand($command);
			$str = str_replace('ERROR', "<b><font color=red>ERROR</font></b>",$str);
			$str = str_replace('FATAL', "<b><font color=red>FATAL</font></b>",$str);
			$str = str_replace('WARN', "<b><font color=orange>WARN</font></b>",$str);
			
			$tmp = explode("\n", $str);
			$tmp = array_reverse($tmp);
			$str = implode("\n", $tmp);
			
			$this->transport->close();
		}
		catch(Exception $e)
		{
			$str = 'Caught exception: '.  $e->getMessage(). "\n";
		}
		return $str;
	}
	
	public function chown_hdd($host, $mount_point, $role)
	{
		$this->ehm_host = $host;
		$this->ehm_port = $this->config->item('agent_thrift_port');
		$this->socket = new TSocket($this->ehm_host, $this->ehm_port);
		$this->socket->setSendTimeout(30000);
		$this->socket->setRecvTimeout(30000);
		$this->transport = new TBufferedTransport($this->socket);
		$this->protocol = new TBinaryProtocol($this->transport);
		$this->ehm = new EasyHadoopClient($this->protocol);
		
		switch($role)
		{
			case "namenode":
				$user = "hdfs";
				break;
			case "secondarynamenode":
				$user = "hdfs";
				break;
			case "datanode":
				$user = "hdfs";
				break;
			case "jobtracker":
				$user = "mapred";
				break;
			case "tasktracker":
				$user = "mapred";
				break;
		}
		
		try
		{
			$this->transport->open();
			$command = "chown -R ".$user.":".$this->config->item('hadoop_hadoop_group')." " . $mount_point;
			$str = $this->ehm->RunCommand($command);
			//$str = str_replace('ERROR', "<b><font color=red>ERROR</font></b>",$str);
			//$str = str_replace('FATAL', "<b><font color=red>FATAL</font></b>",$str);
			//$str = str_replace('WARN', "<b><font color=orange>WARN</font></b>",$str);
			$this->transport->close();
		}
		catch(Exception $e)
		{
			$str = 'Caught exception: '.  $e->getMessage(). "\n";
		}
		return $str;
	}
	
	public function hdfs_chown($host, $hdfs_folder, $user, $group, $recursive = TRUE)
	{
		$this->ehm_host = $host;
		$this->ehm_port = $this->config->item('agent_thrift_port');
		$this->socket = new TSocket($this->ehm_host, $this->ehm_port);
		$this->socket->setSendTimeout(30000);
		$this->socket->setRecvTimeout(30000);
		$this->transport = new TBufferedTransport($this->socket);
		$this->protocol = new TBinaryProtocol($this->transport);
		$this->ehm = new EasyHadoopClient($this->protocol);
		
		if($recursive == TRUE)
		{
			$r = " -R ";
		}
		
		$cmd = 'sudo -u hdfs hadoop dfs -chown '.$r.' '.$user.':'.$group.' '.$hdfs_folder;
		
		try
		{
			$this->transport->open();
			$str = $this->ehm->RunCommand($cmd);
			$this->transport->close();
		}
		catch(Exception $e)
		{
			$str = 'Caught exception: '.  $e->getMessage(). "\n";
		}
		return $str;
	}
	
	public function hdfs_chmod($host, $hdfs_folder, $chmod, $recursive = TRUE)
	{
		$this->ehm_host = $host;
		$this->ehm_port = $this->config->item('agent_thrift_port');
		$this->socket = new TSocket($this->ehm_host, $this->ehm_port);
		$this->socket->setSendTimeout(30000);
		$this->socket->setRecvTimeout(30000);
		$this->transport = new TBufferedTransport($this->socket);
		$this->protocol = new TBinaryProtocol($this->transport);
		$this->ehm = new EasyHadoopClient($this->protocol);
		
		if($recursive == TRUE)
		{
			$r = " -R ";
		}
		
		echo $cmd = 'sudo -u hdfs hadoop dfs -chmod '.$r.' '.$chmod.' '.$hdfs_folder;
		
		try
		{
			$this->transport->open();
			$str = $this->ehm->RunCommand($cmd);
			$this->transport->close();
		}
		catch(Exception $e)
		{
			$str = 'Caught exception: '.  $e->getMessage(). "\n";
		}
		return $str;
	}
	
	public function hdfs_mkdir($host, $hdfs_folder, $user, $group, $chmod, $recursive = TRUE)
	{
		$cmd = 'sudo -u hdfs hadoop dfs -mkdir '.$hdfs_folder;
		try
		{
			$this->transport->open();
			$str = $this->ehm->RunCommand($cmd);
			$this->transport->close();
		}
		catch(Exception $e)
		{
			$str = 'Caught exception: '.  $e->getMessage(). "\n";
		}
		$this->hdfs_chown($host, $hdfs_folder, $user, $group, $recursive);
		$this->hdfs_chmod($host, $hdfs_folder, $chmod, $recursive);
		return $str;
	}
	
	public function execute_shell_script($host, $commands)
	{
		$this->ehm_host = $host;
		$this->ehm_port = $this->config->item('agent_thrift_port');
		$this->socket = new TSocket($this->ehm_host, $this->ehm_port);
		$this->socket->setSendTimeout(30000);
		$this->socket->setRecvTimeout(30000);
		$this->transport = new TBufferedTransport($this->socket);
		$this->protocol = new TBinaryProtocol($this->transport);
		$this->ehm = new EasyHadoopClient($this->protocol);
		
		try
		{
			$this->transport->open();
			$str = $this->ehm->RunCommand($commands);
			$this->transport->close();
		}
		catch(Exception $e)
		{
			$str = 'Caught exception: '.  $e->getMessage(). "\n";
		}
		return $str;
	}
}

?>