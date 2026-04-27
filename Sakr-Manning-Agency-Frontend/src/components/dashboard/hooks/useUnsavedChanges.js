// hooks/useUnsavedChanges.js
import { useEffect } from 'react';
/**

useUnsavedChanges - Warns user about unsaved changes
Shows browser confirmation when leaving page with unsaved data

@param {boolean} isDirty - Whether there are unsaved changes
@param {string} message - Custom warning message (optional)

@example
const [isDirty, setIsDirty] = useState(false);
useUnsavedChanges(isDirty);
*/
export function useUnsavedChanges(isDirty, message = 'You have unsaved changes. Are you sure you want to leave?') {
    useEffect(() => {
        if (!isDirty) return;
        const handleBeforeUnload = (event) => {
            event.preventDefault();
            event.returnValue = message; // Required for Chrome
            return message; // Required for other browsers
        };
        window.addEventListener('beforeunload', handleBeforeUnload);
        return () => {
            window.removeEventListener('beforeunload', handleBeforeUnload);
        };
    }, [isDirty, message]);
}
