import { Select } from "./Select";
import { useFormField, cx } from "../../../../hooks/useFormField";

const variants = {
  default:
    "w-full bg-white shadow-md rounded-[15px] border border-black/50 flex items-center gap-2",
  light:
    "bg-blue-50 border border-blue-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-100",
  half: "w-full md:w-1/2 bg-white shadow-md rounded-[15px] border border-black/50 p-4",
  full: "w-full bg-white shadow-md rounded-[15px] border border-black/50 p-4",
  outlined: "w-full bg-white border border-gray-300 rounded-[15px] p-4",
  shadowed: "w-full bg-white shadow-lg rounded-[15px] p-4",
  calendar:
    "font-inter text-sm bg-white border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100",
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
          variant="light"
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
  prefix, // 🔹 new
  suffix, // 🔹 new
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
          "flex items-center rounded-lg text-sm transition-all duration-200",
          variants[variant],
          err
            ? "border-red-400 focus-within:ring-red-100 focus-within:border-red-500"
            : "",
          className
        )}
      >
        {/* prefix slot */}
        {prefix && <div className="flex-shrink-0">{prefix}</div>}

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
          className="w-full px-3 py-2 outline-none bg-transparent"
          {...props}
        />

        {/* suffix slot */}
        {suffix && <div className="flex-shrink-0">{suffix}</div>}

        {icon && (
          <div
            className="ml-2 text-gray-400 pointer-events-none"
            aria-hidden="true"
          >
            {icon}
          </div>
        )}
      </div>

      {err && (
        <p
          id={`${name}-error`}
          className="mt-1 text-red-500 text-xs flex items-center gap-1"
        >
          <span className="w-1 h-1 bg-red-500 rounded-full" /> {err}
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
