from models import db, Workout, Set

def calculate_one_rep_max(weight, reps):
	"""
	Calculates the 1RM for a single set using the Epley formula.
	"""
	if weight is not None and reps is not None and reps > 0:
		# Epley formula: 1RM = w * (1 + r/30)
		return round(weight * (1 + reps / 30), 2)
	return None


def find_pr(sets):
	"""
	Finds the personal record (PR) for an exercise from a list of sets.
	"""
	pr_weight = 0.0
	pr_set_id = None

	for s in sets:
		if s.weight is not None and s.weight > pr_weight:
			pr_weight = s.weight
			pr_set_id = s.id

	return {
		'max_weight_set_id': pr_set_id,
		'max_weight': pr_weight
	}


def get_sets_for_exercise_and_user(user_id, exercise_id):
	"""
	Retrieves all sets for a specific exercise and user.
	"""
	sets = db.session.query(Set).join(Workout).filter(
		Workout.user_id == user_id,
		Set.exercise_id == exercise_id
	).all()
	return sets
