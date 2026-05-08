from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import qrcode
import io
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import (
    SolidFillColorMask,
    RadialGradiantColorMask,
    HorizontalGradiantColorMask,
)
from qrcode.image.styles.moduledrawers import (
    RoundedModuleDrawer,
    CircleModuleDrawer,
    GappedSquareModuleDrawer,
    SquareModuleDrawer,
)
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import ImageColor

from ..database import get_db
from ..schemas import CreateQr
from ..models import Links

router_qr = APIRouter()


@router_qr.post("/qr/create", tags=["Create"])
async def qreate_qr(data: CreateQr, db: AsyncSession = Depends(get_db)):
    url_str = str(data.url)
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4
    )

    check = await db.execute(select(Links).where(Links.shortened == url_str))
    check_res = check.scalar_one_or_none()
    if check_res:
        target_url = f"https://yourdomain.com/{check_res.shortened}"
    else:
        target_url = url_str

    qr.add_data(target_url)

    match getattr(data, "eye_style", "square"):
        case "rounded":
            selected_drawer = RoundedModuleDrawer()
        case "circle":
            selected_drawer = CircleModuleDrawer()
        case "gapped":
            selected_drawer = GappedSquareModuleDrawer()
        case _:
            selected_drawer = SquareModuleDrawer()

    match getattr(data, "eye_style", "square"):
        case "circle":
            selected_eye_drawer = CircleModuleDrawer()
        case "rounded":
            selected_eye_drawer = RoundedModuleDrawer()
        case _:
            selected_eye_drawer = SquareModuleDrawer()

    try:
        rgb_fill = ImageColor.getcolor(data.fill_color, "RGB")
        rgb_back = ImageColor.getcolor(data.back_color, "RGB")

        raw_grad_color = data.gradient_color if data.gradient_color else "#000000"
        gradient_color = ImageColor.getcolor(raw_grad_color, "RGB")
    except ValueError as e:
        raise HTTPException(status_code=400, detail='Incorrect color format')

    match getattr(data, "gradient_type", None):
        case "radial":
            selected_mask = RadialGradiantColorMask(
                back_color=rgb_back, center_color=rgb_fill, edge_color=gradient_color
            )
        case "horizontal":
            selected_mask = HorizontalGradiantColorMask(
                back_color=rgb_back, left_color=rgb_fill, right_color=gradient_color
            )
        case _:
            selected_mask = SolidFillColorMask(
                front_color=rgb_fill, back_color=rgb_back
            )

    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=selected_drawer,
        eye_drawer=selected_eye_drawer,
        color_mask=selected_mask,
    )

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png")
