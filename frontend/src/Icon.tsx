import iconPath from "./assets/heart.png"

interface IconProps {
    path?: string
    width?: number
    height?: number
}

const IconImage = (props: IconProps) => {
    const {
       path = iconPath,
       width = 20,
       height = 20 
    } = props
    return (
        <img 
        src={path} 
        alt="Иконка" 
        style={{width: `${width}px`, height: `${height}px`}}
    />
    )
}

export default IconImage