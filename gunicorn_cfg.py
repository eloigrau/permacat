command = '/home/udjango/permacat/permacatenv/bin/gunicorn'
pythonpath = '/home/udjango/permacat/permacatenv/bin/python'
bind = 'unix:/home/udjango/permacat/gunicorn.sock'
workers = 3
accesslog = "/home/udjango/gunicorn.access.log"
# Error log - records Gunicorn server goings-on
errorlog = "/home/udjango/gunicorn.error.log"
# Whether to send Django output to the error log 
capture_output = True
# How verbose the Gunicorn error logs should be 
loglevel = "warning"
#loglevel= "debug

timeout=120
