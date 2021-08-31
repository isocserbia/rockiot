import docker

client = docker.DockerClient(base_url='unix://var/run/docker.sock')

env_dict = {
    'DEMO_SLEEP_SECONDS': '3',
    'DEMO_IS_SSL': 'True',
    'BROKER_ATTRIBUTES_TOPIC': 'v1.attributes',
    'BROKER_DEVICE_ACTIONS_TOPIC': 'v1.devices.actions',
    'BROKER_DEVICE_EVENTS_TOPIC':'v1.devices.%s.events',
    'BROKER_DEVICE_INGEST_TOPIC': 'v1.devices.%s.actions.ingest',
    'BROKER_HOST':'rabbit1',
    'BROKER_AMQP_PORT': '5672',
    'BROKER_AMQP_SSL_PORT': '5671',
    'BROKER_MQTT_PORT': '1883',
    'BROKER_MQTT_SSL_PORT': '8883',
    'BROKER_VHOST': '/'
}

env_dict_2 = env_dict.copy()
env_dict_2['DEVICE_ID'] = 'device2'
env_dict_2['DEVICE_PASS'] = 'device2pass'

env_dict_3 = env_dict.copy()
env_dict_3['DEVICE_ID'] = 'device3'
env_dict_3['DEVICE_PASS'] = 'device3pass'

env_dict_4 = env_dict.copy()
env_dict_4['DEVICE_ID'] = 'device4'
env_dict_4['DEVICE_PASS'] = 'device4pass'

env_dict_5 = env_dict.copy()
env_dict_5['DEVICE_ID'] = 'device5'
env_dict_5['DEVICE_PASS'] = 'device5pass'

env_dict_6 = env_dict.copy()
env_dict_6['DEVICE_ID'] = 'device6'
env_dict_6['DEVICE_PASS'] = 'device6pass'

env_dict_7 = env_dict.copy()
env_dict_7['DEVICE_ID'] = 'device7'
env_dict_7['DEVICE_PASS'] = 'device7pass'

env_dict_8 = env_dict.copy()
env_dict_8['DEVICE_ID'] = 'device8'
env_dict_8['DEVICE_PASS'] = 'device8pass'

env_dict_9 = env_dict.copy()
env_dict_9['DEVICE_ID'] = 'device9'
env_dict_9['DEVICE_PASS'] = 'device9pass'

env_dict_10 = env_dict.copy()
env_dict_10['DEVICE_ID'] = 'device10'
env_dict_10['DEVICE_PASS'] = 'device10pass'

envs = [env_dict_2, env_dict_3, env_dict_4, env_dict_5, env_dict_6, env_dict_7, env_dict_8, env_dict_9, env_dict_10]

for e in envs:
    container = client.containers.run(
        command="/start.sh",
        image='rockiot_demo',
        name=f'rockiot_project_rockiot_demo_{e["DEVICE_ID"]}',
        detach=True,
        environment=e,
        network="rockiot_project_app-tier"
    )
