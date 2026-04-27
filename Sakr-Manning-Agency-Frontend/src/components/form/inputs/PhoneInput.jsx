import { Select } from "../inputs/Select";
import { useFormField, cx } from "../../../hooks/useFormField";

const variants = {
  default:
    "w-full bg-white shadow-md rounded-xl border-2 border-gray-300 hover:border-gray-400 hover:shadow-lg focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 transition-all duration-200 flex items-center gap-2",
  light:
    "bg-blue-50 border-2 border-blue-200 rounded-xl hover:border-blue-300 focus-within:border-blue-400 focus-within:ring-2 focus-within:ring-blue-100 transition-all duration-200",
  half: "w-full md:w-1/2 bg-white shadow-md rounded-xl border-2 border-gray-300 hover:border-gray-400 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 transition-all duration-200",
  full: "w-full bg-white shadow-md rounded-xl border-2 border-gray-300 hover:border-gray-400 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 transition-all duration-200",
  outlined: "w-full bg-white border-2 border-gray-300 rounded-xl hover:border-gray-400 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 transition-all duration-200",
  shadowed: "w-full bg-white shadow-lg rounded-xl border-2 border-gray-200 hover:shadow-xl focus-within:border-blue-400 focus-within:ring-2 focus-within:ring-blue-100 transition-all duration-200",
  calendar:
    "font-inter text-sm bg-white border-2 border-gray-300 rounded-xl hover:border-gray-400 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 transition-all duration-200",
};

const COUNTRY_CODES = [
  { value: "US", label: "🇺🇸 +1 United States" },
  { value: "EG", label: "🇪🇬 +20 Egypt" },
  { value: "GB", label: "🇬🇧 +44 United Kingdom" },
  { value: "DE", label: "🇩🇪 +49 Germany" },
  { value: "FR", label: "🇫🇷 +33 France" },
  { value: "IT", label: "🇮🇹 +39 Italy" },
  { value: "ES", label: "🇪🇸 +34 Spain" },
  { value: "CA", label: "🇨🇦 +1 Canada" },
  { value: "AU", label: "🇦🇺 +61 Australia" },
  { value: "JP", label: "🇯🇵 +81 Japan" },
  { value: "CN", label: "🇨🇳 +86 China" },
  { value: "IN", label: "🇮🇳 +91 India" },
  { value: "BR", label: "🇧🇷 +55 Brazil" },
  { value: "RU", label: "🇷🇺 +7 Russia" },
  { value: "SA", label: "🇸🇦 +966 Saudi Arabia" },
  { value: "AE", label: "🇦🇪 +971 UAE" },
  { value: "TR", label: "🇹🇷 +90 Turkey" },
  { value: "GR", label: "🇬🇷 +30 Greece" },
  { value: "NL", label: "🇳🇱 +31 Netherlands" },
  { value: "SE", label: "🇸🇪 +46 Sweden" },
];

export function PhoneInput({
  name,
  placeholder,
  rules,
  selectName = "phoneCode",
  defaultCountry = "EG",
  variant = "default",
}) {
  return (
    <BaseInput
      name={name}
      type="tel"
      placeholder={placeholder}
      variant={variant}
      rules={rules}
      prefix={
        <Select
          name={selectName}
          defaultValue={defaultCountry}
          variant="code"
          options={COUNTRY_CODES}
          rules={{ required: "Code is required" }}
        />
      }
    />
  );
}

export function BaseInput({
  name,
  label,
  type = "text",
  placeholder,
  rules,
  required = false,
  value,
  onChange,
  onBlur,
  error: externalError,
  icon,
  prefix,
  suffix,
  variant = "default",
  className = "",
  ...props
}) {
  const { inForm, register, error } = useFormField(name);
  const err = inForm ? error : externalError;

  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={name}
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}

      <div
        className={cx(
          "flex items-center rounded-xl transition-all duration-200 min-h-[48px]",
          variants[variant],
          className
        )}
      >
        {/* prefix slot */}
        {prefix && <div className="flex-shrink-0 pl-2">{prefix}</div>}

        <input
          id={name}
          name={name}
          type={type}
          required={required}
          aria-invalid={!!err}
          aria-describedby={err ? `${name}-error` : undefined}
          {...(inForm
            ? register(name, rules)
            : {
              value: value ?? "",
              onChange: (e) => onChange?.(e.target.value),
              onBlur,
            })}
          placeholder={placeholder}
          className="w-full px-4 py-3.5 text-base outline-none bg-transparent placeholder:text-gray-400"
          {...props}
        />

        {/* suffix slot */}
        {suffix && <div className="flex-shrink-0 pr-2">{suffix}</div>}

        {icon && (
          <div
            className="mr-4 text-gray-400 pointer-events-none"
            aria-hidden="true"
          >
            {icon}
          </div>
        )}
      </div>

      {err && (
        <p
          id={`${name}-error`}
          className="mt-2 text-sm text-red-600 flex items-center gap-1.5"
        >
          <span className="w-1.5 h-1.5 bg-red-600 rounded-full flex-shrink-0" />
          {err}
        </p>
      )}
    </div>
  );
}


import { DBBaseInput } from './BaseInput';
import { formatPhone, parsePhone } from '../../../utils/dashboard/formatters';

/**
@example
<PhoneInput
name="phone"
label="Phone Number"
value={formData.phone}
onChange={(val) => handleChange('phone', val)}
required
/>
*/

export function DBPhoneInput({
  value,
  onChange,
  variant = 'dashboard',
  ...props
}) {
  const handleChange = (val) => {
    // Parse to clean digits only
    const cleaned = parsePhone(val);
    onChange?.(cleaned);
  };

  // Display formatted version
  const displayValue = formatPhone(value || '');
  return (
    <DBBaseInput
      {...props}
      type="tel"
      value={displayValue}
      onChange={handleChange}
      placeholder="+1 (234) 567-8900"
      variant={variant}
      maxLength={20}
    />
  );
}

/////////////////////////////////////////////////////////////////////////////////////////

import { formatIMO } from '../../../utils/dashboard/formatters';
/**

@example
<IMOInput
name="imo_number"
label="IMO Number"
value={formData.imo_number}
onChange={(val) => handleChange('imo_number', val)}
/>
*/
export function IMOInput({
  value,
  onChange,
  variant = 'dashboard',
  ...props
}) {
  const handleChange = (val) => {
    // Only keep digits, max 7
    const cleaned = formatIMO(val);
    onChange?.(cleaned);
  };

  return (
    <DBBaseInput
      {...props}
      type="text"
      inputMode="numeric"
      value={value || ''}
      onChange={handleChange}
      placeholder="1234567"
      maxLength={7}
      variant={variant}
    />
  );
}