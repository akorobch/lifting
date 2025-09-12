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
        <form onSubmit={handleSubmit} className="p-4 bg-white shadow-md rounded-lg max-w-sm mx-auto">
            <h3 className="text-xl font-semibold mb-4 text-center">Create Workout</h3>
            
            <div className="mb-4">
                <label htmlFor="comment" className="block text-gray-700 text-sm font-bold mb-2">
                    Comment:
                </label>
                <textarea
                    id="comment"
                    value={comment}
                    onChange={handleCommentChange}
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                />
            </div>
            
            <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors w-full"

            >
                Confirm
            </button>
            
            {message && <div className="mt-4 text-green-600 text-center font-bold">{message}</div>}
            {error && <div className="mt-4 text-red-600 text-center font-bold">{error}</div>}
        </form>
    );
};

export default AddWorkoutForm;