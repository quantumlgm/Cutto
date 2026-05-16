import Input from './Input'
import s from './Hero.module.css'

const trustItems = ['Secure', 'Reliable', 'Fast', 'Built for scale']

export default function Hero() {
  return (
    <section className={s.hero}>
      <div className={s.dotGridLeft} aria-hidden />
      <div className={s.dotGridRight} aria-hidden />

      <div className={s.content}>
        <p className={s.badge}>✦ FAST LINK SHORTENER</p>
        <h1 className={s.title}>Short links. Big impact.</h1>
        <p className={s.description}>
          Cutto helps you turn long, messy URLs into short, branded links that look better,
          perform better, and convert more.
        </p>

        <Input />

        <ul className={s.trustList}>
          {trustItems.map((item) => (
            <li key={item} className={s.trustItem}>
              <svg className={s.checkIcon} width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden>
                <path d="M3 8.5L6.5 12L13 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              {item}
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
