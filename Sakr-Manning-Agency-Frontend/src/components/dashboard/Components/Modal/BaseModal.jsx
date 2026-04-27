
// components/dashboard/Common/BaseModal.jsx
import React, { useEffect, useRef } from 'react';
import { X } from 'lucide-react';
import { useFocusTrap } from '../../hooks/useFocusTrap';
import { useClickOutside } from '../../hooks/useClickOutside';
import useKeyboardShortcuts from '../../hooks/useKeyboardShortcuts';
import { getModalTitleStyles } from '../../Styles/cssClasses';
import { getModalStyles } from "../../Styles/componentStyles";

/** 
@param {boolean} isOpen - Controls modal visibility
@param {function} onClose - Close handler
@param {string} title - Modal title
@param {string} subtitle - Optional subtitle
@param {string} size - Modal size: 'sm' (400px), 'md' (600px), 'lg' (800px), 'xl' (1000px)
@param {ReactNode} children - Modal content
@param {ReactNode} footer - Optional footer content
@param {boolean} closeOnOverlayClick - Allow closing by clicking overlay (default: true)
@param {boolean} closeOnEscape - Allow closing with ESC key (default: true)
@param {boolean} showCloseButton - Show X button (default: true)
@param {number} scale - Scale factor for responsive design
@param {string} className - Additional CSS classes
*/
export function BaseModal({
    isOpen,
    onClose,
    title,
    subtitle,
    size = 'md',
    children,
    footer,
    closeOnOverlayClick = true,
    closeOnEscape = true,
    showCloseButton = true,
    scale = 1,
    className = '',
}) {
    const modalRef = useRef(null);
    const modalStyles = getModalStyles(scale);
    const titleStyles = getModalTitleStyles(scale);

    // Focus trap
    useFocusTrap(modalRef, isOpen);
    // Click outside to close
    useClickOutside(
        modalRef,
        () => {
            if (closeOnOverlayClick) onClose();
        },
        isOpen
    );
    // Keyboard shortcuts
    useKeyboardShortcuts(
        {
            Escape: () => {
                if (closeOnEscape) onClose();
            },
        },
        isOpen
    );
    // Prevent body scroll when modal is open
    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
        return () => {
            document.body.style.overflow = '';
        };
    }, [isOpen]);
    if (!isOpen) return null;
    // Size mapping
    const sizeMap = {
        sm: 400,
        md: 600,
        lg: 800,
        xl: 1000,
    };
    const maxWidth = `${Math.round((sizeMap[size] || 600) * scale)}px`;
    return (
        <div
            style={{
                ...modalStyles.overlay,
                animation: 'fadeIn 0.2s ease-out',
            }}
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-title"
            onClick={(e) => {
                // Only close if clicking directly on overlay
                if (e.target === e.currentTarget && closeOnOverlayClick) {
                    onClose();
                }
            }}
        >
            <style>
                { /*
@keyframes fadeIn {from { opacity: 0; } to { opacity: 1; } } @keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }}
*/}
            </style>
            <div
                ref={modalRef}
                style={{
                    ...modalStyles.panel,
                    maxWidth,
                    animation: 'slideUp 0.3s ease-out',
                }}
                className={className}
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div
                    style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'flex-start',
                        marginBottom: subtitle ? `${Math.round(12 * scale)}px` : `${Math.round(20 * scale)}px`,
                    }}
                >
                    <div style={{ flex: 1 }}>
                        <h2 id="modal-title" style={titleStyles}>
                            {title}
                        </h2>
                        {subtitle && (
                            <p
                                style={{
                                    margin: 0,
                                    marginTop: `${Math.round(4 * scale)}px`,
                                    fontSize: `${Math.round(14 * scale)}px`,
                                    color: '#6B7280',
                                    fontFamily: 'Inter, sans-serif',
                                }}
                            >
                                {subtitle}
                            </p>
                        )}
                    </div>

                    {showCloseButton && (
                        <button
                            onClick={onClose}
                            aria-label="Close modal"
                            style={{
                                background: 'transparent',
                                border: 'none',
                                cursor: 'pointer',
                                padding: `${Math.round(4 * scale)}px`,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                borderRadius: `${Math.round(6 * scale)}px`,
                                transition: 'background-color 0.2s',
                                marginLeft: `${Math.round(8 * scale)}px`,
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.backgroundColor = '#F3F4F6';
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.backgroundColor = 'transparent';
                            }}
                        >
                            <X size={Math.round(20 * scale)} color="#6B7280" />
                        </button>
                    )}
                </div>

                {/* Body */}
                <div
                    style={{
                        flex: 1,
                        overflowY: 'auto',
                        marginBottom: footer ? `${Math.round(20 * scale)}px` : 0,
                    }}
                >
                    {children}
                </div>

                {/* Footer */}
                {footer && (
                    <div
                        style={{
                            borderTop: '1px solid #E5E7EB',
                            paddingTop: `${Math.round(16 * scale)}px`,
                            marginTop: `${Math.round(16 * scale)}px`,
                        }}
                    >
                        {footer}
                    </div>
                )}
            </div>
        </div>
    );
}

export default BaseModal;