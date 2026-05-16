export const validators = {
    /**
    
    Required field validator
    */
    required: (value, message = 'This field is required') => {
        if (value === null || value === undefined) {
            return message;
        }
        if (typeof value === 'string' && !value.trim()) {
            return message;
        }
        if (Array.isArray(value) && value.length === 0) {
            return message;
        }
        return null;
    },

    /**
    
    Email validator
    */
    email: (value) => {
        if (!value) return null; // Optional field
        const emailRegex = /^[^\s@]+@[^\s@]+.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            return 'Invalid email format';
        }
        return null;
    },

    /**
    
    Phone number validator (international format)
    */
    phone: (value) => {
        if (!value) return null; // Optional field
        // Accepts: +1234567890, (123) 456-7890, 123-456-7890, etc.
        const phoneRegex = /^[+]?[(]?[0-9]{1,4}[)]?[-\s.]?[(]?[0-9]{1,4}[)]?[-\s.]?[0-9]{1,9}$/;
        if (!phoneRegex.test(value.replace(/\s/g, ''))) {
            return 'Invalid phone number';
        }
        return null;
    },

    /**
    
    IMO number validator (7 digits)
    */
    imo: (value) => {
        if (!value) return null; // Optional field
        if (!/^\d{7}$/.test(value)) {
            return 'IMO number must be exactly 7 digits';
        }
        return null;
    },

    /**
    
    URL validator
    */
    url: (value) => {
        if (!value) return null; // Optional field
        try {
            new URL(value);
            return null;
        } catch {
            return 'Invalid URL format';
        }
    },

    /**
    
    Minimum length validator
    */
    minLength: (min) => (value) => {
        if (!value) return null; // Optional field
        if (value.length < min) {
            return Minimum`${min} characters required`;
        }
        return null;
    },

    /**
    
    Maximum length validator
    */
    maxLength: (max) => (value) => {
        if (!value) return null; // Optional field
        if (value.length > max) {
            return Maximum`${max} characters allowed`;
        }
        return null;
    },

    /**
    
    Minimum value validator (for numbers)
    */
    min: (min) => (value) => {
        if (value === '' || value === null || value === undefined) return null;
        const numValue = parseFloat(value);
        if (isNaN(numValue) || numValue < min) {
            return `Minimum value is ${min}`;
        }
        return null;
    },

    /**
    
    Maximum value validator (for numbers)
    */
    max: (max) => (value) => {
        if (value === '' || value === null || value === undefined) return null;
        const numValue = parseFloat(value);
        if (isNaN(numValue) || numValue > max) {
            return `Maximum value is ${max}`;
        }
        return null;
    },

    /**
    
    Date after validator
    */
    dateAfter: (startDate, message = 'End date must be after start date') => (endDate) => {
        if (!startDate || !endDate) return null;
        const start = new Date(startDate);
        const end = new Date(endDate);
        if (end <= start) {
            return message;
        }
        return null;
    },

    /**
    
    Date before validator
    */
    dateBefore: (endDate, message = 'Start date must be before end date') => (startDate) => {
        if (!startDate || !endDate) return null;
        const start = new Date(startDate);
        const end = new Date(endDate);
        if (start >= end) {
            return message;
        }
        return null;
    },

    /**
    
    Pattern validator (regex)
    */
    pattern: (regex, message = 'Invalid format') => (value) => {
        if (!value) return null; // Optional field
        if (!regex.test(value)) {
            return message;
        }
        return null;
    },

    /**
    
    Numeric validator
    */
    numeric: (value) => {
        if (!value) return null; // Optional field
        if (isNaN(value)) {
            return 'Must be a number';
        }
        return null;
    },

    /**
    
    Integer validator
    */
    integer: (value) => {
        if (!value) return null; // Optional field
        if (!Number.isInteger(Number(value))) {
            return 'Must be an integer';
        }
        return null;
    },

    /**
    
    Custom validator
    */
    custom: (validatorFn, message) => (value) => {
        const isValid = validatorFn(value);
        return isValid ? null : message;
    },
};

/**

Validate entire form against rules

@param {Object} formData - Form data object
@param {Object} rules - Validation rules object
@returns {Object} Errors object

@example
const rules = {
email: [validators.required, validators.email],
age: [validators.required, validators.min(18)],
};

const errors = validateForm(formData, rules);
*/
export function validateForm(formData, rules) {
    const errors = {};

    Object.keys(rules).forEach((field) => {
        const fieldRules = Array.isArray(rules[field]) ? rules[field] : [rules[field]];
        const value = formData[field];
        for (const rule of fieldRules) {
            const error = rule(value);
            if (error) {
                errors[field] = error;
                break; // Stop at first error
            }
        }
    });
    return errors;
}
/**

Validate single field

@param {any} value - Field value
@param {Array|Function} rules - Validation rules
@returns {string|null} Error message or null
*/
export function validateField(value, rules) {
    const fieldRules = Array.isArray(rules) ? rules : [rules];

    for (const rule of fieldRules) {
        const error = rule(value);
        if (error) {
            return error;
        }
    }
    return null;
}
/**

Common validation rule presets
*/
export const validationPresets = {
    // Company validations
    company: {
        company_name: [validators.required, validators.minLength(2)],
        company_type: validators.required,
        contact_email: [validators.required, validators.email],
        hourly_rate: [validators.required, validators.min(0)],
        open_positions: validators.min(0),
    },

    // User validations
    user: {
        email: [validators.required, validators.email],
        first_name: [validators.required, validators.minLength(2)],
        phone_number: validators.phone,
    },
    // Ship validations
    ship: {
        ship_name: [validators.required, validators.minLength(2)],
        imo_number: validators.imo,
        company: validators.required,
        ship_type: validators.required,
        flag: validators.required,
        gross_tonnage: validators.min(0),
    },
    // Document/Contract validations
    document: {
        user: validators.required,
        company: validators.required,
        rank: validators.required,
        sign_on_date: validators.required,
        sign_off_date: validators.required,
        salary: [validators.required, validators.min(0)],
    },
    // Interview validations
    interview: {
        candidate: validators.required,
        company: validators.required,
        scheduled_date: validators.required,
        scheduled_time: validators.required,
    },
    // Finance validations
    finance: {
        user: validators.required,
        company: validators.required,
        start_date: validators.required,
        end_date: validators.required,
        status: validators.required,
    },
};
export default {
    validators,
    validateForm,
    validateField,
    validationPresets,
};
