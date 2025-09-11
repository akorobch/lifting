import React, { useState } from 'react';

// Define the props interface
interface AddExerciseFormProps {
    onAddSuccess: () => void;
}

const AddExerciseForm: React.FC<AddExerciseFormProps> = ({ onAddSuccess }) => {
    const [name, setName] = useState<string>('');
    const [description, setDescription] = useState<string>('');
    const [message, setMessage] = useState<string>('');
    const [error, setError] = useState<string>('');

    const handleSubmit = async (e: React.FormEvent): Promise<void> => {
        e.preventDefault();
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

            // Call the prop function to notify the parent component
            onAddSuccess();

        } catch (err) {
            if (err instanceof Error) {
                setError(`Failed to add exercise: ${err.message}`);
            } else {
                setError('An unknown error occurred.');
            }
        }
    };

    const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
        setName(e.target.value);
    };

    const handleDescriptionChange = (e: React.ChangeEvent<HTMLTextAreaElement>): void => {
        setDescription(e.target.value);
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
                        onChange={handleNameChange}
                        required
                    />
                </div>
                <div>
                    <label htmlFor="description">Description:</label>
                    <textarea
                        id="description"
                        value={description}
                        onChange={handleDescriptionChange}
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