from typing import Literal

T_PdfTools = Literal[
    "compress",
    "extract",
    "htmlpdf",
    "imagepdf",
    "merge",
    "officepdf",
    "pagenumber",
    "pdfa",
    "pdfjpg",
    "pdfocr",
    "protect",
    "repair",
    "rotate",
    "split",
    "unlock",
    "validatepdfa",
    "watermark",
]
T_ImageTools = Literal[
    "compressimage",
    "cropimage",
    "convertimage",
    "removebackgroundimage",
    "repairimage",
    "resizeimage",
    "rotateimage",
    "upscaleimage",
    "watermarkimage",
]
