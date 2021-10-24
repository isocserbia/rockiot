import logging
from datetime import date

from app.rabbitops import operations
from app.system import dbops, pipeline
from tasks.celery import app

logger = logging.getLogger(__name__)


@app.task(bind=True, ignore_result=True, max_retries=1, soft_time_limit=10)
def check_system_health(self):
    logger.debug(f'Check System Health Request: {self.request!r}')
    return operations.check_system_health()


@app.task(bind=True, ignore_result=True, max_retries=1, soft_time_limit=30)
def update_connections(self):
    logger.debug(f'Update Connections Request: {self.request!r}')
    return operations.update_connections()


@app.task(bind=True, ignore_result=False, max_retries=1, soft_time_limit=30)
def get_overview(self):
    logger.debug(f'Get Overview Request: {self.request!r}')
    return operations.get_overview()


@app.task(bind=True, ignore_result=False, max_retries=1, time_limit=120)
def export_raw_data_to_csv(self, dat=None):
    logger.debug(f'Export raw data request: {self.request!r}')
    return dbops.export_raw_data_to_csv(dat)


@app.task(bind=True, ignore_result=False, max_retries=1, rate_limit='1/m', soft_time_limit=60)
def clean_and_calibrate(self):
    logger.debug(f'Clean and Calibrate Request: {self.request!r}')
    return pipeline.clean_and_calibrate_dataframe()


@app.task(bind=True, ignore_result=False, max_retries=1, rate_limit='12/m')
def send_platform_attributes(self):
    logger.debug(f'Handle Send Platform Attributes Request: {self.request!r}')
    return operations.send_platform_attributes()


@app.task(bind=True, ignore_result=False, max_retries=2, rate_limit='240/m')
def register_device(self, did):
    logger.debug(f'Register Device Request: {self.request!r}')
    return operations.register_device(did)


@app.task(bind=True, ignore_result=False, max_retries=2, rate_limit='240/m')
def activate_device(self, did):
    logger.debug(f'Activate Device Request: {self.request!r}')
    return operations.activate_device(did)


@app.task(bind=True, ignore_result=False, max_retries=2, rate_limit='240/m')
def deactivate_device(self, did):
    logger.debug(f'Deactivate Device Request: {self.request!r}')
    return operations.deactivate_device(did)


@app.task(bind=True, ignore_result=False, max_retries=2, rate_limit='240/m')
def handle_activation_request(self, did):
    logger.debug(f'Handle Activation Request: {self.request!r}')
    return operations.handle_activation_request(did)


@app.task(bind=True, ignore_result=False, max_retries=2, rate_limit='240/m')
def terminate_device(self, did):
    logger.debug(f'Terminate Device Request: {self.request!r}')
    return operations.terminate_device(did)


@app.task(bind=True, ignore_result=False, max_retries=1, rate_limit='240/m')
def send_device_event(self, did, event_type):
    logger.debug(f'Device Event Request: {self.request!r}')
    return operations.send_device_event(did, event_type)


@app.task(bind=True, ignore_result=True, max_retries=1, rate_limit='240/m')
def save_device_metadata(self, did, metadata):
    logger.debug(f'Handle Save Device Metadata Request: {self.request!r}')
    return operations.save_device_metadata(did, metadata)


@app.task(bind=True, ignore_result=True, max_retries=1, rate_limit='240/m')
def send_device_metadata(self, did):
    logger.debug(f'Handle Send Device Metadata Request: {self.request!r}')
    return operations.send_device_metadata(did)



