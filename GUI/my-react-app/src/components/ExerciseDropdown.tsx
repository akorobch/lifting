import React, { useState, useEffect } from 'react';

// Define a type for a single exercise object
interface Exercise {
    id: number;
    name: string;
    description: string;
}

const ExercisesDropdown = () => {
    const [exercises, setExercises] = useState<Exercise[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);
    const [selectedExercise, setSelectedExercise] = useState<Exercise | null>(null);

    useEffect(() => {
        const fetchExercises = async () => {
            try {
                const response = await fetch('http://127.0.0.1:5000/exercises/', {
                    headers: {
                        'X-User-ID': '1',
                        'X-User-Role': 'admin'
                    }
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data: Exercise[] = await response.json();
                
                // Sort the data by exercise name
                const sortedData = data.sort((a, b) => a.name.localeCompare(b.name));
                
                setExercises(sortedData);
            } catch (error) {
                if (error instanceof Error) {
                    setError(error);
                } else {
                    setError(new Error('An unknown error occurred.'));
                }
            } finally {
                setLoading(false);
            }
        };

        fetchExercises();
    }, []);

    const handleSelectChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        const selectedId = parseInt(event.target.value);
        const exercise = exercises.find(ex => ex.id === selectedId);
        if (exercise) {
            setSelectedExercise(exercise);
        }
    };

    if (loading) {
        return <div>Loading exercises...</div>;
    }

    if (error) {
        return <div>Error: {error.message}</div>;
    }

    return (
        <div className="exercises-dropdown">
            <h2>Select an Exercise</h2>
            <select onChange={handleSelectChange} defaultValue="">
                <option value="" disabled>Select an exercise...</option>
                {exercises.map((exercise) => (
                    <option key={exercise.id} value={exercise.id}>
                        {exercise.name}
                    </option>
                ))}
            </select>
            {selectedExercise && (
                <div className="exercise-details">
                    <h3>{selectedExercise.name}</h3>
                    <p>{selectedExercise.description}</p>
                </div>
            )}
        </div>
    );
};

export default ExercisesDropdown;