from flask import Flask
from flask_restx import Api, Resource, fields
from models import db, User, Exercise
from flask_restx import reqparse

# Initialize Flask and SQLAlchemy
app = Flask(__name__)
# Configure a simple SQLite database for local testing
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lifting.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RESTX_MASK_SWAGGER'] = False  # Allows full API doc in Swagger

db.init_app(app)
api = Api(app, version='1.0', title='Lifting API', description='API for tracking lifting workouts', doc='/swagger/')

# Create the database tables
with app.app_context():
    db.create_all()

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
    def get(self):
        """List all users"""
        users = User.query.all()
        return users

# A new namespace to handle single user resources
@ns_users.route('/<int:id>/enable')
class UserEnable(Resource):
    @ns_users.doc('enable_user')
    @ns_users.marshal_with(user_model)
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

if __name__ == '__main__':
    app.run(debug=True)