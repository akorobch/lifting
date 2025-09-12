import React from 'react';
import Modal from './Modal'; // Assuming you have a Modal component

interface ConfirmationModalProps {
    show: boolean;
    onConfirm: () => void;
    onCancel: () => void;
    message: string;
}

const ConfirmationModal: React.FC<ConfirmationModalProps> = ({ show, onConfirm, onCancel, message }) => {
    return (
        <Modal show={show} onClose={onCancel}>
            <div className="p-4 text-center">
                <h3 className="text-xl font-bold mb-4">Lifting App</h3>
                <p className="mb-6">{message}</p>
                <div className="flex justify-center space-x-4">
                    <button
                        onClick={onConfirm}
                        className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                    >
                        Confirm
                    </button>
                    <button
                        onClick={onCancel}
                        className="px-4 py-2 bg-gray-300 text-gray-800 rounded-md hover:bg-gray-400 transition-colors"
                    >
                        Cancel
                    </button>
                </div>
            </div>
        </Modal>
    );
};

export default ConfirmationModal;