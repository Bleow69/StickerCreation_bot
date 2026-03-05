import io
from PIL import Image


class ImageProcessor:
    MAX_STICKER_SIZE = 512
    MAX_INPUT_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_STICKER_FILE_SIZE = 512 * 1024      # 512KB

    def validate_input_size(self, file_size: int):
        if file_size and file_size > self.MAX_INPUT_FILE_SIZE:
            raise ValueError("Image file too large (over 10MB).")

    def process_image(self, image_bytes: bytes) -> io.BytesIO:
        """
        Converts any supported image into a Telegram-compatible
        512x512 PNG sticker.
        """

        try:
            image = Image.open(io.BytesIO(image_bytes))
        except Exception:
            raise ValueError("Invalid or unsupported image file.")

        # Convert to RGBA (handles JPG, PNG, WEBP)
        image = image.convert("RGBA")

        # Maintain aspect ratio
        image.thumbnail(
            (self.MAX_STICKER_SIZE, self.MAX_STICKER_SIZE),
            Image.LANCZOS
        )

        # Create transparent canvas
        canvas = Image.new(
            "RGBA",
            (self.MAX_STICKER_SIZE, self.MAX_STICKER_SIZE),
            (0, 0, 0, 0)
        )

        # Center image
        x = (self.MAX_STICKER_SIZE - image.width) // 2
        y = (self.MAX_STICKER_SIZE - image.height) // 2
        canvas.paste(image, (x, y), image)

        # Save to PNG
        output = io.BytesIO()
        canvas.save(output, format="PNG", optimize=True)
        output.seek(0)

        # Validate Telegram limit
        if output.getbuffer().nbytes > self.MAX_STICKER_FILE_SIZE:
            raise ValueError("Final sticker exceeds 512KB Telegram limit.")

        return output
