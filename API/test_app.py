import os, json
from dotenv import load_dotenv
from sqlalchemy import text
import pytest
from app import app as flask_app, db, User, Exercise, Workout, Set

# Load environment variables from the .env file
load_dotenv()

# Your other code, which can now access the variables
db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
data_file = os.getenv("DATA_FILE")


def load_data(app, db):
	"""Loads SQL data from a file into the database."""
	sql_file_path = data_file

	with open(sql_file_path, 'r', encoding='utf-8') as f:
		sql_script = f.read()

	with app.app_context():
		# Execute the SQL script directly using the app's database engine
		with db.engine.connect() as connection:
			connection.execute(text(sql_script))
	print("--- Test data loaded successfully! ---")


@pytest.fixture(scope="session")
def app():
	print("\n--- Configuring FLASK for testing ---")
	flask_app.config['TESTING'] = True
	flask_app.config['WTF_CSRF_ENABLED'] = False

	print("--- Ready to run the test suite ---")
	yield flask_app

	print("--- Cleaning up the DB ---")
	with flask_app.app_context():
		db.drop_all()


@pytest.fixture(scope="session")
def seed_database(app):
	"""
	Fixture to drop, recreate, and seed the database using an external script.
	This runs only once per test session.
	"""
	print(f"--- Connecting to database: '{db_name}' on '{db_host}' with user '{db_username}' ---")

	with app.app_context():
		print(f"--- Removing all tables ---")
		db.drop_all()
		print(f"--- Recreating all tables ---")
		db.create_all()

	print(f"--- Loading test data ---")
	load_data(app, db)
	print(f"--- Preseeding completed ---       ", end="", flush=True)
	yield


@pytest.fixture(scope="session")
def test_client(app):
	return app.test_client()


@pytest.fixture(scope="function")
def session(app, seed_database):
	"""
	Provides a transactional session for each test, relying on the seeded database.
	"""
	with app.app_context():
		connection = db.engine.connect()
		transaction = connection.begin()

		db.session = db._make_scoped_session(options={'bind': connection})

		yield db.session

		db.session.remove()
		transaction.rollback()
		connection.close()


def test_add_user_success(test_client, session):
	"""Test a new user can be added successfully by an admin."""

	initial_count = 2

	headers = {
		'X-User-ID': 1,
		'X-User-Role': 'admin'
	}
	payload = {
		'first_name': 'Raj',
		'last_name': 'Kumar',
		'email': 'raj@devops-innovations.com'
	}

	print(f"\n--- Real DB user count: {initial_count} ---")
	print(f"--- Adding new user {payload['first_name']} via POST request ---")
	res = test_client.post('/users/add', json=payload, headers=headers)
	assert res.status_code == 201

	# Check the response data instead of database count
	added_user = res.get_json()
	print(f"--- Ensure added user's first email is {added_user['email']} ---")
	assert added_user['first_name'] == 'Raj'
	assert added_user['email'] == 'raj@devops-innovations.com'


def test_swagger_docs_are_available(test_client):
	"""Test for the swagger documentation."""
	print("\n--- Swagger docs are reachable at localhost:5000/swagger.json ---")
	res = test_client.get('/swagger.json')
	assert res.status_code == 200


def test_get_users_unauthorized(test_client):
	"""Test the API's unauthorized user list retrieval."""
	print("\n--- Getting error 401 if I do not login ---")
	res = test_client.get('/users/')
	assert res.status_code == 401


