from io import BytesIO

from pypdf import PdfReader


async def extract_text_from_pdf(file_id, bot):
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_path}"

    file_content = await bot.download_file(file_path)
    reader = PdfReader(BytesIO(file_content.read()))
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text
