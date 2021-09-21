import logging
import uuid

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.gis.db import models as gismodels
from django.db import models
from django.db.models import JSONField
from django.utils.text import slugify
from simple_history.models import HistoricalRecords

logger = logging.getLogger(__name__)


class CommaSeparatedStringsField(models.CharField):

    def from_db_value(self, value, *args):
        if not value:
            return ''
        return ','.join(value.split(sep=' '))

    def get_prep_value(self, value):
        return value.replace(',', ' ')


class Municipality(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100, null=True)
    area = gismodels.MultiPolygonField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Municipalities"

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        self.code = slugify(self.name)
        super(Municipality, self).save(*args, **kwargs)


class Facility(models.Model):
    ELEMENTARY_SCHOOL = 'ELEMENTARY_SCHOOL'
    HIGH_SCHOOL = 'HIGH_SCHOOL'
    FACULTY = 'FACULTY'
    UNIVERSITY = 'UNIVERSITY'
    TYPES = (
        (ELEMENTARY_SCHOOL, 'ELEMENTARY_SCHOOL'),
        (HIGH_SCHOOL, 'HIGH_SCHOOL'),
        (FACULTY, 'FACULTY'),
        (UNIVERSITY, 'UNIVERSITY'),
    )

    name = models.CharField(max_length=100, null=False, unique=True)
    code = models.SlugField(max_length=64, unique=True, default=uuid.uuid1())
    type = models.CharField(max_length=20, null=False, choices=TYPES, default=ELEMENTARY_SCHOOL)
    email = models.EmailField(max_length=120, null=False)
    description = models.TextField(blank=True, null=True)
    municipality = models.ForeignKey(Municipality, related_name='facilities',
                                     db_column='municipality_id', on_delete=models.PROTECT)
    address = models.CharField(max_length=250)
    location = gismodels.PointField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    users = models.ManyToManyField(
        User,
        through='FacilityMembership',
        through_fields=('facility', 'user'),
    )

    class Meta:
        ordering = ['name']
        verbose_name = "Facility"
        verbose_name_plural = "Facilities"

    def __str__(self):
        return str(self.name)

    @property
    def lon(self):
        return None if not self.location else self.location.coords[0]

    @property
    def lat(self):
        return None if not self.location else self.location.coords[1]

    def municipality_name(self):
        return None if not self.municipality else self.municipality.name

    def save(self, *args, **kwargs):
        self.code = slugify(self.name)
        super(Facility, self).save(*args, **kwargs)


