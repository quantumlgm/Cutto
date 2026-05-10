interface TitleProps {
    text: string
    color: string
}

const Title = ({ text, color }: TitleProps) => {
    return (
        <div>
            <h1 style={{color: color}}>{text}</h1>
        </div>
    )
}

export default Title