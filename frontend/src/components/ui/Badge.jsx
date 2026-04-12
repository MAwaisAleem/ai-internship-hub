export default function Badge({ children, active = false, className = '', style = {} }) {
  return (
    <span
      className={`inline-block py-1 px-2 rounded-sm text-xs font-medium ${
        active ? 'bg-mint-active text-onMint' : 'bg-mint text-content'
      } ${className}`.trim()}
      style={style}
    >
      {children}
    </span>
  )
}
