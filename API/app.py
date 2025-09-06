import os
from dotenv import load_dotenv
from flask import Flask
from flask_restx import Api, Resource, fields, reqparse
from models import db, User, Exercise, Workout, Set, SchemaVersion
from datetime import datetime
from functools import wraps
from analytics import calculate_one_rep_max, find_pr, get_sets_for_exercise_and_user
from flask_cors import CORS


# Load environment variables from .env file
load_dotenv()

# Initialize Flask and SQLAlchemy
app = Flask(__name__)
CORS(app)

# Configure a simple SQLite database for local testing
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lifting.db'
# Get database credentials from environment variables
db_user = os.getenv('DB_USERNAME')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')

# Construct the database URI and set it in the app config
database_uri = f"mysql://{db_user}:{db_password}@{db_host}/{db_name}"
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RESTX_MASK_SWAGGER'] = False  # Allows full API doc in Swagger

# Security definitions for API documentation
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-User-Role'
    },
    'userid': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-User-ID'
    }
}

db.init_app(app)

# --- Get API Metadata from Environment Variables ---
api_version = os.getenv('API_VERSION')
api_title = os.getenv('API_TITLE')
api_description = os.getenv('API_DESCRIPTION')

api = Api(app,
          version=api_version,
          title=api_title,
          description=api_description,
          doc='/swagger/',
          authorizations=authorizations,
          security=['apikey', 'userid'])


# Create the database tables
with app.app_context():
    db.create_all()

# --- Security Decorator ---
# This parser will extract the user role and ID from the request headers
auth_parser = reqparse.RequestParser()
auth_parser.add_argument('X-User-Role', type=str, required=True, location='headers',
                         help='The role of the authenticated user (admin, user, report)')
auth_parser.add_argument('X-User-ID', type=int, required=True, location='headers',
                         help='The ID of the authenticated user')


