export default function Button({
  children,
  type = 'button',
  variant = 'primary',
  disabled = false,
  className = '',
  style = {},
  ...props
}) {
  const base =
    variant === 'primary'
      ? 'inline-flex items-center justify-center py-2 px-3 bg-mint-active text-onMint border-0 rounded-md text-base font-semibold transition-[filter] duration-150 ease-in-out hover:brightness-105 disabled:opacity-60 disabled:cursor-not-allowed'
      : 'inline-flex items-center justify-center py-2 px-3 bg-transparent text-contentSecondary border border-borderInput rounded-md text-base font-medium hover:bg-borderLight'
  return (
    <button
      type={type}
      className={`${base} ${className}`.trim()}
      disabled={disabled}
      style={style}
      {...props}
    >
      {children}
    </button>
  )
}
