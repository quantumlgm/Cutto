import icon from '../../assets/logo.png'
import Button from '../Button/Button.tsx'
import s from './Header.module.css'

const navItems = [
  { label: 'Product' },
  { label: 'Resources' },
  { label: 'Contacts' },
  { label: 'GitHub' },
]

export default function Header() {
  return (
    <header className={s.header}>
      <div className={s.container}>
        <a href="/">
          <img src={icon} alt="" className={s.logo} aria-hidden />          
        </a>

        <nav className={s.nav} aria-label="Main navigation">
          <ul className={s.navList}>
            {navItems.map((item) => (
              <li key={item.label}>
                <a href={`#${item.label.toLowerCase()}`} className={s.navLink}>
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>

        <div className={s.authButtons}>
          <Button variant="ghost">Log in</Button>
          <Button variant="primary">Sign up free</Button>
        </div>
      </div>
    </header>
  )
}
