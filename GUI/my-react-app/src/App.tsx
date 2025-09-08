import React, { useState } from 'react';
import './App.css';
import ExercisesDropdown from './components/ExerciseDropdown';
import Modal from './components/Modal';
import AddWorkoutForm from './components/AddWorkoutForm'; // <-- Import the new component
import AddExerciseForm from './components/AddExerciseForm'; 

function App() {
    const [showExerciseModal, setShowExerciseModal] = useState(false);
    const [showWorkoutModal, setShowWorkoutModal] = useState(false);
    const [refreshKey, setRefreshKey] = useState(0);

    const handleAddExerciseSuccess  = () => {
        setShowExerciseModal(false);
        setRefreshKey(prevKey => prevKey + 1); 
    };

    const handleWorkoutAdded = () => {
        setShowWorkoutModal(false);
    };

    return (
        <div className="container">
            <h1>Lifting App</h1>
            <p>Welcome, Alex!</p>
            {/* Exercise Management Section */}
            <div className="exercise-management-pane">
                <h2>Exercise Management</h2>
                <button onClick={() => setShowExerciseModal(true)}>Add New Exercise</button>
                <ExercisesDropdown key={refreshKey} />
            </div>

            <hr /> {/* A horizontal line for visual separation */}
            
            {/* Workout Creation Section */}
            <div className="workout-creation-pane">
                <h2>Workout Creation</h2>
                <p>Create a new workout entry.</p>
                <button onClick={() => setShowWorkoutModal(true)}>Create Workout</button>
            </div>
            
            {/* Modals are rendered outside of the panes so they can be positioned properly */}
            <Modal show={showExerciseModal} onClose={() => setShowExerciseModal(false)}>
                <AddExerciseForm onAddSuccess={handleAddExerciseSuccess} /> 
            </Modal>

            <Modal show={showWorkoutModal} onClose={() => setShowWorkoutModal(false)}>
                <AddWorkoutForm onWorkoutAdded={handleWorkoutAdded} />
            </Modal>
        </div>
    );
}

export default App;