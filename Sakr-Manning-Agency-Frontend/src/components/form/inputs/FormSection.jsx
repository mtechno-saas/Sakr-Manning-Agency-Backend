/**
 * FormSection - Styled container for grouping form elements.
 *
 * Props:
 *  - title: optional section title
 *  - children: form elements inside
 *  - className: extra styling
 *  - variant: "default" | "primary" | "light" | "shadowed" | "gradient"
 *
 * Features:
 *  - Responsive Tailwind styling
 *  - Different visual backgrounds from UI design mapped to variants
 */

const variants = {
  plain: `
    h-auto bg-transparent px-8 pt-16 pb-2
  `,
  spacious: `
    h-auto bg-transparent flex flex-col gap-6 text-start px-6 py-14
  `,
  card: `
    h-auto bg-white 
    shadow-[0px_11px_13.2px_rgba(0,0,0,0.1)] 
    rounded-xl md:rounded-[15px] 
    md:p-10 px-6 py-14
  `,
  gradient: `
    h-auto flex flex-col gap-8
    bg-gradient-to-r from-[#DBE9F5] to-[#AFD1EE] 
    rounded-xl md:rounded-[15px] 
    pt-1 pb-10 px-6 !text-center
  `,
  compact: `
    h-auto flex flex-col gap-2 bg-transparent px-6 py-14
  `,
  default: `
    h-auto bg-white border border-gray-200 
    rounded-xl p-6 md:p-8 text-start mb-10 px-6 py-14 gap-8
  `,
};

export function FormSection({
  title,
  children,
  className = "",
  variant = "default",
}) {
  return (
    <div className={`rounded-2xl text-start ${variants[variant]} ${className}`}>
      {title && (
        <h2 className="text-4xl font-semibold font-poppins text-[#0065AF]">
          {title}
        </h2>
      )}
      {children}
    </div>
  );
}
