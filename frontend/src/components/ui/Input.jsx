export default function Input({ className = '', style = {}, ...props }) {
  return (
    <input
      className={`w-full py-2 px-3 border border-borderInput rounded-md text-base bg-card text-content focus:outline-none focus:border-mint-active focus:ring-2 focus:ring-focus ${className}`.trim()}
      style={style}
      {...props}
    />
  )
}
