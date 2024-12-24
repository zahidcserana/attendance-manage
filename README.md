# Employee Attendance Management
My documented journey to learning fastapi

## Database migration

docker exec -it attendance_app alembic init alembic

docker exec -it attendance_app alembic revision --autogenerate -m "Initial migration"

docker exec -it attendance_app alembic upgrade head
