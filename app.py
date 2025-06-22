# app.py - Girasol completo con tallo, hojas y flores de fondo
from flask import Flask, render_template, jsonify, url_for
from PIL import Image, ImageDraw, ImageFilter
import os
import math
import time
import random

app = Flask(__name__)

# Carpeta donde se guardan los girasoles
girasoles_folder = os.path.join('static', 'girasoles')
os.makedirs(girasoles_folder, exist_ok=True)

contador_path = os.path.join(girasoles_folder, 'contador.txt')
if not os.path.exists(contador_path):
    with open(contador_path, 'w') as f:
        f.write('0')

def actualizar_contador():
    with open(contador_path, 'r+') as f:
        count = int(f.read().strip()) + 1
        f.seek(0)
        f.write(str(count))
        f.truncate()
    return count

def create_gradient_sky(size):
    """Crea un fondo con gradiente de cielo"""
    image = Image.new("RGB", (size, size), (15, 25, 35))
    draw = ImageDraw.Draw(image)
    
    # Gradiente de cielo de noche
    for y in range(size):
        # Color que va de azul oscuro arriba a azul más claro abajo
        factor = y / size
        r = int(15 + 25 * factor)
        g = int(25 + 35 * factor)
        b = int(35 + 45 * factor)
        color = (r, g, b)
        draw.line([(0, y), (size, y)], fill=color)
    
    # Añadir algunas estrellas
    for _ in range(30):
        x = random.randint(0, size)
        y = random.randint(0, size//2)  # Solo en la parte superior
        star_size = random.randint(1, 2)
        draw.ellipse((x-star_size, y-star_size, x+star_size, y+star_size), 
                    fill=(255, 255, 200))
    
    return image

def draw_background_flowers(draw, size, cx, cy):
    """Dibuja flores pequeñas de fondo"""
    flower_positions = [
        (cx - 250, cy - 100, 25),  # x, y, size
        (cx + 200, cy - 150, 30),
        (cx - 180, cy + 120, 20),
        (cx + 180, cy + 100, 28),
        (cx - 300, cy + 50, 22),
        (cx + 250, cy - 50, 26),
    ]
    
    for fx, fy, flower_size in flower_positions:
        if 0 < fx < size and 0 < fy < size:
            # Pétalos de la flor de fondo
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                petal_x = fx + flower_size * math.cos(rad)
                petal_y = fy + flower_size * math.sin(rad)
                
                # Pétalo pequeño
                draw.ellipse((petal_x-8, petal_y-4, petal_x+8, petal_y+4), 
                           fill=(100, 50, 150), outline=(80, 40, 120))
            
            # Centro de la flor de fondo
            draw.ellipse((fx-6, fy-6, fx+6, fy+6), fill=(255, 255, 100))

def draw_stem_and_leaves(draw, cx, cy, size):
    """Dibuja el tallo y las hojas del girasol"""
    # Tallo principal
    stem_width = 12
    stem_bottom = size - 80
    stem_color = (34, 139, 34)  # Verde bosque
    
    # Dibujar tallo con curvatura sutil
    stem_points = []
    for i in range(50):
        y = cy + 80 + (stem_bottom - cy - 80) * (i / 49)
        curve = 5 * math.sin(i * 0.2)  # Curvatura sutil
        x = cx + curve
        stem_points.append((x, y))
    
    # Dibujar el tallo como una serie de rectángulos
    for i in range(len(stem_points) - 1):
        x1, y1 = stem_points[i]
        x2, y2 = stem_points[i + 1]
        draw.line([(x1, y1), (x2, y2)], fill=stem_color, width=stem_width)
    
    # Sombra del tallo
    for i in range(len(stem_points) - 1):
        x1, y1 = stem_points[i]
        x2, y2 = stem_points[i + 1]
        draw.line([(x1+2, y1), (x2+2, y2)], fill=(20, 100, 20), width=stem_width//2)
    
    # Hojas grandes
    leaf_positions = [
        (cx - 30, cy + 150, -45, 40, 80),  # x, y, angle, width, height
        (cx + 35, cy + 200, 30, 45, 85),
        (cx - 40, cy + 280, -30, 50, 90),
        (cx + 25, cy + 350, 45, 42, 75),
    ]
    
    for lx, ly, angle, width, height in leaf_positions:
        if ly < size - 50:
            draw_leaf(draw, lx, ly, angle, width, height)

def draw_leaf(draw, x, y, angle, width, height):
    """Dibuja una hoja detallada"""
    rad = math.radians(angle)
    
    # Colores de la hoja
    leaf_green = (85, 170, 85)
    dark_green = (60, 120, 60)
    
    # Puntos de la hoja (forma elíptica)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    
    # Crear forma de hoja
    leaf_points = []
    for i in range(20):
        t = i / 19 * 2 * math.pi
        # Forma de hoja (elipse modificada)
        local_x = width/2 * math.cos(t) * (1.2 if abs(t - math.pi) < math.pi/2 else 0.8)
        local_y = height/2 * math.sin(t)
        
        # Rotación
        rotated_x = local_x * cos_a - local_y * sin_a
        rotated_y = local_x * sin_a + local_y * cos_a
        
        leaf_points.append((x + rotated_x, y + rotated_y))
    
    # Dibujar hoja
    draw.polygon(leaf_points, fill=leaf_green, outline=dark_green, width=2)
    
    # Venas de la hoja
    for i in range(-2, 3):
        vein_start_x = x - height/3 * cos_a
        vein_start_y = y - height/3 * sin_a
        vein_end_x = x + height/3 * cos_a
        vein_end_y = y + height/3 * sin_a
        
        # Vena lateral
        offset_x = i * width/8 * (-sin_a)
        offset_y = i * width/8 * cos_a
        
        draw.line([(vein_start_x + offset_x, vein_start_y + offset_y),
                  (vein_end_x + offset_x, vein_end_y + offset_y)], 
                 fill=dark_green, width=1)

def draw_geometric_petal_enhanced(draw, cx, cy, angle, length, width, fill_color, line_color):
    """Versión mejorada del pétalo geométrico con más detalles"""
    rad = math.radians(angle)
    
    # Calcular puntos del pétalo
    base_dist = 65
    tip_dist = length
    
    # Punto base y punta
    base_x = cx + base_dist * math.cos(rad)
    base_y = cy + base_dist * math.sin(rad)
    tip_x = cx + tip_dist * math.cos(rad)
    tip_y = cy + tip_dist * math.sin(rad)
    
    # Puntos laterales
    side_offset = width / 2
    left_angle = rad + math.pi/2
    right_angle = rad - math.pi/2
    
    # Crear forma del pétalo más detallada
    base_left_x = base_x + (width/4) * math.cos(left_angle)
    base_left_y = base_y + (width/4) * math.sin(left_angle)
    base_right_x = base_x + (width/4) * math.cos(right_angle)
    base_right_y = base_y + (width/4) * math.sin(right_angle)
    
    mid_left_x = cx + (tip_dist * 0.7) * math.cos(rad) + side_offset * math.cos(left_angle)
    mid_left_y = cy + (tip_dist * 0.7) * math.sin(rad) + side_offset * math.sin(left_angle)
    mid_right_x = cx + (tip_dist * 0.7) * math.cos(rad) + side_offset * math.cos(right_angle)
    mid_right_y = cy + (tip_dist * 0.7) * math.sin(rad) + side_offset * math.sin(right_angle)
    
    # Puntos adicionales para forma más suave
    quarter_left_x = cx + (tip_dist * 0.4) * math.cos(rad) + (side_offset*0.8) * math.cos(left_angle)
    quarter_left_y = cy + (tip_dist * 0.4) * math.sin(rad) + (side_offset*0.8) * math.sin(left_angle)
    quarter_right_x = cx + (tip_dist * 0.4) * math.cos(rad) + (side_offset*0.8) * math.cos(right_angle)
    quarter_right_y = cy + (tip_dist * 0.4) * math.sin(rad) + (side_offset*0.8) * math.sin(right_angle)
    
    # Dibujar pétalo con gradiente simulado (múltiples polígonos)
    petal_points = [
        (base_left_x, base_left_y),
        (quarter_left_x, quarter_left_y),
        (mid_left_x, mid_left_y),
        (tip_x, tip_y),
        (mid_right_x, mid_right_y),
        (quarter_right_x, quarter_right_y),
        (base_right_x, base_right_y)
    ]
    
    # Base del pétalo más clara
    base_color = tuple(min(255, c + 20) for c in fill_color)
    draw.polygon(petal_points, fill=base_color)
    
    # Centro del pétalo
    inner_points = [
        (quarter_left_x, quarter_left_y),
        (mid_left_x, mid_left_y),
        (tip_x, tip_y),
        (mid_right_x, mid_right_y),
        (quarter_right_x, quarter_right_y)
    ]
    draw.polygon(inner_points, fill=fill_color)
    
    # Líneas internas con patrón más complejo
    num_lines = 15
    for i in range(1, num_lines):
        t = i / num_lines
        
        # Líneas principales
        center_x = cx + (base_dist + (tip_dist - base_dist) * t) * math.cos(rad)
        center_y = cy + (base_dist + (tip_dist - base_dist) * t) * math.sin(rad)
        line_width = width * (1 - t * 0.6)
        
        left_x = center_x + (line_width/2) * math.cos(left_angle)
        left_y = center_y + (line_width/2) * math.sin(left_angle)
        right_x = center_x + (line_width/2) * math.cos(right_angle)
        right_y = center_y + (line_width/2) * math.sin(right_angle)
        
        line_thickness = 2 if i % 3 == 0 else 1
        draw.line([(left_x, left_y), (right_x, right_y)], 
                 fill=line_color, width=line_thickness)
        
        # Líneas diagonales para efecto chevron
        if i % 4 == 0:
            # Líneas en zigzag
            mid_x = (left_x + right_x) / 2
            mid_y = (left_y + right_y) / 2
            
            offset = 8
            draw.line([(left_x, left_y), (mid_x, mid_y - offset)], 
                     fill=line_color, width=1)
            draw.line([(mid_x, mid_y - offset), (right_x, right_y)], 
                     fill=line_color, width=1)
    
    # Contorno del pétalo
    draw.polygon(petal_points, outline=line_color, width=3)
    
    # Línea central más gruesa
    draw.line([(base_x, base_y), (tip_x, tip_y)], fill=line_color, width=3)

def draw_enhanced_center(draw, cx, cy, radius):
    """Centro mejorado con más textura y detalle"""
    phi = math.radians(137.508)
    
    # Colores del centro más variados
    center_colors = [
        (139, 0, 0),      # Rojo oscuro
        (165, 42, 42),    # Rojo ladrillo  
        (178, 34, 34),    # Rojo fuego
        (220, 20, 60),    # Carmesí
        (255, 69, 0),     # Rojo-naranja
        (128, 0, 0),      # Granate
    ]
    
    # Fondo del centro con gradiente
    for r in range(radius, 0, -2):
        alpha = 1 - (r / radius)
        color_idx = int(alpha * (len(center_colors) - 1))
        color = center_colors[min(color_idx, len(center_colors) - 1)]
        draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=color)
    
    # Semillas con más variación
    for i in range(1000):
        r = 1.5 * math.sqrt(i)
        if r > radius - 5:
            break
            
        theta = i * phi
        x = cx + r * math.cos(theta)
        y = cy + r * math.sin(theta)
        
        # Tamaño variable
        base_size = 2.5 - (r / radius) * 1.5
        size_variation = random.uniform(0.8, 1.3)
        seed_size = max(0.5, base_size * size_variation)
        
        # Color con más variación
        base_color = random.choice(center_colors)
        color = tuple(max(0, min(255, c + random.randint(-25, 25))) for c in base_color)
        
        # Forma ligeramente irregular
        offset = random.uniform(-0.5, 0.5)
        draw.ellipse((x-seed_size+offset, y-seed_size+offset, 
                     x+seed_size+offset, y+seed_size+offset), fill=color)
        
        # Pequeños destellos ocasionales
        if random.random() < 0.05:
            highlight_color = tuple(min(255, c + 50) for c in color)
            highlight_size = seed_size * 0.3
            draw.ellipse((x-highlight_size, y-highlight_size, 
                         x+highlight_size, y+highlight_size), fill=highlight_color)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detalles')
def detalles():
    return render_template('detalles.html')

@app.route('/mensajes')
def mensajes():
    return render_template('mensajes.html')

@app.route('/sunflower')
def sunflower_page():
    return render_template('sunflower.html')

@app.route('/generate_sunflower')
def generate_sunflower():
    timestamp = int(time.time())
    filename = f"girasol_{timestamp}.png"
    filepath = os.path.join(girasoles_folder, filename)

    # Crear imagen con fondo de cielo
    size = 800
    image = create_gradient_sky(size)
    draw = ImageDraw.Draw(image)

    # Centro de la flor principal
    cx, cy = size // 2, size // 2 - 50  # Subir un poco la flor
    
    # Configurar semilla aleatoria
    random.seed(timestamp)
    
    # Dibujar flores de fondo primero
    draw_background_flowers(draw, size, cx, cy)
    
    # Dibujar tallo y hojas
    draw_stem_and_leaves(draw, cx, cy, size)
    
    # Colores del girasol principal
    petal_colors = [
        (255, 235, 59),   # Amarillo brillante
        (255, 215, 0),    # Dorado
        (255, 193, 7),    # Amarillo intenso
    ]
    line_color = (40, 40, 40)
    
    # PÉTALOS - Múltiples capas con más variación
    # Capa 1: Pétalos exteriores
    num_outer = 20
    for i in range(num_outer):
        angle = i * (360 / num_outer) + random.uniform(-3, 3)
        length = random.uniform(150, 170)
        width = random.uniform(30, 40)
        color = petal_colors[0]
        
        draw_geometric_petal_enhanced(draw, cx, cy, angle, length, width, color, line_color)
    
    # Capa 2: Pétalos medios
    num_mid = 16
    for i in range(num_mid):
        angle = i * (360 / num_mid) + (360 / num_mid / 2) + random.uniform(-2, 2)
        length = random.uniform(120, 140)
        width = random.uniform(25, 32)
        color = petal_colors[1]
        
        draw_geometric_petal_enhanced(draw, cx, cy, angle, length, width, color, line_color)
    
    # Capa 3: Pétalos interiores
    num_inner = 12
    for i in range(num_inner):
        angle = i * (360 / num_inner) + (360 / num_inner / 3) + random.uniform(-2, 2)
        length = random.uniform(95, 115)
        width = random.uniform(18, 25)
        color = petal_colors[2]
        
        draw_geometric_petal_enhanced(draw, cx, cy, angle, length, width, color, line_color)
    
    # CENTRO DEL GIRASOL
    center_radius = 60
    draw_enhanced_center(draw, cx, cy, center_radius)
    
    # Contorno del centro con sombra
    draw.ellipse((cx-center_radius-2, cy-center_radius-2, 
                 cx+center_radius+2, cy+center_radius+2), 
                outline=(20, 20, 20), width=2)
    draw.ellipse((cx-center_radius, cy-center_radius, 
                 cx+center_radius, cy+center_radius), 
                outline=line_color, width=3)
    
    # TEXTO MEJORADO
    text = "Te Quiero"
    text_size = 24
    text_y = size - 70
    
    # Simular fuente más grande
    bbox = draw.textbbox((0, 0), text)
    text_width = bbox[2] - bbox[0]
    text_x = cx - text_width // 2
    
    # Fondo decorativo para el texto
    bg_padding = 15
    bg_x1 = text_x - bg_padding
    bg_y1 = text_y - bg_padding
    bg_x2 = text_x + text_width + bg_padding
    bg_y2 = text_y + 25 + bg_padding
    
    # Fondo con gradiente simulado
    draw.rectangle([bg_x1, bg_y1, bg_x2, bg_y2], fill=(0, 0, 0, 200))
    draw.rectangle([bg_x1+2, bg_y1+2, bg_x2-2, bg_y2-2], fill=(40, 40, 40))
    draw.rectangle([bg_x1, bg_y1, bg_x2, bg_y2], outline=(255, 215, 0), width=2)
    
    # Texto con múltiples efectos
    # Sombra
    draw.text((text_x + 3, text_y + 3), text, fill=(0, 0, 0))
    # Resplandor
    draw.text((text_x + 1, text_y + 1), text, fill=(255, 255, 150))
    draw.text((text_x - 1, text_y - 1), text, fill=(255, 255, 150))
    # Texto principal
    draw.text((text_x, text_y), text, fill=(255, 235, 59))
    
    # Aplicar filtro final para suavizar
    image = image.filter(ImageFilter.SMOOTH)
    
    image.save(filepath)
    count = actualizar_contador()
    return jsonify({
        'image_url': url_for('static', filename=f'girasoles/{filename}'),
        'count': count
    })

@app.route('/generate_cake')
def generate_cake():
    import time
    import os
    import random
    from PIL import Image, ImageDraw, ImageFont
    from flask import jsonify, url_for
    
    timestamp = int(time.time())
    filename = f"cake_{timestamp}.png"
    
    # Crear carpeta si no existe
    mensajes_folder = os.path.join('static', 'mensajes')
    os.makedirs(mensajes_folder, exist_ok=True)
    
    png_path = os.path.join(mensajes_folder, filename)
    
    try:
        # Crear imagen base
        width, height = 900, 800
        img = Image.new('RGB', (width, height), '#d3dae8')
        draw = ImageDraw.Draw(img)
        
        # Paleta de colores
        colors = {
            "light_green": "#c5e8c8",
            "medium_green": "#a3d2a7",
            "light_yellow": "#f7e8aa",
            "cream": "#fffceb",
            "off_white": "#fffdf4",
            "brown": "#8b5a2b",
            "dark_brown": "#5e4425",
            "orange": "#ffa500",
            "golden_yellow": "#ffb732",
            "teal": "#66cccc",
            "flame_orange": "#ff6600",
            "sky_blue": "#87ceeb",
            "light_steel": "#b0c4de",
            "confetti_colors": ["#4CAF50", "#FFC107", "#2196F3", "#FF5722", "#9C27B0", "#3F51B5", "#00BCD4", "#009688"]
        }
        
        # Función para dibujar elipse
        def draw_ellipse_layer(x_center, y_center, width, height, fill_color, outline_color="#ffffff"):
            left = x_center - width
            top = y_center - height
            right = x_center + width
            bottom = y_center + height
            draw.ellipse([left, top, right, bottom], fill=fill_color, outline=outline_color, width=3)
        
        # Función para dibujar rectángulo con bordes redondeados (capa del pastel)
        def draw_cake_layer(x_center, y_center, width, height, fill_color, outline_color="#ffffff"):
            # Base elíptica
            draw_ellipse_layer(x_center, y_center, width, height//3, fill_color, outline_color)
            
            # Lados del pastel
            left = x_center - width
            right = x_center + width
            top = y_center - height
            bottom = y_center
            
            draw.rectangle([left, top, right, bottom], fill=fill_color, outline=outline_color, width=3)
            
            # Elipse superior
            draw_ellipse_layer(x_center, y_center - height, width, height//3, fill_color, outline_color)
        
        # Función para dibujar vela
        def draw_candle(x, y, candle_height=50):
            # Cuerpo de la vela
            candle_width = 8
            draw.rectangle([x-candle_width//2, y-candle_height, x+candle_width//2, y], 
                          fill=colors["teal"], outline="#ffffff", width=2)
            
            # Rayas en la vela
            for i in range(1, 6):
                stripe_y = y - (candle_height * i // 6)
                draw.line([x-candle_width//2, stripe_y, x+candle_width//2, stripe_y], 
                         fill="#ffffff", width=2)
            
            # Mecha
            draw.line([x, y-candle_height, x, y-candle_height-10], fill="#333333", width=3)
            
            # Llama
            flame_points = [
                (x, y-candle_height-25),
                (x-6, y-candle_height-15),
                (x-3, y-candle_height-10),
                (x+3, y-candle_height-10),
                (x+6, y-candle_height-15)
            ]
            draw.polygon(flame_points, fill=colors["flame_orange"], outline="#ff3300")
        
        # Función para agregar confeti
        def add_confetti(num_dots=50):
            for _ in range(num_dots):
                x = random.randint(50, width-50)
                y = random.randint(50, height-100)
                size = random.randint(3, 8)
                color = random.choice(colors["confetti_colors"])
                draw.ellipse([x-size, y-size, x+size, y+size], fill=color)
        
        # Dibujar el pastel por capas (de abajo hacia arriba)
        center_x = width // 2
        
        # Capa base (más grande)
        base_y = height - 150
        draw_cake_layer(center_x, base_y, 150, 80, colors["light_green"], "#ffffff")
        
        # Capa media
        middle_y = base_y - 70
        draw_cake_layer(center_x, middle_y, 120, 70, colors["light_yellow"], "#ffffff")
        
        # Capa superior
        top_y = middle_y - 60
        draw_cake_layer(center_x, top_y, 80, 50, colors["brown"], "#ffffff")
        
        # Cobertura superior
        draw_ellipse_layer(center_x, top_y - 50, 70, 20, colors["orange"], colors["dark_brown"])
        
        # Posiciones de las velas
        candle_positions = [
            (center_x, top_y - 50),
            (center_x - 40, top_y - 45),
            (center_x + 40, top_y - 45),
            (center_x - 20, top_y - 55),
            (center_x + 20, top_y - 55)
        ]
        
        # Dibujar velas
        for pos in candle_positions:
            draw_candle(pos[0], pos[1])
        
        # Agregar confeti de fondo
        add_confetti(30)
        
        # Decoraciones adicionales en el pastel
        # Puntos decorativos en las capas
        for _ in range(15):
            x = random.randint(center_x - 140, center_x + 140)
            y = random.randint(base_y - 40, base_y + 20)
            color = random.choice(colors["confetti_colors"])
            draw.ellipse([x-3, y-3, x+3, y+3], fill=color)
        
        for _ in range(12):
            x = random.randint(center_x - 110, center_x + 110)
            y = random.randint(middle_y - 35, middle_y + 15)
            color = random.choice(colors["confetti_colors"])
            draw.ellipse([x-2, y-2, x+2, y+2], fill=color)
        
        # Texto "Happy Birthday"
        try:
            # Intentar usar una fuente del sistema
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 40)
                except:
                    try:
                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
                    except:
                        font = ImageFont.load_default()
            
            text = "Happy Birthday"
            
            # Calcular posición centrada para el texto
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = (width - text_width) // 2
            text_y = 50
            
            # Sombra del texto
            draw.text((text_x + 2, text_y + 2), text, fill="#333333", font=font)
            # Texto principal
            draw.text((text_x, text_y), text, fill="#ff1493", font=font)
            
        except Exception as e:
            print(f"Error con fuente: {e}")
            # Fallback sin fuente especial
            draw.text((center_x - 100, 50), "Happy Birthday!", fill="#ff1493")
        
        # Más confeti decorativo
        add_confetti(20)
        
        # Guardar imagen
        img.save(png_path, 'PNG', quality=95)
        
        return jsonify({
            'success': True,
            'image_url': url_for('static', filename=f'mensajes/{filename}'),
            'message': '¡Pastel horneado exitosamente!, disfrutalo'
        })
        
    except Exception as e:
        print(f"Error generando pastel: {e}")
        return jsonify({
            'success': False,
            'error': f'Error al generar el pastel: {str(e)}'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
