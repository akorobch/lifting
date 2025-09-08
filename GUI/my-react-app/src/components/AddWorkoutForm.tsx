import React, { useState } from 'react';

const AddWorkoutForm = ({ onWorkoutAdded }: { onWorkoutAdded: () => void }) => {
    const [comment, setComment] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setMessage('');
        setError('');

        // Construct the URL with optional parameters
        const baseUrl = 'http://localhost:5000/workouts/1/add';
        const url = `${baseUrl}?comment=${encodeURIComponent(comment)}`;

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

            setMessage('Workout added successfully!');
            setComment('');
            onWorkoutAdded();
            
        } catch (err) {
            if (err instanceof Error) {
                setError(`Failed to add workout: ${err.message}`);
            } else {
                setError('An unknown error occurred.');
            }
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <h3>Create Workout</h3>
            {/* The date is optional and handled on the backend based on your curl command. */}
            <div>
                <label htmlFor="comment">Comment:</label>
                <textarea
                    id="comment"
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                />
            </div>
            <button type="submit">Confirm</button>
            {message && <div className="success-message">{message}</div>}
            {error && <div className="error-message">{error}</div>}
        </form>
    );
};

export default AddWorkoutForm;