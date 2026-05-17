import { useState, useEffect } from 'react'
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
  const [showOptions, setShowOptions] = useState(false) 
  const [customText, setCustomText] = useState('')
  const [expireTime, setExpireTime] = useState('')

  const [qrBlobUrl, setQrBlobUrl] = useState<string | null>(null)
  const [isQrLoading, setIsQrLoading] = useState(false)
  const [fillColor, setFillColor] = useState('#D16B4B')
  const [backColor, setBackColor] = useState('#FFFFFF')
  const [gradientType, setGradientType] = useState<string>('none')
  const [gradientColor, setGradientColor] = useState('#1A1A1A')
  const [dotsStyle, setDotsStyle] = useState('square')
  const [eyeStyle, setEyeStyle] = useState('square')

  const API_URL = 'http://127.0.0.1:8000'
  const fullShortLink = shortenedCode ? `${API_URL}/${shortenedCode}` : ''

  useEffect(() => {
    if (isModalOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [isModalOpen])

  const handleShorten = async () => {
    if (!url) {
      alert('Пожалуйста, введите ссылку!')
      return
    }

    setIsLoading(true)
    try {
      const token = localStorage.getItem('token')
      const bodyData = {
        url: url,
        text: customText.trim() || null,
        time: expireTime ? Number(expireTime) : null,
      }

      const response = await fetch(`${API_URL}/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(bodyData),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Ошибка при сокращении ссылки')
      }

      const data = await response.json()
      setShortenedCode(data.shortened)
      setIsModalOpen(true)
    } catch (err: any) {
      alert(err.message || 'Произошла непредвиденная ошибка')
    } finally {
      setIsLoading(false)
    }
  }

  const generateQrCode = async () => {
    if (!fullShortLink) return
    setIsQrLoading(true)

    try {
      const qrPayload = {
        url: fullShortLink,
        fill_color: fillColor,
        back_color: backColor,
        gradient_type: gradientType === 'none' ? null : gradientType,
        gradient_color: gradientType === 'none' ? null : gradientColor,
        dots_style: dotsStyle,
        eye_style: eyeStyle,
        border_style: 'square'
      }

      const response = await fetch(`${API_URL}/qr/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(qrPayload)
      })

      if (!response.ok) throw new Error('Не удалось сгенерировать QR-код')

      const blob = await response.blob()
      if (qrBlobUrl) URL.revokeObjectURL(qrBlobUrl)
      setQrBlobUrl(URL.createObjectURL(blob))
    } catch (error) {
      console.error(error)
    } finally {
      setIsQrLoading(false)
    }
  }

  useEffect(() => {
    if (isModalOpen && fullShortLink) {
      const delayDebounce = setTimeout(() => {
        generateQrCode()
      }, 400)
      return () => clearTimeout(delayDebounce)
    }
  }, [fillColor, backColor, gradientType, gradientColor, dotsStyle, eyeStyle, isModalOpen])

  return (
    <div className={s.container}>
      <div className={s.wrapper}>
        <img src={iconLink} alt="Link icon" className={s.icon} />
        <input
          type="text"
          placeholder={placeholder}
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className={s.input}
        />
        <Button variant="primary" onClick={handleShorten} disabled={isLoading}>
          {isLoading ? 'Shortening...' : 'Shorten URL'}
        </Button>
      </div>

      <button
        onClick={() => setShowOptions(!showOptions)}
        className={s.optionsToggle}
      >
        {showOptions ? '▾ Hide advanced options' : '▸ Show advanced options'}
      </button>

      {showOptions && (
        <div className={s.optionsPanel}>
          <div className={s.optionField}>
            <label className={s.label}>Custom Alias (Optional)</label>
            <input
              type="text"
              placeholder="e.g. my-custom-link"
              value={customText}
              onChange={(e) => setCustomText(e.target.value)}
              className={s.subInput}
            />
          </div>
          <div className={s.optionField}>
            <label className={s.label}>Link Expiration</label>
            <select
              value={expireTime}
              onChange={(e) => setExpireTime(e.target.value)}
              className={s.select}
            >
              <option value="">Never (Permanent)</option>
              <option value="1">1 Hour</option>
              <option value="24">1 Day</option>
              <option value="168">7 Days</option>
              <option value="720">30 Days</option>
            </select>
          </div>
        </div>
      )}
      
      {isModalOpen && (
        <div className={s.modalOverlay}>
          <div className={s.modalContentLarge}>
            <h2>Ссылка успешно создана!</h2>
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

            <div className={s.qrWorkspace}>
              <div className={s.qrPreviewSection}>
                <div className={s.qrFrame}>
                  {isQrLoading && <div className={s.qrSpinner}>Загрузка...</div>}
                  {qrBlobUrl ? (
                    <img src={qrBlobUrl} alt="Generated QR Code" className={s.qrImage} />
                  ) : (
                    <div className={s.qrPlaceholder}>Генерация превью...</div>
                  )}
                </div>
                {qrBlobUrl && (
                  <a href={qrBlobUrl} download={`qr-${shortenedCode}.png`} className={s.downloadBtn}>
                    Скачать PNG
                  </a>
                )}
              </div>

              <div className={s.qrControlsSection}>
                <h3>Настройка дизайна QR</h3>
                
                <div className={s.controlGroupRow}>
                  <div className={s.controlItem}>
                    <label>Цвет паттерна</label>
                    <input type="color" value={fillColor} onChange={(e) => setFillColor(e.target.value)} />
                  </div>
                  <div className={s.controlItem}>
                    <label>Цвет фона</label>
                    <input type="color" value={backColor} onChange={(e) => setBackColor(e.target.value)} />
                  </div>
                </div>

                <div className={s.controlItem}>
                  <label>Тип градиента</label>
                  <select value={gradientType} onChange={(e) => setGradientType(e.target.value)}>
                    <option value="none">Без градиента (Сплошной)</option>
                    <option value="horizontal">Горизонтальный</option>
                    <option value="radial">Радиальный</option>
                  </select>
                </div>

                {gradientType !== 'none' && (
                  <div className={s.controlItem}>
                    <label>Второй цвет градиента</label>
                    <input type="color" value={gradientColor} onChange={(e) => setGradientColor(e.target.value)} />
                  </div>
                )}

                <div className={s.controlItem}>
                  <label>Форма точек (Паттерн)</label>
                  <select value={dotsStyle} onChange={(e) => setDotsStyle(e.target.value)}>
                    <option value="square">Квадрат (Стандарт)</option>
                    <option value="rounded">Сглаженный квадрат</option>
                    <option value="gapped">Раздельные точки</option>
                    <option value="circle">Круги</option>
                  </select>
                </div>

                <div className={s.controlItem}>
                  <label>Стиль угловых маркеров (Eyes)</label>
                  <select value={eyeStyle} onChange={(e) => setEyeStyle(e.target.value)}>
                    <option value="square">Квадратные</option>
                    <option value="rounded">Округлые</option>
                  </select>
                </div>
              </div>
            </div>

            <button onClick={() => setIsModalOpen(false)} className={s.closeBtn}>
              Закрыть редактор
            </button>
          </div>
        </div>
      )}
    </div>
  )
}