def requires_auth(allowed_roles):
    """
    Decorator to protect API routes based on user roles.
    Checks for the X-User-Role and X-User-ID headers.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                args_from_parser = auth_parser.parse_args()
                user_role = args_from_parser['X-User-Role']
                authenticated_user_id = args_from_parser['X-User-ID']

                # Check if the user role is in the list of allowed roles
                if user_role not in allowed_roles:
                    api.abort(403, "Forbidden: You do not have the required permissions.")

                # If the role is 'user', restrict access to their own data
                if user_role == 'user':
                    if 'userID' in kwargs and kwargs['userID'] != authenticated_user_id:
                        api.abort(403, "Forbidden: Users can only access their own data.")

                return func(*args, **kwargs)
            except Exception as e:
                api.abort(401, "Authentication required: Please provide X-User-Role and X-User-ID headers.")

        return wrapper

    return decorator


# --- API Resources ---
# A model to define the structure of a user in the API docs
user_model = api.model('User', {
    'id': fields.Integer(readOnly=True, description='The user unique identifier'),
    'first_name': fields.String(required=True, description='The user\'s first name'),
    'last_name': fields.String(required=True, description='The user\'s last name'),
    'email': fields.String(required=True, description='The user\'s email address'),
    'enabled': fields.String(required=True, description='1 - enabled, 0 - disabled'),
})

# Namespace for user endpoints
ns_users = api.namespace('users', description='User operations')

@ns_users.route('/')
class UserList(Resource):
    @ns_users.doc('list_users')
    @ns_users.marshal_list_with(user_model)
    @requires_auth(['admin'])
    def get(self):
        """List all users"""
        users = User.query.all()
        return users

# A new namespace to handle single user resources
@ns_users.route('/<int:id>/enable')
class UserEnable(Resource):
    @ns_users.doc('enable_user')
    @ns_users.marshal_with(user_model)
    @requires_auth(['admin'])
    def put(self, id):
        """Enable a user by their ID"""
        user = User.query.get_or_404(id)
        user.enabled = 1
        db.session.commit()
        return user

@ns_users.route('/<int:id>/disable')
class UserDisable(Resource):
    @ns_users.doc('disable_user')
    @ns_users.marshal_with(user_model)
    @requires_auth(['admin'])
    def put(self, id):
        """Disable a user by their ID"""
        user = User.query.get_or_404(id)
        user.enabled = 0
        db.session.commit()
        return user

# Create a request parser to handle the input parameters
parser = reqparse.RequestParser()
parser.add_argument('first_name', type=str, required=True, help='First name of the user')
parser.add_argument('last_name', type=str, required=True, help='Last name of the user')
parser.add_argument('email', type=str, required=True, help='Email of the user')


@ns_users.route('/add')
class UserAdd(Resource):
    @ns_users.doc('add_user')
    @ns_users.expect(parser)
    @ns_users.marshal_with(user_model)
    @requires_auth(['admin'])
    def post(self):
        """Creates a new user"""
        args = parser.parse_args()
        new_user = User(
            first_name=args['first_name'],
            last_name=args['last_name'],
            email=args['email'],
            enabled=1  # Enabled by default
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user, 201

# A model to define the structure of an exercise in the API docs
exercise_model = api.model('Exercise', {
    'id': fields.Integer(readOnly=True, description='The exercise unique identifier'),
    'name': fields.String(required=True, description='The name of the exercise'),
    'description': fields.String(description='A description of the exercise'),
    'date_started': fields.DateTime(readOnly=True, description='The date the exercise was started'),
})

# Namespace for exercise endpoints
ns_exercises = api.namespace('exercises', description='Exercise operations')

# Request parser for adding a new exercise
exercise_add_parser = reqparse.RequestParser()
exercise_add_parser.add_argument('name', type=str, required=True, help='Name of the exercise')
exercise_add_parser.add_argument('description', type=str, required=False, help='Description of the exercise')

@ns_exercises.route('/')
class ExerciseList(Resource):
    @ns_exercises.doc('add_exercise')
    @ns_exercises.expect(exercise_add_parser)
    @ns_exercises.marshal_with(exercise_model)
    @requires_auth(['admin', 'user'])
    def post(self):
        """Creates a new exercise"""
        args = exercise_add_parser.parse_args()
        new_exercise = Exercise(
            name=args['name'],
            description=args['description']
        )
        db.session.add(new_exercise)
        db.session.commit()
        return new_exercise, 201

    @ns_exercises.doc('list_all_exercises')
    @ns_exercises.marshal_list_with(exercise_model)
    @requires_auth(['admin', 'user', 'report'])
    def get(self):
        """List all exercises"""
        exercises = Exercise.query.all()
        return exercises

# Model for the API documentation
workout_model = api.model('Workout', {
    'id': fields.Integer(readOnly=True),
    'workout_date': fields.DateTime(required=True),
    'comment': fields.String,
    'user_id': fields.Integer(required=True)
})

ns_workouts = api.namespace('workouts', description='Workout operations')

# Request parser for adding a new workout
workout_add_parser = reqparse.RequestParser()
workout_add_parser.add_argument('workout_date', type=str, required=False, help='Date and time of the workout (YYYY-MM-DD HH:MM:SS)')
workout_add_parser.add_argument('comment', type=str, required=False, help='A comment about the workout')

@ns_workouts.route('/<int:userID>/add')
class WorkoutAdd(Resource):
    @ns_workouts.doc('add_workout_for_user')
    @ns_workouts.expect(workout_add_parser)
    @ns_workouts.marshal_with(workout_model, code=201)
    @requires_auth(['admin', 'user'])
    def post(self, userID):
        """Creates a new workout for a specific user"""

        # 1. Validate the user ID
        user = User.query.get_or_404(userID, description="User not found")

        # 2. Parse optional arguments
        args = workout_add_parser.parse_args()

        # 3. Handle optional date
        workout_date = args['workout_date']
        if workout_date is not None:
            try:
                workout_date = datetime.strptime(workout_date, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                api.abort(400, "Invalid date format. Use YYYY-MM-DD HH:MM:SS")

        # 4. Create and save the new workout
        new_workout = Workout(
            workout_date=workout_date,
            comment=args['comment'],
            user_id=userID
        )
        db.session.add(new_workout)
        db.session.commit()

        return new_workout, 201


set_model = api.model('Set', {
    'id': fields.Integer(readOnly=True),
    'exercise_id': fields.Integer(required=True),
    'weight': fields.Float,
    'reps': fields.Integer,
    'comment': fields.String,
    'workout_id': fields.Integer(required=True)
})

ns_sets = api.namespace('sets', description='Set operations')

set_add_parser = reqparse.RequestParser()
set_add_parser.add_argument('exercise_id', type=int, required=True, help='ID of the exercise this set belongs to')
set_add_parser.add_argument('weight', type=float, required=False, help='Weight used for the set')
set_add_parser.add_argument('reps', type=int, required=False, help='Number of repetitions')
set_add_parser.add_argument('comment', type=str, required=False, help='A comment about the set')


@ns_sets.route('/<int:workoutID>')
class SetList(Resource):
    @ns_sets.doc('add_set_for_workout')
    @ns_sets.expect(set_add_parser)
    @ns_sets.marshal_with(set_model, code=201)
    @requires_auth(['admin', 'user'])
    def post(self, workoutID):
        """Creates a new set for a specific workout"""

        # 1. Validate the workout ID
        workout = Workout.query.get_or_404(workoutID, description="Workout not found")

        # 2. Parse the request arguments
        args = set_add_parser.parse_args()

        # 3. Validate the exercise ID
        exercise_id = args['exercise_id']
        exercise = Exercise.query.get_or_404(exercise_id, description="Exercise not found")

        # 4. Create and save the new set
        new_set = Set(
            exercise_id=exercise.id,  # Use the validated exercise ID
            weight=args['weight'],
            reps=args['reps'],
            comment=args['comment'],
            workout_id=workout.id  # Use the validated workout ID
        )
        db.session.add(new_set)
        db.session.commit()

        return new_set, 201

    @ns_sets.doc('list_sets_for_workout')
    @ns_sets.marshal_list_with(set_model)
    @requires_auth(['admin', 'user'])
    def get(self, workoutID):
        """Lists all sets for a specific workout"""
        # Validate that the workout exists
        Workout.query.get_or_404(workoutID, description="Workout not found")

        # Get all sets with the specified workout ID
        sets = Set.query.filter_by(workout_id=workoutID).all()
        return sets


# Parser for updating a set
set_update_parser = reqparse.RequestParser()
set_update_parser.add_argument('reps', type=int, required=False, help='Number of repetitions')
set_update_parser.add_argument('weight', type=float, required=False, help='Weight used')
set_update_parser.add_argument('comment', type=str, required=False, help='A comment about the set')


@ns_sets.route('/<int:setID>/update')
class SetUpdate(Resource):
    @ns_sets.doc('update_set')
    @ns_sets.expect(set_update_parser)
    @ns_sets.marshal_with(set_model)
    @requires_auth(['admin', 'user'])
    def put(self, setID):
        """Update a set's reps, weight, and/or comment"""
        set_record = Set.query.get_or_404(setID, description="Set not found")
        args = set_update_parser.parse_args()

        if args['reps'] is not None:
            set_record.reps = args['reps']
        if args['weight'] is not None:
            set_record.weight = args['weight']
        if args['comment'] is not None:
            set_record.comment = args['comment']

        db.session.commit()
        return set_record


