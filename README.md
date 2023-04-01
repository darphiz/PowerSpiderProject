# PowerSpiderProject

### REQUIRED QUEUES 
1. default x 5 
2. Notification x 2  (notify) 
3. CPU intensive x 3 
4. Report x 2  (report)



### COMMANDS
clean all queue - redis-cli flushall
Flower - celery -A ngo_scraper flower --port=5566
Notify Queue - celery -A ngo_scraper worker -l INFO -Q notify
report Queue - celery -A ngo_scraper worker -l INFO -Q report
Default Queue - celery -A ngo_scraper worker -l INFO -n worker_four
Scheduler - celery -A ngo_scraper beat -l INFO


## Start services
systemd location = /etc/systemd/system/celery.service
create directory sudo mkdir -p /var/run/celery/
add permission sudo chown scraper1:scraper1 /var/run/celery
sudo systemctl daemon-reload
sudo systemctl start celery.service

## Restart
sudo systemctl restart celery

## Stop
sudo systemctl stop celery
## Logs
sudo journalctl -u celery.service -f

## start server
sudo ./env/bin/python3.9 manage.py runserver 0.0.0.0:80