import React, { useState, useEffect } from 'react';

const ExercisesTable = () => {
    const [exercises, setExercises] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

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
                
                const data = await response.json();
                setExercises(data);
            } catch (error) {
                setError(error);
            } finally {
                setLoading(false);
            }
        };

        fetchExercises();
    }, []); // The empty array ensures this effect runs only once

    if (loading) {
        return <div>Loading exercises...</div>;
    }

    if (error) {
        return <div>Error: {error.message}</div>;
    }

    return (
        <div>
            <h2>Exercises</h2>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    {exercises.map((exercise: any) => (
                        <tr key={exercise.id}>
                            <td>{exercise.name}</td>
                            <td>{exercise.description}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default ExercisesTable;