def test_disable_enable_user(test_client, session, app):
	"""Test that a user can be disabled and re-enabled by an admin."""
	headers = {
		'X-User-ID': 1,
		'X-User-Role': 'admin'
	}

	user_to_toggle = 2
	print("\n--- Ensure user enabled ---")
	with app.app_context():
		user = db.session.get(User, user_to_toggle)
		assert user.enabled == 1

	print(f"--- Disabling user {user.first_name} ---")
	res_disable = test_client.put(f'/users/{user_to_toggle}/disable', headers=headers)
	assert res_disable.status_code == 200

	print(f"--- Ensure user {user.first_name} disabled ---")
	with app.app_context():
		user = db.session.get(User, user_to_toggle)
		assert user.enabled == 0

	print(f"--- Enabling user {user.first_name} ---")
	res_enable = test_client.put(f'/users/{user_to_toggle}/enable', headers=headers)
	assert res_enable.status_code == 200

	print(f"--- Ensure user {user.first_name} enabled ---")
	with app.app_context():
		user = db.session.get(User, user_to_toggle)
		assert user.enabled == 1


def test_add_multiple_exercises(test_client, session, app):
	"""Test adding multiple exercises and verifying the final count."""

	exercises_to_add = [
		{'name': 'Curl', 'description': 'Straight barbell curl'},
		{'name': 'Pull up', 'description': 'Shoulder width body weight pull up'},
		{'name': 'Dip', 'description': 'Parallel bar dip'}
	]
	headers = {
		'X-User-ID': 1,
		'X-User-Role': 'admin'
	}

	print("\n--- Getting initial exercise count ---")
	get_res = test_client.get('/exercises/', headers=headers)
	assert get_res.status_code == 200
	initial_count = len(get_res.get_json())

	print(f"--- Adding {len(exercises_to_add)} exercises to initial {initial_count} exercises ---")
	for exercise in exercises_to_add:
		res = test_client.post('/exercises/', json=exercise, headers=headers)
		assert res.status_code == 201

	print("--- Verifying exercises via GET request ---")
	get_res = test_client.get('/exercises/', headers=headers)
	assert get_res.status_code == 200
	retrieved_exercises = get_res.get_json()

	print(f"--- Verifying {len(exercises_to_add)} exercises were added---")
	assert len(retrieved_exercises) == len(exercises_to_add) + initial_count
	retrieved_names = {ex['name'] for ex in retrieved_exercises}
	expected_names = {ex['name'] for ex in exercises_to_add}

	print(f"--- Verifying all exercise names are {expected_names} ---")
	assert expected_names <= retrieved_names


def test_add_workout_for_user(test_client, session, app):
	"""Test adding a new workout and verifying the database."""
	headers = {
		'X-User-ID': 1,
		'X-User-Role': 'admin'
	}

	workout_user_id = 1
	with app.app_context():
		user = db.session.get(User, workout_user_id)
	print(f"\n--- Adding workout for {user.first_name} via POST ---")

	res = test_client.post(f'/workouts/{workout_user_id}/add', headers=headers)
	assert res.status_code == 201
	workout_data = res.get_json()
	workout_id = workout_data['id']

	print(f"--- Asserting user id {workout_user_id} ---")
	assert workout_data['user_id'] == workout_user_id

	print(f"--- Verifying workout for {user.first_name} in database ---")
	with app.app_context():
		workout = db.session.get(Workout, workout_id)
		assert workout is not None
		assert workout.user_id == workout_user_id


