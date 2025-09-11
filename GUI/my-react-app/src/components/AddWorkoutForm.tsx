import React, { useState } from 'react';

// Define an interface for the component's props
interface AddWorkoutFormProps {
    onWorkoutAdded: () => void;
}

const AddWorkoutForm: React.FC<AddWorkoutFormProps> = ({ onWorkoutAdded }) => {
    const [comment, setComment] = useState<string>('');
    const [message, setMessage] = useState<string>('');
    const [error, setError] = useState<string>('');

    const handleSubmit = async (e: React.FormEvent): Promise<void> => {
        e.preventDefault();
        setMessage('');
        setError('');

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

    const handleCommentChange = (e: React.ChangeEvent<HTMLTextAreaElement>): void => {
        setComment(e.target.value);
    };

    return (
        <form onSubmit={handleSubmit}>
            <h3>Create Workout</h3>
            <div>
                <label htmlFor="comment">Comment:</label>
                <textarea
                    id="comment"
                    value={comment}
                    onChange={handleCommentChange}
                />
            </div>
            <button type="submit">Confirm</button>
            {message && <div className="success-message">{message}</div>}
            {error && <div className="error-message">{error}</div>}
        </form>
    );
};

export default AddWorkoutForm;