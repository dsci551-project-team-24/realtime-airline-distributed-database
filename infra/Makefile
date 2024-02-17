.PHONY: mysql_image up down scale_mysql_cluster scale_down_mysql_cluster deploy

mysql_image:
	docker build -t custom_mysql -f custom_mysql/Dockerfile custom_mysql

up:
	docker-compose -f docker-compose.yaml up -d

down:
	docker-compose -f docker-compose.yaml down

deploy: mysql_image up