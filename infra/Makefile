.PHONY: mysql_image router_image up down deploy

mysql_image:
	docker build -t custom_mysql -f custom_mysql/Dockerfile custom_mysql

router_image:
	docker build -t data_router -f ../src/backend/Dockerfile.data_router ../src/backend

up:
	docker-compose -f docker-compose.yaml up -d

down:
	docker-compose -f docker-compose.yaml down

deploy: mysql_image router_image up