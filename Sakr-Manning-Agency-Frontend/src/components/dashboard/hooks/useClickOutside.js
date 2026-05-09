// hooks/useClickOutside.js
import { useEffect } from 'react';
/**

useClickOutside - Detects clicks outside a component
Useful for closing dropdowns, modals, menus

@param {React.RefObject} ref - Ref to the element
@param {Function} handler - Callback when clicking outside
@param {boolean} isActive - Whether the listener is active

@example
const dropdownRef = useRef(null);
useClickOutside(dropdownRef, () => setIsOpen(false), isOpen);
*/
export function useClickOutside(ref, handler, isActive = true) {
    useEffect(() => {
        if (!isActive) return;
        const handleClickOutside = (event) => {
            // Ignore clicks that land inside a portalled dropdown (Select / MultiSelect).
            // Those are appended to document.body so they're always "outside" any modal
            // ref, but they should not trigger an outside-click close.
            if (event.target.closest('[data-portal-dropdown]')) return;

            if (ref.current && !ref.current.contains(event.target)) {
                handler(event);
            }
        };
        // Use mousedown instead of click for better UX
        // (prevents closing when dragging from inside to outside)
        document.addEventListener('mousedown', handleClickOutside);
        document.addEventListener('touchstart', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
            document.removeEventListener('touchstart', handleClickOutside);
        };
    }, [ref, handler, isActive]);
}
