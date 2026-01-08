from PIL import Image

img = Image.open("logo.png")

# Convertir a escala de grises
img = img.convert("L")

# Redimensionar a 384 px de ancho (58mm)
w_percent = 384 / float(img.size[0])
h_size = int(float(img.size[1]) * w_percent)
img = img.resize((384, h_size))

# Convertir a blanco y negro real (1-bit)
img = img.point(lambda x: 0 if x < 128 else 255, '1')

# Guardar imagen lista para ESC/POS
img.save("logo_escpos.png")

print("Logo convertido correctamente → logo_escpos.png")
