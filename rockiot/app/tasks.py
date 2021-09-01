import logging
from tasks.celery import app
from app.rabbitops import rabbit_ops

logger = logging.getLogger(__name__)


@app.task(bind=True, ignore_result=False, max_retries=3)
def check_system_health(self):
    logger.debug(f'Check System Health Request: {self.request!r}')
    rabbit_ops.check_system_health()


@app.task(bind=True, ignore_result=False, max_retries=3)
def update_connections(self):
    logger.debug(f'Update Connections Request: {self.request!r}')
    rabbit_ops.update_connections()


@app.task(bind=True, ignore_result=False, max_retries=3)
def get_overview(self):
    logger.debug(f'Get Overview Request: {self.request!r}')
    rabbit_ops.get_overview()


@app.task(bind=True, ignore_result=False, max_retries=3)
def register_device(self, did):
    logger.debug(f'Register Device Request: {self.request!r}')
    rabbit_ops.register_device(did)


@app.task(bind=True, ignore_result=False, max_retries=3)
def activate_device(self, did):
    logger.debug(f'Activate Device Request: {self.request!r}')
    rabbit_ops.activate_device(did)


@app.task(bind=True, ignore_result=False, max_retries=3)
def deactivate_device(self, did):
    logger.debug(f'Deactivate Device Request: {self.request!r}')
    rabbit_ops.deactivate_device(did)


@app.task(bind=True, ignore_result=False, max_retries=3)
def handle_activation_request(self, did):
    logger.debug(f'Handle Activation Request: {self.request!r}')
    rabbit_ops.handle_activation_request(did)


@app.task(bind=True, ignore_result=False, max_retries=3)
def terminate_device(self, did):
    logger.debug(f'Terminate Device Request: {self.request!r}')
    rabbit_ops.terminate_device(did)
