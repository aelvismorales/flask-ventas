import imghdr

def validar_imagen(image_stream):
    """
    Validate if the given stream is a valid image file.
    Return the file extension if valid, otherwise None.
    """
    MAX_CONTENT_LENGTH = 1024 * 1024  # 1 MB

    if image_stream is None or not hasattr(image_stream, 'read'):
        raise ValueError("The 'image_stream' argument must be a readable byte stream.")

    # Check the size of the stream
    image_stream.seek(0, 2)  # Seek to the end of the stream
    size = image_stream.tell()  # Get the current position, which is the size of the stream
    if size > MAX_CONTENT_LENGTH:
        raise ValueError(f"The 'image_stream' is too large. Maximum size is {MAX_CONTENT_LENGTH} bytes.")
    image_stream.seek(0)  # Seek back to the start of the stream

    header = image_stream.read(512)
    image_stream.seek(0)
    image_format = imghdr.what(None, header)

    if not image_format:
        return None

    return '.' + (image_format if image_format != 'jpeg' else 'jpg')