import os

workers = int(os.environ.get('GUNICORN_PROCESSES', '2'))
threads = int(os.environ.get('GUNICORN_THREADS', '4'))
timeout = int(os.environ.get('GUNICORN_TIMEOUT', '30'))
bind = os.environ.get('GUNICORN_BIND', '0.0.0.0:8080')

forwarded_allow_ips = "*"
secure_scheme_headers = {'X-Forwarded-Proto': 'https'}

# ACCESS LOGS
## log to stoud
accesslog = '-'
## log format
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# ERROR LOGS
## log to sterr
errorlog = '-'
## can change this to 'debug' for troubleshooting
loglevel = 'info'