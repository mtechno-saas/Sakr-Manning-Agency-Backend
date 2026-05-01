import "./formStyles.css";

const inputStyles =
  "w-full h-14 bg-white border border-gray-400 shadow-sm rounded-2xl px-5 text-base font-poppins";

export function FormInput({
  name,
  placeholder,
  type = "text",
  value,
  onChange,
  className = "",
  ...props
}) {
  return (
    <input
      type={type}
      name={name}
      placeholder={placeholder}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className={`${inputStyles} ${className}`}
      {...props}
    />
  );
}

export function FormSelect({
  name,
  placeholder,
  options = [],
  value,
  onChange,
  className = "",
}) {
  return (
    <div className={`relative ${className}`}>
      <select
        name={name}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={`${inputStyles} appearance-none cursor-pointer`}
      >
        <option value="" disabled>
          {placeholder}
        </option>
        {options.map((option, i) => (
          <option key={i} value={option}>
            {option}
          </option>
        ))}
      </select>
      <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-gray-500">
        ▼
      </div>
    </div>
  );
}

export function FileUploadArea({ name, onChange }) {
  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) onChange(file);
  };

  return (
    <div className="flex justify-center mb-[4%]">
      <label
        htmlFor={name}
        className="cursor-pointer w-2/3 h-[20vh] bg-gray-100 border-2 border-dashed border-gray-300 rounded-2xl flex flex-col items-center justify-center gap-3"
      >
        <div className="text-green-500 text-2xl">📁</div>
        <p className="text-gray-600 text-sm font-poppins text-center">
          <span className="text-[#0065AF] underline">Click</span> to upload or
          drag & drop your profile photo (JPG/PNG)
        </p>
        <input
          type="file"
          id={name}
          name={name}
          accept="image/*"
          onChange={handleFileSelect}
          className="hidden"
        />
      </label>
    </div>
  );
}
