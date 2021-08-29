#!/bin/bash

echo "Starting RabbitMQ"

HOSTNAME=`env hostname`

rabbitmq-server & rabbitmqctl wait /var/lib/rabbitmq/mnesia/rabbit\@$HOSTNAME.pid

if [[ $(rabbitmqadmin list users -q | grep 'rabbitmngmt') =~ 'rabbitmngmt' ]]; then

  echo "Configuration for RabbitMQ already exists, skipping ..."

else

#  echo "Initializing RabbitMQ queue 'mq2_amqp'"
#  rabbitmqadmin declare queue name=mq2_amqp durable=true
#  rabbitmqadmin declare binding source=amq.topic destination_type=queue destination=mq2_amqp routing_key=v1.devices.#.actions.ingest
#
#  echo "Initializing RabbitMQ task queue"
#  rabbitmqadmin declare queue name=tasks_amqp durable=true
#  rabbitmqadmin declare binding source=amq.topic destination_type=queue destination=tasks_amqp routing_key=v1.devices.actions
#  rabbitmqadmin declare queue name=tasks_amqp_delay durable=true arguments='{"x-dead-letter-exchange":"amq.direct","x-message-ttl":30000,"x-dead-letter-routing-key":"tasks.amqp"}'
#  rabbitmqadmin declare binding source=amq.direct destination_type=queue destination=tasks_amqp routing_key=tasks.amqp
#
#  echo "Initializing RabbitMQ management user"
#  rabbitmqctl add_user rabbitmngmt rabbitmngmt_pass
#  rabbitmqctl set_user_tags rabbitmngmt administrator
#  rabbitmqctl set_permissions -p / rabbitmngmt ".*" ".*" ".*"
#  rabbitmqctl set_topic_permissions -p / rabbitmngmt ".*" ".*" ".*"
#
#  echo "Initializing RabbitMQ management user"
#  rabbitmqctl add_user device1 device1pass
#  rabbitmqctl set_user_tags device1 device
#  rabbitmqctl set_permissions -p / device1 ".*" ".*" ".*"
#  rabbitmqctl set_topic_permissions -p / device1 ".*" ".*" ".*"
#
#  echo "Initializing RabbitMQ application users"
#  rabbitmqctl add_user amqpingest amqpingest_pass
#  rabbitmqctl set_user_tags amqpingest administrator
#  rabbitmqctl set_permissions -p / amqpingest ".*" ".*" ".*"
#  rabbitmqctl set_topic_permissions -p / amqpingest ".*" ".*" ".*"
#
#  rabbitmqctl add_user amqptaskproducer amqptaskproducer_pass
#  rabbitmqctl set_user_tags amqptaskproducer administrator
#  rabbitmqctl set_permissions -p / amqptaskproducer ".*" ".*" ".*"
#  rabbitmqctl set_topic_permissions -p / amqptaskproducer ".*" ".*" ".*"
#
#  rabbitmqctl add_user amqptaskconsumer amqptaskconsumer_pass
#  rabbitmqctl set_user_tags amqptaskconsumer administrator
#  rabbitmqctl set_permissions -p / amqptaskconsumer ".*" ".*" ".*"
#  rabbitmqctl set_topic_permissions -p / amqptaskconsumer ".*" ".*" ".*"
#
#  rabbitmqctl add_user mqtteventproducer mqtteventproducer_pass
#  rabbitmqctl set_user_tags mqtteventproducer administrator
#  rabbitmqctl set_permissions -p / mqtteventproducer ".*" ".*" ".*"
#  rabbitmqctl set_topic_permissions -p / mqtteventproducer ".*" ".*" ".*"

#  echo "Removing RabbitMQ guest user"
#  rabbitmqctl delete_user guest
  echo "Configuration completed"

fi

#tail -f /var/log/rabbitmq/log/rabbit_upgrade.log
tail -f /var/log/rabbitmq/log/rabbit.log
#tail -f /var/log/alternatives.log