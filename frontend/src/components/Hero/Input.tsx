import iconLink from '../../assets/icon-link.svg'
import Button from '../Button/Button'
import s from './Input.module.css'

interface Props {
    placeholder?: string
}

export default function Input({ placeholder = 'Paste your long URL' }: Props) {
  return (
    <div className={s.wrapper}>
      <img src={iconLink} alt="" className={s.icon} aria-hidden />
      <input
        type="url"
        placeholder={placeholder}
        className={s.input}
      />
      <div>
        <Button variant="primary" >
          Shorten link &rarr;
        </Button>
      </div>
    </div>
  )
}
