import React from 'react';
import './Modal.css'; // You'll need to create this CSS file

interface ModalProps {
    show: boolean;
    onClose: () => void;
    children: React.ReactNode;
    maxWidthClass?: string; 
}

const Modal = ({ show, onClose, children }: ModalProps) => {
    if (!show) {
        return null;
    }

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={e => e.stopPropagation()}>
                <button className="modal-close-button" onClick={onClose}>&times;</button>
                {children}
            </div>
        </div>
    );
};

export default Modal;