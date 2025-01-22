# sshared

后端共享库。

## 功能介绍

- `api`：基于 Litestar 框架的标准化 Web API 实现
- `config`：TOML 配置文件解析模块，包含常用的配置块
- `logging`：支持彩色输出、异常记录、保存到 PostgreSQL 数据库的日志记录模块
- `postgres`：PostgreSQL 表、视图、物化视图封装，连接池模块
- `terminal`：支持彩色输出、异常类格式化输出的终端增强模块
- `retry`：支持同步和异步函数、内置指数退避算法、支持重试 Hook
- `strict_struct`：基于 msgspec 的严格数据校验模块
- `time`：基于标准库 `date` / `datetime` 的日期处理模块
- `word_split`：基于阿里云 NLP 分词接口的分词模块