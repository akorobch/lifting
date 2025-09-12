import React, { useState, useEffect } from 'react';
import Modal from './Modal'; 
import ConfirmationModal from './ConfirmationModal';

// Define TypeScript interfaces for your data structures
interface Workout {
    id: number;
    workout_date: string;
    comment: string;
}

interface Set {
    id: number;
    exercise_id: number;
    weight: number;
    reps: number;
    comment: string;
    workout_id: number;
}

interface Exercise {
    id: number;
    name: string;
    description: string;
}

interface WorkoutListProps {
    refreshKey: number;
}

interface EditFormState {
    reps: number | '';
    weight: number | '';
    comment: string;
}

const WorkoutList: React.FC<WorkoutListProps> = ({ refreshKey }) => {
    const [workouts, setWorkouts] = useState<Workout[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [showWorkoutDetailsModal, setShowWorkoutDetailsModal] = useState<boolean>(false);
    const [selectedWorkoutId, setSelectedWorkoutId] = useState<number | null>(null);
    const [sets, setSets] = useState<Set[]>([]);
    const [isFetchingSets, setIsFetchingSets] = useState<boolean>(false);

    const [exercises, setExercises] = useState<Exercise[]>([]);
    const [isFetchingExercises, setIsFetchingExercises] = useState<boolean>(true);
    const [exerciseFetchError, setExerciseFetchError] = useState<string | null>(null);

    // State for the new set editing modal
    const [showEditSetModal, setShowEditSetModal] = useState<boolean>(false);
    const [selectedSet, setSelectedSet] = useState<Set | null>(null);
    const [editForm, setEditForm] = useState<EditFormState>({ reps: '', weight: '', comment: '' });
    const [successMessage, setSuccessMessage] = useState<string>('');
    const [newSetForm, setNewSetForm] = useState({
        exercise_id: '',
        weight: '',
        reps: '',
        comment: ''
    });

    const [showConfirmDelete, setShowConfirmDelete] = useState<boolean>(false);
    const [workoutToDelete, setWorkoutToDelete] = useState<number | null>(null);

    const userId: number = 1;

    // useEffect to fetch workouts
    useEffect(() => {
        const fetchWorkouts = async () => {
            setIsLoading(true);
            try {
                const headers = {
                    'X-User-Role': 'user',
                    'X-User-ID': userId.toString()
                };
                const response = await fetch(`http://127.0.0.1:5000/workouts/${userId}/get`, { headers });
                if (!response.ok) {
                    throw new Error('Failed to fetch workouts.');
                }
                const data: Workout[] = await response.json();
                setWorkouts(data);
            } catch (error) {
                console.error("Failed to fetch workouts:", error);
                setWorkouts([]);
            } finally {
                setIsLoading(false);
            }
        };

        fetchWorkouts();
    }, [refreshKey]);

    // NEW: useEffect to fetch exercises once on component mount
    useEffect(() => {
        const fetchExercises = async () => {
            setIsFetchingExercises(true);
            setExerciseFetchError(null);
            try {
                const response = await fetch('http://127.0.0.1:5000/exercises/', {
                    headers: {
                        'X-User-ID': '1',
                        'X-User-Role': 'admin'
                    }
                });

                if (!response.ok) {
                    throw new Error(`Failed to fetch exercises with status: ${response.status}`);
                }
                
                const data: Exercise[] = await response.json();
                const sortedData = data.sort((a, b) => a.name.localeCompare(b.name));
                setExercises(sortedData);
            } catch (error) {
                if (error instanceof Error) {
                    setExerciseFetchError(error.message);
                } else {
                    setExerciseFetchError('An unknown error occurred while fetching exercises.');
                }
                console.error("Failed to fetch exercises:", error);
                setExercises([]);
            } finally {
                setIsFetchingExercises(false);
            }
        };
        fetchExercises();
    }, []);


    // Find the exercise name from its ID
    const getExerciseName = (exerciseId: number): string => {
        const exercise = exercises.find(ex => ex.id === exerciseId);
        return exercise ? exercise.name : 'Unknown Exercise';
    };

    const fetchSetsForWorkout = async (workoutId: number) => {
        setIsFetchingSets(true);
        try {
            const headers = {
                'X-User-Role': 'user',
                'X-User-ID': userId.toString()
            };
            const response = await fetch(`http://127.0.0.1:5000/sets/${workoutId}`, { headers });
            if (!response.ok) {
                throw new Error('Failed to fetch sets.');
            }
            const data: Set[] = await response.json();
            setSets(data);
        } catch (error) {
            console.error("Failed to fetch sets:", error);
            setSets([]);
        } finally {
            setIsFetchingSets(false);
        }
    };

    const handleRowClick = (workoutId: number) => {
        setSelectedWorkoutId(workoutId);
        fetchSetsForWorkout(workoutId);
        setShowWorkoutDetailsModal(true);
    };

    const handleDeleteWorkout = async (workoutId: number) => {
        if (!window.confirm("Are you sure you want to delete this workout? This action cannot be undone.")) {
            return;
        }

        try {
            const response = await fetch(`http://127.0.0.1:5000/workouts/${workoutId}/delete`, {
                method: 'DELETE',
                headers: {
                    'X-User-Role': 'admin',
                    'X-User-ID': userId.toString()
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Remove the deleted workout from the state
            setWorkouts(workouts.filter(w => w.id !== workoutId));

        } catch (error) {
            console.error("Failed to delete workout:", error);
            alert("An error occurred while deleting the workout. Please try again.");
        }
    };

    const handleDeleteConfirmed = async () => {
        if (workoutToDelete === null) return;

        try {
            const response = await fetch(`http://127.0.0.1:5000/workouts/${workoutToDelete}/delete`, {
                method: 'DELETE',
                headers: {
                    'X-User-Role': 'admin',
                    'X-User-ID': userId.toString()
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            setWorkouts(workouts.filter(w => w.id !== workoutToDelete));
            setShowConfirmDelete(false); // Hide the modal after deletion
            setWorkoutToDelete(null); // Reset the state
            
        } catch (error) {
            console.error("Failed to delete workout:", error);
            alert("An error occurred while deleting the workout. Please try again.");
            setShowConfirmDelete(false);
        }
    };

    // New function to show the confirmation modal
    const handleDeleteClick = (workoutId: number) => {
        setWorkoutToDelete(workoutId);
        setShowConfirmDelete(true);
    };

    const handleSetRowClick = (set: Set) => {
        setSelectedSet(set);
        setEditForm({ 
            reps: set.reps, 
            weight: set.weight, 
            comment: set.comment 
        });
        setShowEditSetModal(true);
    };

    const handleDeleteSet = async (setId: number) => {
        if (!window.confirm("Are you sure you want to delete this set?")) {
            return;
        }

        try {
            const response = await fetch(`http://localhost:5000/sets/${setId}/delete`, {
                method: 'DELETE',
                headers: {
                    'X-User-Role': 'admin',
                    'X-User-ID': userId.toString()
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Update the state to remove the deleted set
            setSets(sets.filter(s => s.id !== setId));

            setSelectedSet(null); 
            setShowEditSetModal(false);

        } catch (error) {
            console.error("Failed to delete set:", error);
            alert("An error occurred while deleting the set. Please try again.");
        }
    };

    const handleFormChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        if (name === 'reps' || name === 'weight') {
            setEditForm(prev => ({
            ...prev,
            [name]: value === '' ? '' : Number(value)
        }));
        } else {
            setEditForm(prev => ({
                ...prev,
                [name]: value
            }));
        }
    };

    const handleNewSetFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setNewSetForm(prev => ({ ...prev, [name]: value }));
    };

    const handleNewSetSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedWorkoutId || !newSetForm.exercise_id || !newSetForm.weight || !newSetForm.reps) {
            alert("Please fill in all required fields (Exercise, Weight, Reps).");
            return;
        }

        const queryParams = new URLSearchParams({
            exercise_id: newSetForm.exercise_id,
            weight: newSetForm.weight,
            reps: newSetForm.reps,
            comment: newSetForm.comment
        }).toString();

        try {
            const response = await fetch(`http://localhost:5000/sets/${selectedWorkoutId}?${queryParams}`, {
                method: 'POST',
                headers: {
                    'accept': 'application/json',
                    'X-User-Role': 'admin',
                    'X-User-ID': userId.toString()
                },
                body: ''
            });

            if (!response.ok) {
                throw new Error('Failed to add new set.');
            }

            setNewSetForm({
                exercise_id: '',
                weight: '',
                reps: '',
                comment: ''
            });
            await fetchSetsForWorkout(selectedWorkoutId);

        } catch (error) {
            console.error("Failed to add new set:", error);
        }
    };

    const handleEditSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSuccessMessage('');

        if (!selectedSet) {
            console.error("No set selected for editing.");
            setSuccessMessage('Error: No set selected for update.');
            return;
        }

        const setId = selectedSet.id;

        const queryParams = new URLSearchParams({
            reps: editForm.reps.toString(),
            weight: editForm.weight.toString(),
            comment: editForm.comment
        }).toString();

        try {
            const response = await fetch(`http://localhost:5000/sets/${setId}/update?${queryParams}`, {
                method: 'PUT',
                headers: {
                    'accept': 'application/json',
                    'X-User-Role': 'admin',
                    'X-User-ID': userId.toString()
                }
            });

            if (!response.ok) {
                throw new Error('Failed to update set.');
            }

            setSuccessMessage('Set updated successfully!');
            await fetchSetsForWorkout(selectedWorkoutId!);

            setTimeout(() => {
                setShowEditSetModal(false);
                setSuccessMessage('');
            }, 1500);

        } catch (error) {
            console.error("Failed to update set:", error);
            setSuccessMessage('Error updating set.');
        }
    };
    
    // Main component render
    if (isLoading) {
        return <p>Loading workouts...</p>;
    }

    if (workouts.length === 0) {
        return <p>No workouts found. Start by creating a new workout!</p>;
    }

    return (
        <div className="overflow-x-auto">
            <h3 className="text-xl font-semibold mb-2">My Workouts</h3>
            <table className="min-w-full divide-y divide-gray-200 shadow-md rounded-lg">
                <thead className="bg-gray-50">
                    <tr>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Comment</th>
                    </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                    {workouts.map(workout => (
                        <tr
                            key={workout.id}
                            onClick={() => handleRowClick(workout.id)}
                            className="cursor-pointer hover:bg-gray-100 transition-colors"
                        >
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(workout.workout_date).toLocaleString()}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{workout.comment}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation(); // Stop the click from bubbling up to the row
                                        handleDeleteClick(workout.id);
                                    }}
                                    className="text-red-600 hover:text-red-900 font-bold"
                                >
                                    X
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
            
            <Modal
                show={showWorkoutDetailsModal}
                onClose={() => setShowWorkoutDetailsModal(false)}
                // 🆕 NEW: Pass the width class directly to the Modal component
                maxWidthClass="max-w-2xl"
            >
                <div className="p-4">
                    <h3 className="text-lg font-bold mb-2">Sets for Workout #{selectedWorkoutId}</h3>
                    
                    <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
                        <h4 className="text-md font-semibold mb-2">Add New Set</h4>
                        <form onSubmit={handleNewSetSubmit}>
                            <div className="grid grid-cols-3 gap-4 mb-4">
                                {/* NEW: Exercise dropdown */}
                                <div>
                                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="new-set-exercise-id">Exercise</label>
                                    <select
                                        id="new-set-exercise-id"
                                        name="exercise_id"
                                        value={newSetForm.exercise_id}
                                        onChange={handleNewSetFormChange}
                                        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700"
                                        required
                                        disabled={isFetchingExercises || !!exerciseFetchError}
                                    >
                                        <option value="" disabled>
                                            {isFetchingExercises ? "Loading exercises..." : "Select an exercise..."}
                                        </option>
                                        {exerciseFetchError ? (
                                            <option value="" disabled>Error loading exercises</option>
                                        ) : (
                                            exercises.map((exercise) => (
                                                <option key={exercise.id} value={exercise.id}>
                                                    {exercise.name}
                                                </option>
                                            ))
                                        )}
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="new-set-weight">Weight</label>
                                    <input
                                        type="number"
                                        id="new-set-weight"
                                        name="weight"
                                        value={newSetForm.weight}
                                        onChange={handleNewSetFormChange}
                                        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="new-set-reps">Reps</label>
                                    <input
                                        type="number"
                                        id="new-set-reps"
                                        name="reps"
                                        value={newSetForm.reps}
                                        onChange={handleNewSetFormChange}
                                        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700"
                                        required
                                    />
                                </div>
                                <div className="col-span-3">
                                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="new-set-comment">Comment</label>
                                    <textarea
                                        id="new-set-comment"
                                        name="comment"
                                        value={newSetForm.comment}
                                        onChange={handleNewSetFormChange}
                                        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700"
                                    />
                                </div>
                            </div>
                            <div className="flex justify-end">
                                <button
                                    type="submit"
                                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                                    disabled={isFetchingExercises || !!exerciseFetchError}
                                >
                                    Add Set
                                </button>
                            </div>
                        </form>
                    </div>

                    {isFetchingSets ? (
                        <p>Loading sets...</p>
                    ) : sets.length === 0 ? (
                        <p>No sets found for this workout.</p>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200 shadow-md rounded-lg">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Exercise</th>
                                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Weight</th>
                                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Reps</th>
                                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Comment</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {sets.map(set => (
                                        <tr
                                            key={set.id}
                                            onClick={() => handleSetRowClick(set)}
                                            className="cursor-pointer hover:bg-gray-100 transition-colors"
                                        >
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{getExerciseName(set.exercise_id)}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{set.weight}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{set.reps}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{set.comment}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                                <button
                                                    onClick={(e) => {
                                                        // 🆕 NEW: Stop the click from triggering the row's handler
                                                        e.stopPropagation(); 
                                                        handleDeleteSet(set.id);
                                                    }}
                                                    className="text-red-600 hover:text-red-900 font-bold"
                                                >
                                                    X
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                    <div className="mt-4 flex justify-end">
                        <button
                            onClick={() => setShowWorkoutDetailsModal(false)}
                            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                        >
                            Close
                        </button>
                    </div>
                </div>
            </Modal>

            <Modal 
                key={selectedSet?.id || 'edit-set-modal'} 
                show={showEditSetModal} 
                onClose={() => { setShowEditSetModal(false); setSelectedSet(null); }}
            >
                <div className="p-4">
                    <h3 className="text-lg font-bold mb-4">Edit Set #{selectedSet?.id}</h3>
                    {successMessage && (
                        <p className={`mb-4 text-center font-bold ${successMessage.includes('successfully') ? 'text-green-600' : 'text-red-600'}`}>
                            {successMessage}
                        </p>
                    )}
                    <form onSubmit={handleEditSubmit}>
                        <div className="mb-4">
                            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="reps">Reps</label>
                            <input
                                type="number"
                                name="reps"
                                value={editForm.reps}
                                onChange={handleFormChange}
                                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                            />
                        </div>
                        <div className="mb-4">
                            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="weight">Weight</label>
                            <input
                                type="number"
                                name="weight"
                                value={editForm.weight}
                                onChange={handleFormChange}
                                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                            />
                        </div>
                        <div className="mb-6">
                            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="comment">Comment</label>
                            <input
                                type="text"
                                name="comment"
                                value={editForm.comment}
                                onChange={handleFormChange}
                                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                            />
                        </div>
                        <div className="flex items-center justify-between">
                            <button
                                type="submit"
                                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                            >
                                Update Set
                            </button>
                            <button
                                type="button"
                                onClick={() => setShowEditSetModal(false)}
                                className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                            >
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            </Modal>

            <ConfirmationModal
                show={showConfirmDelete}
                onConfirm={handleDeleteConfirmed}
                onCancel={() => setShowConfirmDelete(false)}
                message="Are you sure you want to delete this workout? This action cannot be undone."
            />
        </div>
    );
};

export default WorkoutList;