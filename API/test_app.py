import unittest
from app import app, db, User, Exercise, Workout


class MyTestResult(unittest.TextTestResult):
    def getDescription(self, test):
        return test.shortDescription() or str(test)

    def addSuccess(self, test):
        self.stream.write(f"\n✅  SUCCESS: {self.getDescription(test)}\n\n")

    def addFailure(self, test, err):
        self.stream.write(f"\n❌  FAILED: {self.getDescription(test)}\n")


class MyTestRunner(unittest.TextTestRunner):
    resultclass = MyTestResult


class LiftingAPITestCase(unittest.TestCase):
    """This class represents the lifting api test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        # Use an in-memory SQLite database for testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()

        # create all tables
        with app.app_context():
            db.create_all()
            # Seed the database with a user for testing
            test_user = User(email='testuser@devops-inno.com', first_name='unittest', last_name='admin')
            db.session.add(test_user)
            db.session.commit()

            # Store the ID assigned by the database for future tests
            self.admin_user_id = test_user.id

    def tearDown(self):
        """Executed after each test"""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_admin_login_success(self):
        """Login and find yourself."""
        headers = {
            'X-User-ID': str(self.admin_user_id),
            'X-User-Role': 'admin'
        }

        # Actual condition:
        res = self.app.get('/users/', headers=headers)
        actual_status = res.status_code

        print("\n--- Login successful ---")
        expected_status_code = 200

        # Assert the actual outcome against the expected outcome
        self.assertEqual(res.status_code, expected_status_code)

        print("--- Getting JSON user data ---")
        data = res.get_json()

        print("--- Checking one user only ---")
        number_of_users = 1
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) == number_of_users)

        print("--- Finding user by email ---", end="", flush=True)
        first_user = data[0]
        self.assertEqual(first_user['id'], self.admin_user_id)
        self.assertEqual(first_user['email'], 'testuser@devops-inno.com')

    def test_swagger_docs_are_available(self):
        """Test for the swagger documentation"""
        print("\n--- Swagger docs are reachable ---", end="", flush=True)

        # Actual condition:
        res = self.app.get('/swagger.json')
        actual_status = res.status_code

        # Expected condition:
        expected_status = 200

        self.assertEqual(res.status_code, 200)

    def test_get_users_unauthorized(self):
        """Test the API's unauthorized user list retrieval."""

        print("\n--- Getting error 401 ---", end="", flush=True)

        # Actual condition:
        res = self.app.get('/users/')
        actual_status = res.status_code

        # Expected condition:
        expected_status = 401

        # Result:
        self.assertEqual(actual_status, expected_status)

    def test_add_user_success(self):
        """Test a new user can be added successfully by an admin."""

        # 1. Define the actual conditions
        headers = {
            'X-User-ID': '1',  # An existing admin user from setUp
            'X-User-Role': 'admin'
        }
        payload = {
            'first_name': 'Alex',
            'last_name': 'Korobchevsky',
            'email': 'alex@devops-inno.com'
        }

        print("\n--- Adding new user via POST request ---")
        res = self.app.post('/users/add', json=payload, headers=headers)

        print("--- Validate status 201 ---")
        self.assertEqual(res.status_code, 201)

        print("--- Ensure number of users is now 2 ---")
        with app.app_context():
            users = User.query.all()
            self.assertEqual(len(users), 2)

        print("--- Ensure  added user's first name is correct ---", end="", flush=True)
        added_user = res.get_json()
        self.assertEqual(added_user['first_name'], 'Alex')

    def test_disable_enable_user(self):
        """Test that a user can be disabled and re-enabled by an admin."""
        # First, add a user to the database to be disabled/enabled
        # Let the database handle the ID
        new_user_data = {
            'email': 'alex@devops-inno.com',
            'first_name': 'Alex',
            'last_name': 'Korobchevsky',
        }

        # Use the add user endpoint to create the user
        headers = {
            'X-User-ID': str(self.admin_user_id),
            'X-User-Role': 'admin'
        }

        print("\n--- Adding user via POST ---")
        res_add = self.app.post('/users/add', json=new_user_data, headers=headers)
        self.assertEqual(res_add.status_code, 201)
        added_user = res_add.get_json()
        added_user_id = added_user['id']

        print("--- Ensure user enabled ---")
        with app.app_context():
            user = db.session.get(User, added_user_id)
            self.assertEqual(user.enabled, 1)

        print("--- Disabling the user  ---")
        res_disable = self.app.put(f'/users/{added_user_id}/disable', headers=headers)
        self.assertEqual(res_disable.status_code, 200)

        print("--- Ensure user disabled ---")
        with app.app_context():
            user = db.session.get(User, added_user_id)
            self.assertEqual(user.enabled, 0)

        print("--- Enabling the user  ---")
        res_enable = self.app.put(f'/users/{added_user_id}/enable', headers=headers)
        self.assertEqual(res_enable.status_code, 200)

        print("--- Ensure user enabled ---", end="", flush=True)
        with app.app_context():
            user = db.session.get(User, added_user_id)
            self.assertEqual(user.enabled, 1)

    def test_add_multiple_exercises(self):
        """Test adding multiple exercises and verifying the final count."""

        # Define a list of exercises to be added
        exercises_to_add = [
            {'name': 'Squat', 'description': 'High bar back squat'},
            {'name': 'Bench', 'description': 'Wide grip flat bench barbell press'},
            {'name': 'Dead', 'description': 'Conventional barbell floor deadlift'},
            {'name': 'Press', 'description': 'Medium grip barbell standing press'},
            {'name': 'Front Squat', 'description': 'Olympic style front barbell squat'}
        ]

        # Use a pre-defined admin user for the requests
        headers = {
            'X-User-ID': '1',
            'X-User-Role': 'admin'
        }

        print("\n--- Adding exercises via POST ---")
        for exercise in exercises_to_add:
            res = self.app.post('/exercises/', json=exercise, headers=headers)
            self.assertEqual(res.status_code, 201)

        print("--- Verifying exercises via GET request ---")
        get_res = self.app.get('/exercises/', headers=headers)
        self.assertEqual(get_res.status_code, 200)
        retrieved_exercises = get_res.get_json()

        print(f"--- Verifying {len(retrieved_exercises)} exercises were added--")
        self.assertEqual(len(retrieved_exercises), len(exercises_to_add))

        print(f"--- Verifying all exercise names are correct---", end="", flush=True)
        retrieved_names = {ex['name'] for ex in retrieved_exercises}
        expected_names = {ex['name'] for ex in exercises_to_add}
        self.assertSetEqual(retrieved_names, expected_names)

    def test_add_workout_for_user(self):
        """Test adding a new workout and verifying the database."""
        target_user_id = self.admin_user_id

        # Define the headers for the request.
        headers = {
            'X-User-ID': str(self.admin_user_id),
            'X-User-Role': 'admin'
        }

        print("\n--- Adding workout via POST ---")
        res = self.app.post(f'/workouts/{target_user_id}/add', headers=headers)
        self.assertEqual(res.status_code, 201)
        workout_data = res.get_json()
        workout_id = workout_data['id']

        print("--- Asserting response data ---")
        self.assertEqual(workout_data['user_id'], target_user_id)

        print("--- Verifying workout in database ---", end="", flush=True)
        with app.app_context():
            workout = db.session.get(Workout, workout_id)
            self.assertIsNotNone(workout)
            self.assertEqual(workout.user_id, target_user_id)

    def test_add_and_update_set(self):
        """Test adding a new set via POST and then updating it via PUT."""

        # Precondition: Create a workout and an exercise
        with app.app_context():
            # Create an exercise
            exercise = Exercise(
                name="Squat",
                description="Back Squat"
            )
            db.session.add(exercise)
            db.session.commit()
            exercise_id = exercise.id

            # Create a workout and associate it with the exercise
            workout = Workout(
                user_id=self.admin_user_id,
            )
            db.session.add(workout)
            db.session.commit()
            workout_id = workout.id

        # 1. Add a new set via POST
        print("\n--- Adding a new set via POST ---")
        payload = {
            'exercise_id': exercise_id,
            'weight': 135,
            'reps': 4,
            'comment': 'great'
        }
        headers = {
            'X-User-ID': str(self.admin_user_id),
            'X-User-Role': 'admin'
        }
        res_post = self.app.post(f'/sets/{workout_id}', json=payload, headers=headers)
        self.assertEqual(res_post.status_code, 201)
        added_set = res_post.get_json()
        set_id = added_set['id']
        print(f"--- Set successfully added with ID: {set_id}")

        # 2. Update the newly created set via PUT
        print("--- Updating the set via PUT ---")
        update_payload = {
            'weight': 155,
            'reps': 5,
            'comment': 'Not so great anymore'
        }
        res_put = self.app.put(f'/sets/{set_id}/update', json=update_payload, headers=headers)
        self.assertEqual(res_put.status_code, 200)

        # 3. Retrieve the updated set via GET
        print("--- Retrieving the updated set via GET ---")
        res_get = self.app.get(f'/sets/{workout_id}', headers=headers)
        self.assertEqual(res_get.status_code, 200)
        retrieved_sets = res_get.get_json()
        self.assertEqual(len(retrieved_sets), 1)
        retrieved_set = retrieved_sets[0]

        # 4. Final assertions and printing the JSON
        print("--- Asserting and printing final JSON ---", end="", flush=True)
        self.assertEqual(retrieved_set['id'], set_id)
        self.assertEqual(retrieved_set['weight'], 155)
        self.assertEqual(retrieved_set['reps'], 5)
        self.assertEqual(retrieved_set['comment'], 'Not so great anymore')
        print("\n--- Final JSON values:\n", retrieved_set, end="", flush=True)


if __name__ == "__main__":
    runner = MyTestRunner(verbosity=2)
    unittest.main(testRunner=runner)