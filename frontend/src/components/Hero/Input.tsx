import { useState } from 'react'
import iconLink from '../../assets/icon-link.svg'
import Button from '../Button/Button'
import s from './Input.module.css'

interface Props {
    placeholder?: string
}

export default function Input({ placeholder = 'Paste your long URL' }: Props) {  
  const [url, setUrl] = useState('')
    
  const [shortenedCode, setShortenedCode] = useState('')
  
  const [isModalOpen, setIsModalOpen] = useState(false)
    
  const [isLoading, setIsLoading] = useState(false)

  const handleShorten = async () => {
    if (!url) {
      alert('Пожалуйста, введите ссылку!')
      return
    }

    setIsLoading(true)

    try {     
      const token = localStorage.getItem('token') 
      
      const response = await fetch('http://127.0.0.1:8000/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',         
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify({
          url: url,
          text: null,
          time: null
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Ошибка при создании ссылки')
      }
      
      const data = await response.json() 
          
      setShortenedCode(data.shortened) 
      setIsModalOpen(true)
      
    } catch (error: any) {
      console.error(error)
      alert(`Ошибка: ${error.message}`)
    } finally {
      setIsLoading(false)
    }
  }
  
  const fullShortLink = `http://127.0.0.1:8000/${shortenedCode}`

  return (
    <>
      <div className={s.wrapper}>
        <img src={iconLink} alt="" className={s.icon} aria-hidden />
        <input
          type="url"
          placeholder={placeholder}
          className={s.input}
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <div>        
          <Button variant="primary" onClick={handleShorten} disabled={isLoading} >
            {isLoading ? 'Creating...' : 'Shorten link →'}
          </Button>
        </div>
      </div>
     
      {isModalOpen && (
        <div className={s.modalOverlay}>
          <div className={s.modalContent}>
            <h2>Ссылка успешно создана! 🎉</h2>
            <p className={s.description}>Ваша короткая ссылка:</p>
            
            <div className={s.linkBox}>
              <input type="text" readOnly value={fullShortLink} className={s.modalInput} />
              <button 
                onClick={() => {
                  navigator.clipboard.writeText(fullShortLink)
                  alert('Ссылка скопирована в буфер обмена!')
                }}
                className={s.copyBtn}
              >
                Копировать
              </button>
            </div>

            <button onClick={() => setIsModalOpen(false)} className={s.closeBtn}>
              Закрыть
            </button>
          </div>
        </div>
      )}
    </>
  )
}