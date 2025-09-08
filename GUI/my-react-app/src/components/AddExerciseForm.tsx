import React, { useState } from 'react';

const AddExerciseForm = () => {
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault(); // Prevents the default form submission behavior
        setMessage('');
        setError('');

        if (!name || !description) {
            setError('Both name and description are required.');
            return;
        }

        const url = `http://localhost:5000/exercises/?name=${encodeURIComponent(name)}&description=${encodeURIComponent(description)}`;

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'accept': 'application/json',
                    'X-User-Role': 'admin',
                    'X-User-ID': '1'
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            setMessage('Exercise added successfully!');
            setName('');
            setDescription('');

        } catch (err) {
            if (err instanceof Error) {
                setError(`Failed to add exercise: ${err.message}`);
            } else {
                setError('An unknown error occurred.');
            }
        }
    };

    return (
        <div className="add-exercise-form">
            <h2>Add New Exercise</h2>
            <form onSubmit={handleSubmit}>
                <div>
                    <label htmlFor="name">Exercise Name:</label>
                    <input
                        id="name"
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label htmlFor="description">Description:</label>
                    <textarea
                        id="description"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        required
                    />
                </div>
                <button type="submit">Add Exercise</button>
            </form>
            {message && <div className="success-message">{message}</div>}
            {error && <div className="error-message">{error}</div>}
        </div>
    );
};

export default AddExerciseForm;