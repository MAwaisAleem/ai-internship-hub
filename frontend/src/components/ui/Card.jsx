export default function Card({ children, className = '', style = {} }) {
  return (
    <div
      className={`bg-card rounded-card shadow-card border border-borderLight p-4 ${className}`.trim()}
      style={style}
    >
      {children}
    </div>
  )
}
