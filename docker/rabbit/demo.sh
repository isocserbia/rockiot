#!/bin/sh
i=0
while [ $i -ne 200 ]
do
        i=$(($i+1))
        rabbitmqctl add_user "device999${i}" "device999${i}pass"
        rabbitmqctl set_user_tags "device999${i}" device
        rabbitmqctl set_permissions -p / "device999${i}" ".*" ".*" ".*"
        rabbitmqctl set_topic_permissions -p / "device999${i}" ".*" ".*" ".*"
        echo "Defined device 999${i}"
done