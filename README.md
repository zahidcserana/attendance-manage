# Employee Attendance Management


## Database migration

docker exec -it attendance_app alembic init alembic

docker exec -it attendance_app alembic revision --autogenerate -m "Initial migration"
docker exec -it attendance_app alembic revision --autogenerate -m "Added user_id to Employee"

docker exec -it attendance_app alembic upgrade head

docker exec -it attendance_app alembic downgrade -1
