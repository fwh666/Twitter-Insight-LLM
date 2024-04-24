'''
1. 定时每小时采集一次推特数据
'''


import schedule
import time
from twitter_data_ingestion import  main as twitter_main
def job():
    twitter_main()
    print('[程序运行时间: %s]' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    print('[程序完成...推特数据采集完成]')


def schedule_job():
    schedule.every(1).hours.do(job)
    # schedule.every(30).minutes.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    print('[程序启动...推特数据采集]')
    schedule_job()