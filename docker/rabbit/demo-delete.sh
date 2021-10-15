#!/bin/sh
i=0
while [ $i -ne 10 ]
do
  i=$(($i+1))
  rabbitmqctl delete_user "device${i}"
  echo "Deleted device${i}"
done

i=0
while [ $i -ne 200 ]
do
  i=$(($i+1))
  rabbitmqctl delete_user "device999${i}"
  echo "Deleted device999${i}"
done
