import schedule
import time
from twitter_data_ingestion import main as main_ingestion
from notion_clean_twitter import main as clean_main

def job():
    main_ingestion()
    clean_main()
    print('[Twitter采集程序结束...]')
    print('[Twitter采集程序运行时间: %s]' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))


def schedule_job():
    schedule.every().day.at("08:00").do(job)
    # schedule.every(10).seconds.do(job)
    # schedule.every(10).minutes.do(job)
    # schedule.every(1).hours.do(job)
    # schedule.every(1).seconds.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    print('[程序启动...Twitter采集]')
    schedule_job()
