// hooks/useFocusTrap.js
import { useEffect } from 'react';
/**

useFocusTrap - Traps focus within a modal or dialog
Ensures keyboard navigation stays within the component

@param {React.RefObject} ref - Ref to the container element
@param {boolean} isActive - Whether the trap is active

@example
const modalRef = useRef(null);
useFocusTrap(modalRef, isOpen);
*/
export function useFocusTrap(ref, isActive) {
    useEffect(() => {
        if (!isActive) return;
        const element = ref.current;
        if (!element) return;
        // Get all focusable elements
        const focusableSelector = [
            'button:not([disabled])',
            '[href]',
            'input:not([disabled])',
            'select:not([disabled])',
            'textarea:not([disabled])',
            '[tabindex]:not([tabindex="-1"])',
        ].join(', ');
        const focusableElements = element.querySelectorAll(focusableSelector);
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        // Handle tab key
        const handleTab = (e) => {
            if (e.key !== 'Tab') return;
            if (e.shiftKey) {
                // Shift + Tab
                if (document.activeElement === firstElement) {
                    e.preventDefault();
                    lastElement?.focus();
                }
            } else {
                // Tab
                if (document.activeElement === lastElement) {
                    e.preventDefault();
                    firstElement?.focus();
                }
            }
        };
        // Focus first element on mount
        firstElement?.focus();
        element.addEventListener('keydown', handleTab);
        return () => {
            element.removeEventListener('keydown', handleTab);
        };
    }, [ref, isActive]);
}


