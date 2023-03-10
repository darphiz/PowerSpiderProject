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
Default Queue - celery -A ngo_scraper worker -l INFO 
Scheduler - celery -A ngo_scraper beat -l INFO