schema_version_model = api.model('SchemaVersion', {
    'id': fields.Integer(readOnly=True),
    'version': fields.String(required=True),
    'applied_on': fields.DateTime(readOnly=True),
    'description': fields.String
})

ns_schema = api.namespace('schema', description='Database schema versioning operations')

schema_version_parser = reqparse.RequestParser()
schema_version_parser.add_argument('version', type=str, required=True, help='The version string (e.g., "1.0.0")')
schema_version_parser.add_argument('description', type=str, required=True, help='A description of the changes')


@ns_schema.route('/add')
class SchemaVersionAdd(Resource):
    @ns_schema.doc('add_schema_version')
    @ns_schema.expect(schema_version_parser)
    @ns_schema.marshal_with(schema_version_model, code=201)
    @requires_auth(['admin'])
    def post(self):
        """Inserts a new schema version record"""
        args = schema_version_parser.parse_args()

        new_version = SchemaVersion(
            version=args['version'],
            description=args['description']
        )

        db.session.add(new_version)
        db.session.commit()

        return new_version, 201


ns_analytics = api.namespace('analytics', description='Analytical queries for lifting data')

# Model for a single set with calculated 1RM
analytical_set_model = api.model('AnalyticalSet', {
    'id': fields.Integer(readOnly=True),
    'weight': fields.Float(description='The weight of the set'),
    'reps': fields.Integer(description='The reps in the set'),
    'comment': fields.String(description='The comment for the set'),
    'one_rep_max': fields.Float(description='Calculated one-rep max (1RM) for the set')
})

# Model for the Personal Record (PR)
pr_model = api.model('PersonalRecord', {
    'max_weight_set_id': fields.Integer(description='The ID of the set with the max weight'),
    'max_weight': fields.Float(description='The max weight lifted for this exercise')
})

# Model for the overall analytical response
user_exercise_analytics_model = api.model('UserExerciseAnalytics', {
    'personal_record': fields.Nested(pr_model, description='The user\'s personal record for this exercise'),
    'all_sets': fields.List(fields.Nested(analytical_set_model),
                            description='All sets for this user and exercise, including 1RM calculation')
})


@ns_analytics.route('/sets/<int:setID>/calc1rm')
class Set1RM(Resource):
    @ns_analytics.doc('calculate_set_1rm')
    @requires_auth(['admin', 'user', 'report'])
    def get(self, setID):
        """
        Calculates the 1RM for a single set by its ID.
        """
        set_record = Set.query.get_or_404(setID, description="Set not found")
        one_rep_max = calculate_one_rep_max(set_record.weight, set_record.reps)

        return {
            'set_id': set_record.id,
            'one_rep_max': one_rep_max
        }


@ns_analytics.route('/users/<int:userID>/exercises/<int:exerciseID>/findpr')
class UserExercisePR(Resource):
    @ns_analytics.doc('find_pr_for_user_exercise')
    @ns_analytics.marshal_with(pr_model)
    @requires_auth(['admin', 'user', 'report'])
    def get(self, userID, exerciseID):
        """
        Finds the personal record for a user's exercise.
        """
        User.query.get_or_404(userID, description="User not found")
        Exercise.query.get_or_404(exerciseID, description="Exercise not found")

        sets = get_sets_for_exercise_and_user(userID, exerciseID)
        return find_pr(sets)


@ns_analytics.route('/users/<int:userID>/exercises/<int:exerciseID>/getsets')
class UserExerciseSets(Resource):
    @ns_analytics.doc('get_sets_for_user_exercise')
    @ns_analytics.marshal_list_with(set_model)
    @requires_auth(['admin', 'user', 'report'])
    def get(self, userID, exerciseID):
        """
        Retrieves all sets for a specific user and exercise.
        """
        User.query.get_or_404(userID, description="User not found")
        Exercise.query.get_or_404(exerciseID, description="Exercise not found")

        sets = get_sets_for_exercise_and_user(userID, exerciseID)
        return sets


if __name__ == '__main__':
    app.run(debug=True)