def test_add_and_update_set(test_client, session, app):
	"""Test adding a new set via POST and then updating it via PUT."""
	# 1. Retrieve the updated set via GET
	headers = {
		'X-User-ID': 1,
		'X-User-Role': 'admin'
	}

	workout_id = 1
	print(f"\n--- Retrieve initial number of sets in workout {workout_id} ---")
	res_get = test_client.get(f'/sets/{workout_id}', headers=headers)
	assert res_get.status_code == 200
	retrieved_sets = res_get.get_json()
	initial_sets = len(retrieved_sets)

	# 2. Add a new set via POST
	payload = {
		'exercise_id': 1,
		'weight': 135,
		'reps': 4,
		'comment': 'great'
	}
	print(f"--- Adding a new set via POST with {payload} ---")
	res_post = test_client.post(f'/sets/{workout_id}', json=payload, headers=headers)
	assert res_post.status_code == 201
	added_set = res_post.get_json()
	set_id = added_set['id']
	print(f"--- Set successfully added with ID: {set_id} ---")

	# 3. Update the newly created set via PUT
	update_payload = {
		'weight': 105,
		'reps': 5,
		'comment': 'Not so great anymore'
	}
	print(f"--- Updating the set via PUT with {update_payload} ---")

	res_put = test_client.put(f'/sets/{set_id}/update', json=update_payload, headers=headers)
	assert res_put.status_code == 200

	# 4. Retrieve the updated set via GET
	print("--- Retrieving the updated set via GET ---")
	res_get = test_client.get(f'/sets/{workout_id}', headers=headers)
	assert res_get.status_code == 200
	retrieved_sets = res_get.get_json()
	assert len(retrieved_sets) == initial_sets + 1
	retrieved_set = retrieved_sets[-1]

	# 5. Final assertions and printing the JSON
	print("--- Asserting and printing final JSON ---")
	assert retrieved_set['id'] == set_id
	assert retrieved_set['weight'] == 105
	assert retrieved_set['reps'] == 5
	assert retrieved_set['comment'] == 'Not so great anymore'
	print("--- Final JSON values: ", retrieved_set)


def test_calculate_one_rep_max(test_client, app, session):
	"""
	Test the /analytics/sets/<int:setID>/calc1rm endpoint
	"""

	headers = {
		'X-User-ID': 1,
		'X-User-Role': 'admin'
	}

	set_to_calculate = 1
	print(f"\n--- Testing successful 1RM calculation of set {set_to_calculate} ---")
	res = test_client.get(f'/analytics/sets/{set_to_calculate}/calc1rm', headers=headers)
	assert res.status_code == 200
	data = res.get_json()
	assert data['set_id'] == 1
	# We are happy if the value returned is greater than zero
	assert data['one_rep_max'] > 0
	print(f"--- 1RM for set 1: {data['one_rep_max']}")


def test_find_pr(test_client, app, session):
	"""
	Test the /analytics/users/<int:userID>/exercises/<int:exerciseID>/findpr endpoint
	"""

	headers = {
		'X-User-ID': 1,
		'X-User-Role': 'admin'
	}

	user_to_calculate = 1
	exercise_to_calculate = 1
	users_dump = json.loads(test_client.get(f'/users/', headers=headers).data)
	user_name = users_dump[0]['first_name']
	print(f"\n--- Testing successful PR calculation for user {user_name} ---")
	res = test_client.get(f'/analytics/users/{user_to_calculate}/exercises/{exercise_to_calculate}/findpr', headers=headers)
	assert res.status_code == 200
	data = res.get_json()
	assert data['max_weight'] == 105
	print(f"--- 1RM for user {user_name} for exercise {exercise_to_calculate}: {data['max_weight']}")


def test_gets_sets(test_client, app, session):
	"""
	Test the /analytics/users/<int:userID>/exercises/<int:exerciseID>/getsets endpoint
	"""

	headers = {
		'X-User-ID': 1,
		'X-User-Role': 'admin'
	}

	user_to_calculate = 1
	exercise_to_calculate = 1
	users_dump = json.loads(test_client.get(f'/users/', headers=headers).data)
	user_name = users_dump[0]['first_name']
	exercise_dump = json.loads(test_client.get(f'/exercises/', headers=headers).data)
	exercise_name = exercise_dump[0]['name']

	print(f"\n--- Performance retrieval of {exercise_name} for user {user_name} ---")
	res = test_client.get(f'/analytics/users/{user_to_calculate}/exercises/{exercise_to_calculate}/getsets', headers=headers)
	assert res.status_code == 200
	data = res.get_json()
	assert len(data) == 3
	for i in range(len(data)):
		print(f"--- Set {data[i]['id']}: {data[i]['weight']} x {data[i]['reps']}")
