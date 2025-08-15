start:
	@echo "Starting Docker Compose..."
	docker-compose up --build

test:
	@echo "Running backend tests..."
	docker-compose run --rm backend pytest /app/tests

optimize:
	@echo "Running optimization script..."
	docker-compose run --rm backend python -c "from app.core.database import SessionLocal, Base, engine; from app.services.optimizer import Optimizer; from app.services.data_loader import load_all_data; Base.metadata.create_all(bind=engine); db = SessionLocal(); load_all_data(db); optimizer = Optimizer(db); optimizer.assign_orders(); print('Optimization complete.'); db.close()"

clean:
	@echo "Cleaning up Docker resources..."
	docker-compose down --volumes --remove-orphans
	@echo "Removing database file..."
	rm -f ./backend/app/sql_app.db

.PHONY: start test optimize clean
