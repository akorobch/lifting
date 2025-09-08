import React, { useState } from 'react';
import './App.css';
import ExercisesDropdown from './components/ExerciseDropdown';
import Modal from './components/Modal';

import AddExerciseForm from './components/AddExerciseForm'; 

function App() {
    const [showModal, setShowModal] = useState(false);
    const [refreshKey, setRefreshKey] = useState(0); 

    const handleAddSuccess = () => {
        setShowModal(false);
        setRefreshKey(prevKey => prevKey + 1); 
    };

    return (
        <div className="container">
            <h1>Lifting App</h1>
            <p>Welcome, Alex!</p>
            <button onClick={() => setShowModal(true)}>Add New Exercise</button>
            
            {/* Replace the table with the new dropdown component */}
            <ExercisesDropdown key={refreshKey} />
            
            <Modal show={showModal} onClose={() => setShowModal(false)}>
                {/* The form logic can be placed here or in a separate file */}
                <AddExerciseForm onAddSuccess={handleAddSuccess} /> 
            </Modal>
        </div>
    );
}

export default App;