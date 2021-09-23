FROM rabbitmq:3.8-management

RUN apt-get update && apt-get install -y curl unzip

ADD ./certs /etc/ssl/certs/
ADD rabbitmq-ssl.config /etc/rabbitmq/rabbitmq.config
# ADD definitions.json /etc/rabbitmq/definitions.json
ADD definitions-demo.json /etc/rabbitmq/definitions.json
ADD demo.sh /demo.sh
RUN chmod +x /demo.sh

RUN mkdir -p /var/log/rabbitmq/log
RUN chown -R rabbitmq:rabbitmq /var/log/rabbitmq

RUN chown rabbitmq:rabbitmq /etc/ssl/certs \
	&& chown rabbitmq:rabbitmq /etc/ssl/certs/* \
	&& chmod 710 /etc/ssl/certs \
	&& chmod 610 /etc/ssl/certs/*


# COPY plugins/rabbitmq_delayed_message_exchange-3.8.0.ez /opt/rabbitmq/plugins/
# RUN rabbitmq-plugins enable --offline rabbitmq_delayed_message_exchange
#
# COPY plugins/rabbitmq_message_timestamp-3.8.0.ez /opt/rabbitmq/plugins/
# RUN rabbitmq-plugins enable --offline rabbitmq_message_timestamp