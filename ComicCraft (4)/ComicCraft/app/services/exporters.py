from datetime import datetime
from pathlib import Path

from fpdf import FPDF
from PIL import Image


def _safe_text(value: str) -> str:
    return str(value).encode("latin-1", "replace").decode("latin-1")


def save_pdf(layout: list[dict], exports_dir: Path) -> str:
    exports_dir.mkdir(parents=True, exist_ok=True)

    filename = (
        f"comiccraft_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.pdf"
    )

    output = exports_dir / filename

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4",
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15,
    )

    page_width = 210
    content_width = 180

    for panel in layout:

        pdf.add_page()

        # -----------------------------------------------------
        # PANEL TITLE
        # -----------------------------------------------------
        pdf.set_font("Helvetica", "B", 18)

        title = (
            f"Panel {panel['panel_number']}: "
            f"{panel.get('title', '')}"
        )

        pdf.multi_cell(
            content_width,
            10,
            _safe_text(title),
            align="C",
        )

        pdf.ln(3)

        # -----------------------------------------------------
        # COMIC IMAGE
        # -----------------------------------------------------
        image_path = Path(panel["image_path"])

        with Image.open(image_path) as img:
            width, height = img.size

        max_w = content_width
        max_h = 115

        ratio = min(
            max_w / width,
            max_h / height,
        )

        draw_w = width * ratio
        draw_h = height * ratio

        x = (page_width - draw_w) / 2

        # IMPORTANT:
        # Put the image at the CURRENT PDF cursor position.
        image_y = pdf.get_y()

        pdf.image(
            str(image_path),
            x=x,
            y=image_y,
            w=draw_w,
            h=draw_h,
        )

        # IMPORTANT:
        # Move the PDF cursor BELOW the image.
        text_y = image_y + draw_h + 7
        pdf.set_y(text_y)

        # -----------------------------------------------------
        # SCENE DESCRIPTION
        # -----------------------------------------------------
        scene = panel.get("scene_description", "")

        if scene:
            pdf.set_font(
                "Helvetica",
                "I",
                10,
            )

            pdf.multi_cell(
                content_width,
                5,
                _safe_text(scene),
                align="L",
            )

            pdf.ln(3)

        # -----------------------------------------------------
        # CAPTION
        # -----------------------------------------------------
        caption = panel.get("caption", "")

        if caption:
            pdf.set_font(
                "Helvetica",
                "B",
                11,
            )

            pdf.multi_cell(
                content_width,
                6,
                _safe_text("Caption"),
            )

            pdf.set_font(
                "Helvetica",
                "",
                11,
            )

            pdf.multi_cell(
                content_width,
                6,
                _safe_text(caption),
            )

            pdf.ln(2)

        # -----------------------------------------------------
        # NARRATION
        # -----------------------------------------------------
        narration = panel.get("narration", "")

        if narration:
            pdf.set_font(
                "Helvetica",
                "B",
                11,
            )

            pdf.multi_cell(
                content_width,
                6,
                _safe_text("Narration"),
            )

            pdf.set_font(
                "Helvetica",
                "",
                11,
            )

            pdf.multi_cell(
                content_width,
                6,
                _safe_text(narration),
            )

            pdf.ln(2)

        # -----------------------------------------------------
        # DIALOGUE
        # -----------------------------------------------------
        dialogue = panel.get("dialogue", [])

        if dialogue:

            pdf.set_font(
                "Helvetica",
                "B",
                11,
            )

            pdf.multi_cell(
                content_width,
                6,
                _safe_text("Dialogue"),
            )

            pdf.set_font(
                "Helvetica",
                "",
                11,
            )

            for line in dialogue:

                if not line:
                    continue

                # Give every dialogue line its own row.
                pdf.multi_cell(
                    content_width,
                    6,
                    _safe_text(f"“{line}”"),
                    border=1,
                    align="L",
                )

                pdf.ln(1)

    # ---------------------------------------------------------
    # SAVE PDF
    # ---------------------------------------------------------
    pdf.output(str(output))

    return str(output)