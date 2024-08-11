# Xtracking

## 准备工作
1. python > 3.11
---
2. 安装sqlserver驱动
> [MAC](https://learn.microsoft.com/zh-cn/sql/connect/odbc/linux-mac/install-microsoft-odbc-driver-sql-server-macos?view=sql-server-ver16)
> 
> [LINUX](https://learn.microsoft.com/zh-cn/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16&tabs=alpine18-install%2Calpine17-install%2Cdebian8-install%2Credhat7-13-install%2Crhel7-offline)
---
3. 安装依赖
```bash
pip install -r ./requirements.txt 
```
---
说明:
1. 配置文件为config.yaml
2. 开发环境日志等级为默认DEBUG，不生成日志文件。生产环境生成日志文件，路径: ${workdir}/logs/xtracking.log
3. 同步日志保存在sqlite数据库中，路径: ${workdir}/data/xtracking.db


### *注意*
1. 前端无法独立打包，所以必须***有网络的环境下***使用
