import React, { useState } from 'react';
//import ExercisesDropdown from './components/ExerciseDropdown';
import Modal from './components/Modal';
import AddWorkoutForm from './components/AddWorkoutForm';
import AddExerciseForm from './components/AddExerciseForm';
import WorkoutList from './components/WorkoutList';
import './index.css';

const App: React.FC = () => {
    const [showExerciseModal, setShowExerciseModal] = useState<boolean>(false);
    const [showWorkoutModal, setShowWorkoutModal] = useState<boolean>(false);
    const [refreshKey, setRefreshKey] = useState<number>(0);

    const handleAddExerciseSuccess = (): void => {
        setShowExerciseModal(false);
        setRefreshKey(prevKey => prevKey + 1);
    };

    const handleWorkoutAdded = (): void => {
        setShowWorkoutModal(false);
        // We also need to refresh the workout list after a new workout is added
        // The WorkoutList component depends on `refreshKey` to re-fetch data
        setRefreshKey(prevKey => prevKey + 1);
    };

    return (
        <div className="flex flex-col items-center p-6 bg-gray-100 min-h-screen font-inter text-gray-800">
            <div className="w-full max-w-4xl p-8 bg-white rounded-xl shadow-lg">
                <h1 className="text-4xl font-bold text-center text-blue-600 mb-2">Lifting App</h1>
                <p className="text-center text-lg text-gray-600 mb-8">Welcome, Alex!</p>
                
                {/* Exercise Management Section */}
                <div className="bg-blue-50 p-6 rounded-lg mb-6 shadow-sm border border-blue-200">
                    <h2 className="text-2xl font-semibold mb-3 text-blue-700">Exercise Management</h2>
                    <button 
                        onClick={() => setShowExerciseModal(true)}
                        className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                    >
                        Add New Exercise
                    </button>
                </div>

                <hr className="my-6 border-gray-300" />
                
                {/* Workout Creation Section */}
                <div className="bg-green-50 p-6 rounded-lg mb-6 shadow-sm border border-green-200">
                    <h2 className="text-2xl font-semibold mb-3 text-green-700">Workout Creation</h2>
                    <p className="text-gray-600 mb-4">Create a new workout entry.</p>
                    <button
                        onClick={() => setShowWorkoutModal(true)}
                        className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                    >
                        Create Workout
                    </button>
                </div>

                <hr className="my-6 border-gray-300" />

                {/* Workout List Section */}
                <div className="bg-gray-50 p-6 rounded-lg shadow-sm border border-gray-200">
                    <WorkoutList refreshKey={refreshKey} />
                </div>
                
                {/* Modals are rendered outside of the panes so they can be positioned properly */}
                <Modal show={showExerciseModal} onClose={() => setShowExerciseModal(false)}>
                    <AddExerciseForm onAddSuccess={handleAddExerciseSuccess} />
                </Modal>

                <Modal show={showWorkoutModal} onClose={() => setShowWorkoutModal(false)}>
                    <AddWorkoutForm onWorkoutAdded={handleWorkoutAdded} />
                </Modal>
            </div>
        </div>
    );
};

export default App;