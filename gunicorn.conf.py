# 并行工作进程数
workers = 1
# 指定每个工作者的线程数
threads = 1
# 监听端口
bind = '0.0.0.0:5001'
# 设置守护进程
#daemon = True

worker_class = 'uvicorn.workers.UvicornWorker'
# 设置进程文件目录
pidfile = '/app/gunicorn.pid'
# 日志
loglevel = 'warning' # 错误日志级别
accesslog = "/app/gunicorn_access.log"
errorlog = "/app/gunicorn_error.log"

chdir = "/app/"

#user = "www"
#group = "www"