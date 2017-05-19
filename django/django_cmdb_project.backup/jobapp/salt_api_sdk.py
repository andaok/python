# -*- encoding:utf-8 -*-
#--------------------------------
# @Date    : 2017-05-10 15:00
# @Author  : wye
# @Version : v1.0
# @Desrc   : salt api sdk interface
# -------------------------------- 

import salt.config
import salt.client
import salt.runner 



def get_keep_jobs_time():
    master_opts = salt.config.client_config('/etc/salt/master')
    keep_jobs_hours = master_opts['keep_jobs']
    return keep_jobs_hours



def get_running_jobs_info():
    master_opts = salt.config.client_config('/etc/salt/master')
    runner= salt.runner.RunnerClient(master_opts)
    resp = runner.cmd('jobs.active',print_event=False)
    return len(resp),resp



def get_host_meta_info(hostname):
    local = salt.client.LocalClient()
    resp = local.cmd(hostname,'grains.items')
    return resp[hostname]



def get_host_status(hostname):
    local = salt.client.LocalClient()
    resp = local.cmd(hostname,'test.ping',timeout=2)
    print resp
    if resp and resp[hostname]:
        return 1
    else:
        return 0


if __name__ == "__main__":

    # # obtain keep_jobs
    # import salt.config
    # master_opts = salt.config.client_config('/etc/salt/master')
    # print master_opts['keep_jobs']

    # # salt client interface,execute salt cli cmd.
    # import salt.client
    # local = salt.client.LocalClient()
    # resp = local.cmd('*','test.ping')
    # print resp

    # # execute salt cli async cmd
    # import salt.client
    # local = salt.client.LocalClient()
    # resp = local.cmd_async('*','cmd.run',['sleep 10;hostname'])
    # print resp

    # # execute salt cli async cmd
    # import salt.client
    # local = salt.client.LocalClient()
    # resp = local.cmd_async('*','cmd.run',['sleep 13;hostname'])
    # print resp

    # # saltutil.find_job
    # # import salt.client
    # # local = salt.client.LocalClient()
    # # resp = local.cmd('*','saltutil.find_job',['20170510152420651416'])
    # # print resp


    # # execute salt-run cli cmd
    # import salt.runner
    # runner1 = salt.runner.RunnerClient(master_opts)
    # resp = runner1.cmd('jobs.active',print_event=False)
    # print len(resp)

    #print get_host_meta_info("W612-JENKDOCK-3")
    print get_host_status("BGP-NETAM-01")
    pass