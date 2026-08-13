'''
- airflow 내부 정보 접근, 출력시 jinja 활용, 내부 정보 접근시 macro 활용
- 콜백함수 내부 kwargs를 인자를 통해 접근, 기타 일반적인 상황 jinja를 이용하여 접근
'''
# 1. 모듈
from airflow import DAG
# pyrefly: ignore [missing-import]
from airflow.operators.python import PythonOperator
# pyrefly: ignore [missing-import]
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import logging
# pyrefly: ignore [missing-import]
import pendulum

# 2. 전역변수
KST = pendulum.timezone("Asia/Seoul")


def _print(**kwargs):
  # XCOM에서 데이터 획득
  ti = kwargs['ti']
  ds = kwargs['ds']
  ds_nodash = kwargs['ds_nodash']
  run_id = kwargs['run_id']  
  logging.info("=== print_task ===")
  logging.info(f"ti = {ti}")
  logging.info(f"ds = {ds}")
  logging.info(f"ds_nodash = {ds_nodash}")
  logging.info(f"run_id = {run_id}")

# 3. DAG
with DAG(
  dag_id      = "03_basics_context_jinja",
  description = "macro을 이용하여 context 접근, jinja를 통해 표현",
  default_args= {
    "owner"           : "aic-de7-admin",    
    "retries"         : 1,
    "retry_delay"     : timedelta(minutes=1)
  },
  # 매일 오전 9시 00분에 스케줄 작동
  schedule_interval = "0 9 * * *", # cron 방식으로 표기 (분, 시, 일, 월, 주)
  # 수행 시작 시간 서울 시간대 타임존 조정
  start_date  = pendulum.datetime( 2026,6,29, tz=KST ),
  catchup     = False,
  tags        = ['macro', 'context', 'jinja']
) as dag:

  # 4. 오퍼레이터
  t1 = BashOperator(
    task_id = "jinja_used_task"
    ,bash_command = "echo 'DAG의 t1 task 수행시간 {{ds}}, {{ti}}'"
  )  
  t2 = BashOperator(
    task_id = "jinja_macro_task"
    # macro를 통해서 준비된 함수 활용
    ,bash_command = "echo 'DAG의 t1 task 일주일 전 수행시간 {{macros.ds_add(ds, -7)}}, 랜덤 {{macros.random()}}'"
  )  
  t3 = PythonOperator(
    task_id = "jinja_python_task"
    ,python_callable = _print
  )  

  # 5. 의존성(수행순서)