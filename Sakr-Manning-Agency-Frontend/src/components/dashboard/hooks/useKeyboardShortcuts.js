// hooks/useKeyboardShortcut.js
// Custom hook for handling keyboard shortcuts consistently
// Eliminates duplicate keyboard event listeners across pages

import { useEffect } from "react";

/**
 * Custom Hook: useKeyboardShortcut
 *
 * Manages keyboard event listeners with automatic cleanup
 * Prevents duplicate listeners and memory leaks
 *
 * Supported shortcuts:
 * - 'Escape': Close modals, cancel operations
 * - 'Enter': Submit forms, confirm actions
 * - 'Delete': Delete operations (if focused)
 * - 'Ctrl+S' or 'Cmd+S': Save operations
 * - Any other valid KeyboardEvent.key value
 *
 * @param {string} key - The key to listen for (e.g., 'Escape', 'Enter')
 * @param {function} callback - Function to call when key is pressed
 * @param {array} dependencies - Dependencies array (when to re-attach listener)
 * @param {object} options - Additional options
 * @param {boolean} options.ctrlKey - Require Ctrl key (for Ctrl+X combos)
 * @param {boolean} options.shiftKey - Require Shift key
 * @param {boolean} options.altKey - Require Alt key
 * @param {boolean} options.metaKey - Require Meta key (Cmd on Mac)
 * @param {string} options.targetSelector - Only trigger on elements matching selector
 *
 * @example
 * // Close modal with Escape key
 * useKeyboardShortcut('Escape', () => setShowModal(false), [showModal]);
 *
 * // Submit form with Enter key
 * useKeyboardShortcut('Enter', () => handleSubmit(), []);
 *
 * // Save with Ctrl+S
 * useKeyboardShortcut('s', () => handleSave(), [], { ctrlKey: true });
 *
 * // Delete when focused on specific element
 * useKeyboardShortcuts('Delete', () => handleDelete(), [], {
 *   targetSelector: '.deletable-item'
 * });
 */
const useKeyboardShortcuts = (
  key,
  callback,
  dependencies = [],
  options = {}
) => {
  const {
    ctrlKey = false,
    shiftKey = false,
    altKey = false,
    metaKey = false,
    targetSelector = null,
  } = options;

  useEffect(() => {
    if (!key || !callback) return;

    const handleKeyDown = (e) => {
      // Check if key matches
      const keyMatches =
        e.key.toLowerCase() === key.toLowerCase() ||
        e.code.toLowerCase() === key.toLowerCase();

      if (!keyMatches) return;

      // Check modifier keys
      if (ctrlKey && !e.ctrlKey) return;
      if (shiftKey && !e.shiftKey) return;
      if (altKey && !e.altKey) return;
      if (metaKey && !e.metaKey) return;

      // Check target selector if provided
      if (targetSelector) {
        const target = e.target.closest(targetSelector);
        if (!target) return;
      }

      // Prevent default behavior and execute callback
      e.preventDefault();
      callback(e);
    };

    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [
    key,
    callback,
    ctrlKey,
    shiftKey,
    altKey,
    metaKey,
    targetSelector,
    ...dependencies,
  ]);
};

export default useKeyboardShortcuts;

/*
import { useEffect } from 'react';
export function useKeyboardShortcuts(shortcuts, isActive = true) {
useEffect(() => {
if (!isActive) return;
const handleKeyDown = (event) => {
// Build key combination string
const modifiers = [];
if (event.ctrlKey || event.metaKey) modifiers.push('Control');
if (event.altKey) modifiers.push('Alt');
if (event.shiftKey) modifiers.push('Shift');
const key = event.key;
const combination = modifiers.length > 0
? ${modifiers.join('+')}+${key}
: key;
// Also check lowercase version
const combinationLower = modifiers.length > 0
? ${modifiers.join('+')}+${key.toLowerCase()}
: key.toLowerCase();
// Execute handler if shortcut matches
const handler = shortcuts[combination] || shortcuts[combinationLower];
if (handler) {
handler(event);
}
};
document.addEventListener('keydown', handleKeyDown);
return () => {
document.removeEventListener('keydown', handleKeyDown);
};
}, [shortcuts, isActive]);
}
*/