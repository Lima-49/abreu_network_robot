import schedule_run
import time

task = schedule_run.config_run()

while True:
    task.run_pending()
    time.sleep(1)
