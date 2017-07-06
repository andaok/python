>### 作业系统

作业系统 V1.0 是基于蓝鲸cmdb和saltstack的命令执行, sls执行，文件上传等功能的简易作业系统。

如下就基本功能进行简要说明.

>##### 命令执行

- 选取作业目标主机，有三种方式可选取目标主机，分别是"cmdb分组目标选取","salt分组目标选取","动态分组目标选取"。下面以"动态分组目标选取 "进行主机选择。各分组之间区别，详见"分组说明"
![1](http://job.quark.com/static/images/Image.png)
- 确定选取目标主机 ，注意处于"DOWN"状态的主机是不可选取的。
![2](http://job.quark.com/static/images/Image_%5B1%5D.png)
- 执行结果展示
![3](http://job.quark.com/static/images/Image_%5B2%5D.png)

>##### 文件上传

- 选取作业目标主机
- 确定选取目标主机 ，注意处于"DOWN"状态的主机是不可选取的。
![4](http://job.quark.com/static/images/Image_%5B3%5D.png)
- 上传本地文件到salt-mater , 如你需上传到主机的文件，你先前已上传到salt-master中，则这步略过 ，直接选取后"确认执行"即可。
![5](http://job.quark.com/static/images/Image_%5B4%5D.png)
- 执行结果展示
![6](http://job.quark.com/static/images/Image_%5B5%5D.png)

>##### sls执行，过程同上，不再说明

>##### 分组说明

- cmdb分组目标选取, 数据来自于蓝鲸cmdb,编辑分组信息请前往cmdb.quark.com
- salt分组目标选取, 基于saltstack的主机过滤，过滤规则可在"分组管理"下的"salt分组管理"进行设置。
![7](http://job.quark.com/static/images/Image_%5B6%5D.png)
- 动态分组目标选取，自定义分组，可在"分组管理"下的"动态分组管理"进行设置。
![8](http://job.quark.com/static/images/Image_%5B7%5D.png)