class FacilityMembership(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


def default_device_metadata():
    return {"manufacturer": "", "type": ""}


class Device(models.Model):
    NEW = 'NEW'
    REGISTERED = 'REGISTERED'
    ACTIVATED = 'ACTIVATED'
    DEACTIVATED = 'DEACTIVATED'
    FAULTY = 'FAULTY'
    TERMINATED = 'TERMINATED'
    STATUSES = (
        (NEW, 'NEW'),
        (REGISTERED, 'REGISTERED'),
        (ACTIVATED, 'ACTIVATED'),
        (DEACTIVATED, 'DEACTIVATED'),
        (FAULTY, 'FAULTY'),
        (TERMINATED, 'TERMINATED'),
    )

    DEFAULT = 'DEFAULT'
    CALIBRATION = 'CALIBRATION'
    PRODUCTION = 'PRODUCTION'
    MODES = (
        (DEFAULT, 'DEFAULT'),
        (CALIBRATION, 'CALIBRATION'),
        (PRODUCTION, 'PRODUCTION')
    )

    name = models.CharField(max_length=30, null=False)
    description = models.TextField(blank=True, null=True)
    location = gismodels.PointField(null=True)
    facility = models.ForeignKey(Facility, related_name='devices',
                                 db_column='facility_id', on_delete=models.PROTECT)
    device_id = models.CharField(max_length=50, null=True)
    device_pass = models.CharField(max_length=128, null=True)

    status = models.CharField(max_length=20, null=False, choices=STATUSES, default=NEW)
    mode = models.CharField(max_length=20, null=False, choices=MODES, default=DEFAULT)

    metadata = JSONField(default=default_device_metadata)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords(
        history_change_reason_field=models.TextField(null=True),
    )

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Devices"

    def __str__(self):
        return str(self.name)

    def set_device_pass(self, pwd):
        self.device_pass = make_password(pwd)

    def check_device_pass(self, pwd):
        return self.device_pass == make_password(pwd)

    def can_register(self):
        # return self.status == Device.NEW or self.status = Device.TERMINATED
        return True

    def can_activate(self):
        return self.status != Device.NEW

    def can_activate_from_device(self):
        return self.status != Device.FAULTY

    def can_deactivate(self):
        return self.status == Device.ACTIVATED

    @property
    def lon(self):
        return None if not self.location else self.location.coords[0]

    @property
    def lat(self):
        return None if not self.location else self.location.coords[1]

    def municipality_name(self):
        return None if not self.facility else self.facility.municipality_name()


class Platform(models.Model):
    name = models.CharField(max_length=30, null=False)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Platform"

    def __str__(self):
        return str(self.name)


class PlatformAttribute(models.Model):
    name = models.CharField(max_length=30, null=False)
    value = models.CharField(max_length=250, null=False)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    platform = models.ForeignKey(Platform, related_name='attributes',
                                 db_column='platform_id', on_delete=models.PROTECT)

    class Meta:
        ordering = ['name']
        verbose_name = "Platform attribute"
        verbose_name_plural = "Platform attributes"

    def __str__(self):
        return str(self.name)


def default_device_connection_faults():
    return {"count": 0, "messages": {}, "minutes_since_last_entry": 0}


class DeviceConnection(models.Model):
    name = models.CharField(max_length=128, null=False)
    user = models.CharField(max_length=64, null=False)
    client_id = models.CharField(max_length=64, null=False)
    ip_address = models.CharField(max_length=64, null=False)
    msg_cnt = models.DecimalField(decimal_places=0, max_digits=8)
    msg_rate = models.DecimalField(decimal_places=2, max_digits=8)
    connected_at = models.DateTimeField(auto_now_add=True, null=True)
    terminated_at = models.DateTimeField(auto_now_add=False, null=True)
    device = models.ForeignKey(Device, related_name='connections',
                               db_column='device_id', on_delete=models.CASCADE)
    faults = JSONField(default=default_device_connection_faults)
    state = models.CharField(max_length=30, null=False, default="UNKNOWN")

    class Meta:
        ordering = ['-connected_at']
        verbose_name_plural = "Device connections"
        unique_together = ('name', 'client_id')

    def __str__(self):
        return str(self.name)

    def update_from_rabbitmq_connection(self, c):
        self.user = c["user"]
        self.name = c["name"]
        if "variable_map" in c:
            self.client_id = c["variable_map"]["client_id"]
        self.ip_address = c["peer_host"]
        if "recv_cnt" in c:
            self.msg_cnt = c["recv_cnt"]
        else:
            self.msg_cnt = 0
        if "recv_oct_details" in c:
            self.msg_rate = c["recv_oct_details"]["rate"]
        else:
            self.msg_rate = 0
        if "state" in c:
            self.state = c["state"].upper()


class DeviceCalibrationModel(models.Model):
    device = models.ForeignKey(Device, related_name='calibration_models', db_column='device_id',
                               on_delete=models.CASCADE)
    temperature = CommaSeparatedStringsField(max_length=20, default="0,1,0")
    humidity = CommaSeparatedStringsField(max_length=20, default="0,1,0")
    no2 = CommaSeparatedStringsField(max_length=20, default="0,1,0")
    so2 = CommaSeparatedStringsField(max_length=20, default="0,1,0")
    pm1 = CommaSeparatedStringsField(max_length=20, default="0,1,0")
    pm10 = CommaSeparatedStringsField(max_length=20, default="0,1,0")
    pm2_5 = CommaSeparatedStringsField(max_length=20, default="0,1,0")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


def default_data_row():
    return {}


class SensorDataRaw(models.Model):
    time = models.DateTimeField(primary_key=True)
    device_id = models.CharField(max_length=30)
    client_id = models.CharField(max_length=30)
    data = JSONField(default=default_data_row)

    class Meta:
        managed = False
        abstract = False
        ordering = ['-time']
        unique_together = ('time', 'device_id')
        db_table = "sensor_data_raw"


class SensorDataAbstract(models.Model):
    time = models.DateTimeField(primary_key=True)
    device_id = models.CharField(max_length=30)
    client_id = models.CharField(max_length=30)
    temperature = models.DecimalField(decimal_places=4, max_digits=8)
    humidity = models.DecimalField(decimal_places=4, max_digits=8)
    no2 = models.DecimalField(decimal_places=4, max_digits=8)
    so2 = models.DecimalField(decimal_places=4, max_digits=8)
    pm1 = models.DecimalField(decimal_places=4, max_digits=8)
    pm10 = models.DecimalField(decimal_places=4, max_digits=8)
    pm2_5 = models.DecimalField(decimal_places=4, max_digits=8)

    class Meta:
        abstract = True
        ordering = ['-time']
        unique_together = ('time', 'device_id')


class SensorData(SensorDataAbstract):
    class Meta:
        abstract = False
        managed = False
        ordering = ['-time']
        verbose_name_plural = "SensorData"
        db_table = "sensor_data"


class SensorsDataRollupAbstract(models.Model):
    time = models.DateTimeField(primary_key=True)
    device_id = models.CharField(max_length=30)
    temperature = models.DecimalField(decimal_places=4, max_digits=8)
    humidity = models.DecimalField(decimal_places=4, max_digits=8)
    no2 = models.DecimalField(decimal_places=4, max_digits=8)
    so2 = models.DecimalField(decimal_places=4, max_digits=8)
    pm1 = models.DecimalField(decimal_places=4, max_digits=8)
    pm10 = models.DecimalField(decimal_places=4, max_digits=8)
    pm2_5 = models.DecimalField(decimal_places=4, max_digits=8)

    class Meta:
        abstract = True
        managed = False
        ordering = ['-time']
        verbose_name_plural = "SensorsRollups"

    @classmethod
    def get_class_for_interval(cls, interval="15m"):
        if interval == "15m":
            return SensorsDataRollup15m
        if interval == "1h":
            return SensorsDataRollup1h
        elif interval == "4h":
            return SensorsDataRollup4h
        elif interval == "24h":
            return SensorsDataRollup24h
        else:
            return SensorsDataRollup24h


class SensorsDataRollup15m(SensorsDataRollupAbstract):
    class Meta:
        abstract = False
        managed = False
        ordering = ['-time']
        verbose_name_plural = "SensorsDataRollup15m"
        db_table = "sensor_data_rollup_15m"


class SensorsDataRollup1h(SensorsDataRollupAbstract):
    class Meta:
        abstract = False
        managed = False
        ordering = ['-time']
        verbose_name_plural = "SensorsDataRollup1h"
        db_table = "sensor_data_rollup_1h"


class SensorsDataRollup4h(SensorsDataRollupAbstract):
    class Meta:
        abstract = False
        managed = False
        ordering = ['-time']
        verbose_name_plural = "SensorsDataRollup4h"
        db_table = "sensor_data_rollup_4h"


class SensorsDataRollup24h(SensorsDataRollupAbstract):
    class Meta:
        abstract = False
        managed = False
        ordering = ['-time']
        verbose_name_plural = "SensorsDataRollup24h"
        db_table = "sensor_data_rollup_24h"


class SensorDataLastValues(SensorDataAbstract):
    class Meta:
        abstract = False
        managed = False
        ordering = ['-time']
        verbose_name_plural = "SensorDataLastValues"
        db_table = "sensors_last_values"


class LagDiffAbstract(models.Model):
    time = models.DateTimeField(primary_key=True)
    device_id = models.CharField(max_length=30)
    diff_perc = models.DecimalField(decimal_places=4, max_digits=8)

    class Meta:
        abstract = True
        ordering = ['-time']
        unique_together = ('time', 'device_id')


class LagDiffTemperature(LagDiffAbstract):
    class Meta:
        abstract = False
        managed = False
        verbose_name_plural = "LagDiffTemperature"
        db_table = "lag_diff_temperature"


class LagDiffHumidity(LagDiffAbstract):
    class Meta:
        abstract = False
        managed = False
        verbose_name_plural = "LagDiffHumidity"
        db_table = "lag_diff_humidity"


class LagDiffNO2(LagDiffAbstract):
    class Meta:
        abstract = False
        managed = False
        verbose_name_plural = "LagDiffNO2"
        db_table = "lag_diff_no2"


class LagDiffSO2(LagDiffAbstract):
    class Meta:
        abstract = False
        managed = False
        verbose_name_plural = "LagDiffSO2"
        db_table = "lag_diff_so2"


class LagDiffPM1(LagDiffAbstract):
    class Meta:
        abstract = False
        managed = False
        verbose_name_plural = "LagDiffPM1"
        db_table = "lag_diff_pm1"


class LagDiffPM10(LagDiffAbstract):
    class Meta:
        abstract = False
        managed = False
        verbose_name_plural = "LagDiffPM10"
        db_table = "lag_diff_pm10"


class LagDiffPM2_5(LagDiffAbstract):
    class Meta:
        abstract = False
        managed = False
        verbose_name_plural = "LagDiffPM2_5"
        db_table = "lag_diff_pm2_5"


class CronJob(models.Model):
    jobid = models.IntegerField(primary_key=True)
    schedule = models.CharField(max_length=128)
    command = models.TextField()
    nodename = models.CharField(max_length=64)
    nodeport = models.IntegerField()
    database = models.CharField(max_length=64)
    username = models.CharField(max_length=64)
    active = models.BooleanField(default=True)
    jobname = models.CharField(max_length=128)

    class Meta:
        managed = False
        ordering = ['jobid']
        verbose_name_plural = "Data jobs"
        verbose_name = "Data job"
        db_table = "cron\".\"job"

    def __str__(self):
        return str(self.jobname)


class CronJobExecution(models.Model):
    runid = models.IntegerField(primary_key=True)
    jobid = models.ForeignKey(CronJob, related_name='executions',
                              db_column='jobid', on_delete=models.CASCADE)
    job_pid = models.IntegerField()
    database = models.CharField(max_length=64)
    username = models.CharField(max_length=64)
    command = models.TextField()
    status = models.CharField(max_length=128)
    return_message = models.CharField(max_length=64)
    start_time = models.DateTimeField(auto_now_add=False)
    end_time = models.DateTimeField(auto_now=False)

    class Meta:
        managed = False
        ordering = ['jobid', 'runid']
        verbose_name_plural = "Executions"
        verbose_name = "Execution"
        db_table = "cron\".\"job_run_details"

    def __str__(self):
        return str(self.jobid)

