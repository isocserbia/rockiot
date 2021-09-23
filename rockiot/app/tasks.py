import logging
from datetime import date

from app.rabbitops import rabbit_ops
from app.system import dbops, pipeline, anomaly
from tasks.celery import app

logger = logging.getLogger(__name__)


@app.task(bind=True, ignore_result=True, max_retries=3)
def check_system_health(self):
    logger.debug(f'Check System Health Request: {self.request!r}')
    return rabbit_ops.check_system_health()


@app.task(bind=True, ignore_result=True, max_retries=3)
def update_connections(self):
    logger.debug(f'Update Connections Request: {self.request!r}')
    return rabbit_ops.update_connections()


@app.task(bind=True, ignore_result=False, max_retries=3)
def get_overview(self):
    logger.debug(f'Get Overview Request: {self.request!r}')
    return rabbit_ops.get_overview()


@app.task(bind=True, ignore_result=False, max_retries=3, rate_limit='20/m')
def register_device(self, did):
    logger.debug(f'Register Device Request: {self.request!r}')
    return rabbit_ops.register_device(did)


@app.task(bind=True, ignore_result=False, max_retries=3, rate_limit='20/m')
def activate_device(self, did):
    logger.debug(f'Activate Device Request: {self.request!r}')
    return rabbit_ops.activate_device(did)


@app.task(bind=True, ignore_result=False, max_retries=3, rate_limit='20/m')
def deactivate_device(self, did):
    logger.debug(f'Deactivate Device Request: {self.request!r}')
    return rabbit_ops.deactivate_device(did)


@app.task(bind=True, ignore_result=False, max_retries=3, rate_limit='30/m')
def handle_activation_request(self, did):
    logger.debug(f'Handle Activation Request: {self.request!r}')
    return rabbit_ops.handle_activation_request(did)


@app.task(bind=True, ignore_result=False, max_retries=3, rate_limit='20/m')
def terminate_device(self, did):
    logger.debug(f'Terminate Device Request: {self.request!r}')
    return rabbit_ops.terminate_device(did)


@app.task(bind=True, ignore_result=False, max_retries=3)
def export_raw_data_to_csv(self, dat=date.today().isoformat()):
    logger.debug(f'Export raw data request: {self.request!r}')
    return dbops.export_raw_data_to_csv(dat)


@app.task(bind=True, ignore_result=False, max_retries=3)
def clean_and_calibrate(self):
    logger.debug(f'Clean and Calibrate Request: {self.request!r}')
    return pipeline.clean_and_calibrate_dataframe()


@app.task(bind=True, ignore_result=False, max_retries=3)
def detect_anomalies(self):
    logger.debug(f'Detect anomalies Request: {self.request!r}')
    return anomaly.detect_anomalies()
