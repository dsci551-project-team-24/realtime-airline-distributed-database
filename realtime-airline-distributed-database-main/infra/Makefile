.PHONY: mysql_image router_image data_producer_image up down deploy

mysql_image:
	docker build -t custom_mysql -f custom_mysql/Dockerfile custom_mysql

router_image:
	docker build -t data_router -f ../src/backend/Dockerfile.data_router ../src/backend

data_producer_image:
	docker build -t data_producer -f ../src/backend/Dockerfile.flightradar_data_producer ../src/backend

up:
	docker-compose -f docker-compose.yaml up -d

down:
	docker-compose -f docker-compose.yaml down

deploy: mysql_image router_image data_producer_image up