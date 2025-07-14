# app.py - Girasol completo con tallo, hojas y flores de fondo - VERSION MEJORADA
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
    """Crea un fondo con gradiente de cielo - con variaciones aleatorias"""
    # Colores base variables
    sky_types = [
        [(15, 25, 35), (40, 60, 80)],  # Noche azul
        [(25, 15, 45), (60, 40, 90)],  # Noche púrpura
        [(35, 25, 15), (80, 60, 40)],  # Atardecer
        [(10, 30, 50), (30, 70, 100)], # Azul profundo
        [(20, 20, 40), (50, 50, 80)],  # Azul grisáceo
    ]
    
    sky_type = random.choice(sky_types)
    start_color, end_color = sky_type
    
    image = Image.new("RGB", (size, size), start_color)
    draw = ImageDraw.Draw(image)
    
    # Gradiente variable
    for y in range(size):
        factor = y / size
        r = int(start_color[0] + (end_color[0] - start_color[0]) * factor)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * factor)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * factor)
        color = (r, g, b)
        draw.line([(0, y), (size, y)], fill=color)
    
    # Estrellas con variación aleatoria
    num_stars = random.randint(15, 45)
    for _ in range(num_stars):
        x = random.randint(0, size)
        y = random.randint(0, size//2)
        star_size = random.randint(1, 3)
        
        # Diferentes tipos de estrellas
        star_type = random.choice(['circle', 'cross', 'diamond'])
        star_colors = [(255, 255, 200), (255, 255, 255), (255, 255, 150), (200, 255, 255)]
        star_color = random.choice(star_colors)
        
        if star_type == 'circle':
            draw.ellipse((x-star_size, y-star_size, x+star_size, y+star_size), 
                        fill=star_color)
        elif star_type == 'cross':
            draw.line([(x-star_size, y), (x+star_size, y)], fill=star_color, width=1)
            draw.line([(x, y-star_size), (x, y+star_size)], fill=star_color, width=1)
        elif star_type == 'diamond':
            diamond_points = [(x, y-star_size), (x+star_size, y), (x, y+star_size), (x-star_size, y)]
            draw.polygon(diamond_points, fill=star_color)
    
    # Ocasionalmente agregar luna
    if random.random() < 0.3:
        moon_x = random.randint(size//4, 3*size//4)
        moon_y = random.randint(size//6, size//3)
        moon_size = random.randint(25, 45)
        moon_color = (255, 255, 220)
        
        # Luna llena o creciente
        if random.random() < 0.5:
            draw.ellipse((moon_x-moon_size, moon_y-moon_size, moon_x+moon_size, moon_y+moon_size), 
                        fill=moon_color)
        else:
            # Luna creciente
            draw.ellipse((moon_x-moon_size, moon_y-moon_size, moon_x+moon_size, moon_y+moon_size), 
                        fill=moon_color)
            draw.ellipse((moon_x-moon_size+5, moon_y-moon_size, moon_x+moon_size+5, moon_y+moon_size), 
                        fill=start_color)
    
    return image

def draw_background_flowers(draw, size, cx, cy):
    """Dibuja flores pequeñas de fondo con más variación"""
    # Número variable de flores
    num_flowers = random.randint(3, 8)
    
    # Colores variados para flores de fondo
    flower_colors = [
        [(100, 50, 150), (80, 40, 120)],    # Púrpura
        [(150, 50, 100), (120, 40, 80)],    # Rosa
        [(50, 100, 150), (40, 80, 120)],    # Azul
        [(100, 150, 50), (80, 120, 40)],    # Verde
        [(150, 100, 50), (120, 80, 40)],    # Naranja
        [(120, 80, 150), (100, 60, 120)],   # Violeta
    ]
    
    for i in range(num_flowers):
        # Posición aleatoria que no interfiera con el girasol principal
        attempts = 0
        while attempts < 20:
            fx = random.randint(50, size-50)
            fy = random.randint(50, size-50)
            
            # Verificar que esté lejos del girasol principal
            distance = math.sqrt((fx - cx)**2 + (fy - cy)**2)
            if distance > 200:  # Suficiente distancia
                break
            attempts += 1
        
        flower_size = random.randint(15, 35)
        flower_color = random.choice(flower_colors)
        petal_color, center_color = flower_color
        
        # Tipo de flor aleatoria
        flower_type = random.choice(['daisy', 'simple', 'star'])
        
        if flower_type == 'daisy':
            # Pétalos tipo margarita
            num_petals = random.randint(6, 12)
            for angle in range(0, 360, 360//num_petals):
                rad = math.radians(angle)
                petal_x = fx + flower_size * math.cos(rad)
                petal_y = fy + flower_size * math.sin(rad)
                
                petal_width = random.randint(6, 12)
                petal_height = random.randint(3, 6)
                draw.ellipse((petal_x-petal_width, petal_y-petal_height, 
                            petal_x+petal_width, petal_y+petal_height), 
                           fill=petal_color, outline=center_color)
        
        elif flower_type == 'simple':
            # Pétalos simples
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                petal_x = fx + flower_size * math.cos(rad)
                petal_y = fy + flower_size * math.sin(rad)
                
                draw.ellipse((petal_x-8, petal_y-4, petal_x+8, petal_y+4), 
                           fill=petal_color, outline=center_color)
        
        elif flower_type == 'star':
            # Flor en forma de estrella
            points = []
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                if angle % 90 == 0:
                    x = fx + flower_size * math.cos(rad)
                    y = fy + flower_size * math.sin(rad)
                else:
                    x = fx + (flower_size * 0.6) * math.cos(rad)
                    y = fy + (flower_size * 0.6) * math.sin(rad)
                points.append((x, y))
            draw.polygon(points, fill=petal_color, outline=center_color)
        
        # Centro de la flor
        center_size = random.randint(4, 8)
        center_colors = [(255, 255, 100), (255, 200, 100), (200, 255, 100), (100, 255, 200)]
        center_fill = random.choice(center_colors)
        draw.ellipse((fx-center_size, fy-center_size, fx+center_size, fy+center_size), 
                    fill=center_fill)

def draw_stem_and_leaves(draw, cx, cy, size):
    """Dibuja el tallo y las hojas del girasol con variaciones aleatorias"""
    # Altura del tallo variable
    stem_height_factor = 1.1  # Valor fijo para altura consistente
    stem_bottom = size - random.randint(60, 120)
    
    # Grosor del tallo variable
    stem_width = random.randint(8, 16)
    
    # Colores del tallo con variación
    stem_colors = [
        (34, 139, 34),   # Verde bosque
        (50, 120, 50),   # Verde medio
        (40, 150, 40),   # Verde claro
        (60, 100, 60),   # Verde grisáceo
    ]
    stem_color = random.choice(stem_colors)
    
    # Curvatura del tallo variable
    curve_intensity = random.uniform(0.1, 0.5)
    curve_frequency = random.uniform(0.1, 0.3)
    
    # Dibujar tallo con curvatura variable
    stem_points = []
    stem_length = int((stem_bottom - cy - 80) * stem_height_factor)
    
    for i in range(50):
        y = cy + 80 + stem_length * (i / 49)
        curve = random.randint(2, 8) * curve_intensity * math.sin(i * curve_frequency)
        x = cx + curve
        stem_points.append((x, y))
    
    # Dibujar el tallo
    for i in range(len(stem_points) - 1):
        x1, y1 = stem_points[i]
        x2, y2 = stem_points[i + 1]
        draw.line([(x1, y1), (x2, y2)], fill=stem_color, width=stem_width)
    
    # Sombra del tallo
    shadow_color = tuple(max(0, c - 40) for c in stem_color)
    for i in range(len(stem_points) - 1):
        x1, y1 = stem_points[i]
        x2, y2 = stem_points[i + 1]
        draw.line([(x1+2, y1), (x2+2, y2)], fill=shadow_color, width=stem_width//2)
    
    # Número variable de hojas
    num_leaves = random.randint(3, 7)
    
    # Hojas con posiciones y tamaños variables
    for i in range(num_leaves):
        # Posición aleatoria a lo largo del tallo
        leaf_position = random.uniform(0.2, 0.8)
        leaf_y = cy + 80 + stem_length * leaf_position
        
        # Lado aleatorio del tallo
        side = random.choice([-1, 1])
        leaf_x = cx + side * random.randint(20, 50)
        
        # Propiedades aleatorias de la hoja
        leaf_angle = random.randint(-60, 60) + (side * 30)
        leaf_width = random.randint(30, 60)
        leaf_height = random.randint(50, 100)
        
        if leaf_y < size - 50:
            draw_leaf(draw, leaf_x, leaf_y, leaf_angle, leaf_width, leaf_height)

def draw_leaf(draw, x, y, angle, width, height):
    """Dibuja una hoja detallada con variaciones aleatorias"""
    rad = math.radians(angle)
    
    # Colores de la hoja con variación
    leaf_colors = [
        [(85, 170, 85), (60, 120, 60)],    # Verde normal
        [(70, 150, 70), (50, 100, 50)],    # Verde oscuro
        [(100, 180, 100), (70, 130, 70)],  # Verde claro
        [(80, 160, 80), (55, 110, 55)],    # Verde medio
    ]
    leaf_green, dark_green = random.choice(leaf_colors)
    
    # Forma de hoja variable
    leaf_shape = random.choice(['ellipse', 'pointed', 'serrated'])
    
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    
    # Crear forma de hoja según el tipo
    leaf_points = []
    num_points = 20
    
    for i in range(num_points):
        t = i / (num_points - 1) * 2 * math.pi
        
        if leaf_shape == 'ellipse':
            local_x = width/2 * math.cos(t)
            local_y = height/2 * math.sin(t)
        elif leaf_shape == 'pointed':
            local_x = width/2 * math.cos(t) * (1.5 if abs(t) < math.pi/2 else 0.7)
            local_y = height/2 * math.sin(t) * (1.2 if t < 0 else 0.8)
        elif leaf_shape == 'serrated':
            base_x = width/2 * math.cos(t)
            base_y = height/2 * math.sin(t)
            # Agregar ondulación
            serration = 3 * math.sin(t * 8)
            local_x = base_x + serration * math.cos(t + math.pi/2)
            local_y = base_y + serration * math.sin(t + math.pi/2)
        
        # Rotación
        rotated_x = local_x * cos_a - local_y * sin_a
        rotated_y = local_x * sin_a + local_y * cos_a
        
        leaf_points.append((x + rotated_x, y + rotated_y))
    
    # Dibujar hoja
    draw.polygon(leaf_points, fill=leaf_green, outline=dark_green, width=2)
    
    # Venas de la hoja con patrón variable
    vein_pattern = random.choice(['straight', 'curved', 'branched'])
    num_veins = random.randint(3, 7)
    
    for i in range(-num_veins//2, num_veins//2 + 1):
        if vein_pattern == 'straight':
            vein_start_x = x - height/3 * cos_a
            vein_start_y = y - height/3 * sin_a
            vein_end_x = x + height/3 * cos_a
            vein_end_y = y + height/3 * sin_a
        elif vein_pattern == 'curved':
            curve_factor = i * 0.1
            vein_start_x = x - height/3 * cos_a + curve_factor * width/4
            vein_start_y = y - height/3 * sin_a
            vein_end_x = x + height/3 * cos_a - curve_factor * width/4
            vein_end_y = y + height/3 * sin_a
        elif vein_pattern == 'branched':
            vein_start_x = x
            vein_start_y = y
            vein_end_x = x + (height/3 + i * width/8) * cos_a
            vein_end_y = y + (height/3 + i * width/8) * sin_a
        
        # Vena con offset
        offset_x = i * width/8 * (-sin_a)
        offset_y = i * width/8 * cos_a
        
        draw.line([(vein_start_x + offset_x, vein_start_y + offset_y),
                  (vein_end_x + offset_x, vein_end_y + offset_y)], 
                 fill=dark_green, width=1)

def draw_geometric_petal_enhanced(draw, cx, cy, angle, length, width, fill_color, line_color):
    """Versión mejorada del pétalo geométrico con variaciones aleatorias"""
    rad = math.radians(angle)
    
    # Variaciones aleatorias en la forma del pétalo
    length_variation = random.uniform(0.9, 1.1)
    width_variation = random.uniform(0.8, 1.2)
    
    length *= length_variation
    width *= width_variation
    
    # Calcular puntos del pétalo
    base_dist = random.randint(60, 70)
    tip_dist = length
    
    # Punto base y punta
    base_x = cx + base_dist * math.cos(rad)
    base_y = cy + base_dist * math.sin(rad)
    tip_x = cx + tip_dist * math.cos(rad)
    tip_y = cy + tip_dist * math.sin(rad)
    
    # Puntos laterales con variación
    side_offset = width / 2
    left_angle = rad + math.pi/2
    right_angle = rad - math.pi/2
    
    # Forma del pétalo con variación aleatoria
    asymmetry = random.uniform(0.8, 1.2)
    
    base_left_x = base_x + (width/4) * math.cos(left_angle)
    base_left_y = base_y + (width/4) * math.sin(left_angle)
    base_right_x = base_x + (width/4) * math.cos(right_angle) * asymmetry
    base_right_y = base_y + (width/4) * math.sin(right_angle) * asymmetry
    
    mid_left_x = cx + (tip_dist * 0.7) * math.cos(rad) + side_offset * math.cos(left_angle)
    mid_left_y = cy + (tip_dist * 0.7) * math.sin(rad) + side_offset * math.sin(left_angle)
    mid_right_x = cx + (tip_dist * 0.7) * math.cos(rad) + side_offset * math.cos(right_angle) * asymmetry
    mid_right_y = cy + (tip_dist * 0.7) * math.sin(rad) + side_offset * math.sin(right_angle) * asymmetry
    
    quarter_left_x = cx + (tip_dist * 0.4) * math.cos(rad) + (side_offset*0.8) * math.cos(left_angle)
    quarter_left_y = cy + (tip_dist * 0.4) * math.sin(rad) + (side_offset*0.8) * math.sin(left_angle)
    quarter_right_x = cx + (tip_dist * 0.4) * math.cos(rad) + (side_offset*0.8) * math.cos(right_angle) * asymmetry
    quarter_right_y = cy + (tip_dist * 0.4) * math.sin(rad) + (side_offset*0.8) * math.sin(right_angle) * asymmetry
    
    # Dibujar pétalo con gradiente simulado
    petal_points = [
        (base_left_x, base_left_y),
        (quarter_left_x, quarter_left_y),
        (mid_left_x, mid_left_y),
        (tip_x, tip_y),
        (mid_right_x, mid_right_y),
        (quarter_right_x, quarter_right_y),
        (base_right_x, base_right_y)
    ]
    
    # Variación en el color del pétalo
    color_variation = random.randint(-20, 20)
    varied_color = tuple(max(0, min(255, c + color_variation)) for c in fill_color)
    
    # Base del pétalo
    base_color = tuple(min(255, c + 20) for c in varied_color)
    draw.polygon(petal_points, fill=base_color)
    
    # Centro del pétalo
    inner_points = [
        (quarter_left_x, quarter_left_y),
        (mid_left_x, mid_left_y),
        (tip_x, tip_y),
        (mid_right_x, mid_right_y),
        (quarter_right_x, quarter_right_y)
    ]
    draw.polygon(inner_points, fill=varied_color)
    
    # Líneas internas con patrón variable
    line_pattern = random.choice(['straight', 'curved', 'zigzag'])
    num_lines = random.randint(10, 20)
    
    for i in range(1, num_lines):
        t = i / num_lines
        
        # Líneas principales con variación
        center_x = cx + (base_dist + (tip_dist - base_dist) * t) * math.cos(rad)
        center_y = cy + (base_dist + (tip_dist - base_dist) * t) * math.sin(rad)
        line_width = width * (1 - t * 0.6)
        
        if line_pattern == 'straight':
            left_x = center_x + (line_width/2) * math.cos(left_angle)
            left_y = center_y + (line_width/2) * math.sin(left_angle)
            right_x = center_x + (line_width/2) * math.cos(right_angle)
            right_y = center_y + (line_width/2) * math.sin(right_angle)
        elif line_pattern == 'curved':
            curve_offset = 3 * math.sin(t * math.pi * 4)
            left_x = center_x + (line_width/2) * math.cos(left_angle) + curve_offset
            left_y = center_y + (line_width/2) * math.sin(left_angle)
            right_x = center_x + (line_width/2) * math.cos(right_angle) - curve_offset
            right_y = center_y + (line_width/2) * math.sin(right_angle)
        elif line_pattern == 'zigzag':
            zigzag = 2 * (1 if i % 2 == 0 else -1)
            left_x = center_x + (line_width/2) * math.cos(left_angle) + zigzag
            left_y = center_y + (line_width/2) * math.sin(left_angle)
            right_x = center_x + (line_width/2) * math.cos(right_angle) - zigzag
            right_y = center_y + (line_width/2) * math.sin(right_angle)
        
        line_thickness = random.choice([1, 2, 3]) if i % 3 == 0 else 1
        draw.line([(left_x, left_y), (right_x, right_y)], 
                 fill=line_color, width=line_thickness)
    
    # Contorno del pétalo
    outline_thickness = random.randint(2, 4)
    draw.polygon(petal_points, outline=line_color, width=outline_thickness)
    
    # Línea central con variación
    central_line_thickness = random.randint(2, 4)
    draw.line([(base_x, base_y), (tip_x, tip_y)], fill=line_color, width=central_line_thickness)

def draw_enhanced_center(draw, cx, cy, radius):
    """Centro mejorado con variaciones aleatorias"""
    phi = math.radians(137.508)
    
    # Variación en el tamaño del centro
    radius_variation = random.uniform(0.8, 1.2)
    radius = int(radius * radius_variation)
    
    # Colores del centro con más variación
    center_color_sets = [
        [(139, 0, 0), (165, 42, 42), (178, 34, 34), (220, 20, 60), (255, 69, 0), (128, 0, 0)],  # Rojos
        [(139, 69, 0), (165, 92, 42), (178, 84, 34), (220, 120, 60), (255, 140, 0), (128, 64, 0)],  # Naranjas
        [(100, 0, 100), (125, 42, 125), (148, 34, 148), (180, 20, 180), (200, 69, 200), (90, 0, 90)],  # Púrpuras
        [(139, 139, 0), (165, 165, 42), (178, 178, 34), (220, 220, 60), (255, 255, 0), (128, 128, 0)],  # Amarillos
    ]
    
    center_colors = random.choice(center_color_sets)
    
    # Fondo del centro con gradiente
    for r in range(radius, 0, -2):
        alpha = 1 - (r / radius)
        color_idx = int(alpha * (len(center_colors) - 1))
        color = center_colors[min(color_idx, len(center_colors) - 1)]
        
        # Variación en el color
        varied_color = tuple(max(0, min(255, c + random.randint(-15, 15))) for c in color)
        draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=varied_color)
    
    # Patrón de semillas con variación
    seed_pattern = random.choice(['spiral', 'concentric', 'random'])
    num_seeds = random.randint(800, 1200)
    
    for i in range(num_seeds):
        if seed_pattern == 'spiral':
            r = 1.5 * math.sqrt(i)
            theta = i * phi
        elif seed_pattern == 'concentric':
            r = (i % 50) * (radius / 50)
            theta = (i // 50) * (2 * math.pi / 20)
        elif seed_pattern == 'random':
            r = random.uniform(0, radius - 5)
            theta = random.uniform(0, 2 * math.pi)
        
        if r > radius - 5:
            continue
            
        x = cx + r * math.cos(theta)
        y = cy + r * math.sin(theta)
        
        # Tamaño variable con más variación
        base_size = 2.5 - (r / radius) * 1.5
        size_variation = random.uniform(0.5, 1.5)
        seed_size = max(0.3, base_size * size_variation)
        
        # Color con más variación
        base_color = random.choice(center_colors)
        color_shift = random.randint(-40, 40)
        color = tuple(max(0, min(255, c + color_shift)) for c in base_color)
        
        # Forma variable de semilla
        seed_shape = random.choice(['circle', 'oval', 'diamond'])
        offset = random.uniform(-1, 1)
        
        if seed_shape == 'circle':
            draw.ellipse((x-seed_size+offset, y-seed_size+offset, 
                         x+seed_size+offset, y+seed_size+offset), fill=color)
        elif seed_shape == 'oval':
            draw.ellipse((x-seed_size*1.2+offset, y-seed_size*0.8+offset, 
                         x+seed_size*1.2+offset, y+seed_size*0.8+offset), fill=color)
        elif seed_shape == 'diamond':
            diamond_points = [
                (x+offset, y-seed_size+offset),
                (x+seed_size+offset, y+offset),
                (x+offset, y+seed_size+offset),
                (x-seed_size+offset, y+offset)
            ]
            draw.polygon(diamond_points, fill=color)
        
        # Destellos ocasionales con más variación
        if random.random() < 0.08:
            highlight_colors = [(255, 255, 200), (255, 200, 255), (200, 255, 255), (255, 255, 255)]
            highlight_color = random.choice(highlight_colors)
            highlight_size = seed_size * random.uniform(0.2, 0.5)
            draw.ellipse((x-highlight_size, y-highlight_size, 
                         x+highlight_size, y+highlight_size), fill=highlight_color)

def draw_message_container(draw, cx, size, text):
    """Dibuja el contenedor del mensaje con variaciones aleatorias"""
    text_y = size - 70
    
    # Simular tamaño del texto
    bbox = draw.textbbox((0, 0), text)
    text_width = bbox[2] - bbox[0]
    text_x = cx - text_width // 2
    
    # Tipos de contenedor
    container_types = ['rectangle', 'rounded', 'oval', 'banner', 'cloud']
    container_type = random.choice(container_types)
    
    # Colores del contenedor
    container_colors = [
        [(0, 0, 0), (40, 40, 40), (255, 215, 0)],      # Negro
        [(255, 255, 255), (200, 200, 200), (0, 0, 0)],        # Blanco
        [(34, 139, 34), (60, 179, 113), (255, 255, 255)],     # Verde
        [(70, 130, 180), (135, 206, 235), (255, 255, 255)],   # Azul
        [(220, 20, 60), (255, 182, 193), (255, 255, 255)],    # Rosa
        [(255, 165, 0), (255, 218, 185), (0, 0, 0)],          # Naranja
        [(148, 0, 211), (221, 160, 221), (255, 255, 255)],    # Púrpura
    ]
    
    bg_color, border_color, text_color = random.choice(container_colors)
    
    # Tamaños y posiciones con variación
    padding = random.randint(15, 25)
    container_height = random.randint(40, 60)
    
    # Dibujar según el tipo de contenedor
    if container_type == 'rectangle':
        draw.rectangle((text_x - padding, text_y - padding,
                       text_x + text_width + padding, text_y + container_height),
                      fill=bg_color, outline=border_color, width=3)
    
    elif container_type == 'rounded':
        # Simular esquinas redondeadas con múltiples rectángulos
        corner_radius = random.randint(8, 15)
        draw.rounded_rectangle((text_x - padding, text_y - padding,
                               text_x + text_width + padding, text_y + container_height),
                              radius=corner_radius, fill=bg_color, outline=border_color, width=3)
    
    elif container_type == 'oval':
        draw.ellipse((text_x - padding, text_y - padding,
                     text_x + text_width + padding, text_y + container_height),
                    fill=bg_color, outline=border_color, width=3)
    
    elif container_type == 'banner':
        # Banner con puntas
        banner_points = [
            (text_x - padding, text_y - padding),
            (text_x + text_width + padding, text_y - padding),
            (text_x + text_width + padding + 10, text_y + container_height//2),
            (text_x + text_width + padding, text_y + container_height),
            (text_x - padding, text_y + container_height),
            (text_x - padding - 10, text_y + container_height//2)
        ]
        draw.polygon(banner_points, fill=bg_color, outline=border_color, width=3)
    
    elif container_type == 'cloud':
        # Nube con círculos
        cloud_circles = [
            (text_x - padding + 20, text_y + 10, 15),
            (text_x + 20, text_y - 5, 18),
            (text_x + text_width//2, text_y - 10, 20),
            (text_x + text_width - 20, text_y - 5, 18),
            (text_x + text_width + padding - 20, text_y + 10, 15),
            (text_x + text_width//2, text_y + 25, 16)
        ]
        
        for cx_cloud, cy_cloud, radius in cloud_circles:
            draw.ellipse((cx_cloud - radius, cy_cloud - radius,
                         cx_cloud + radius, cy_cloud + radius),
                        fill=bg_color, outline=border_color, width=2)
    
    # Efectos adicionales aleatorios
    if random.random() < 0.3:
        # Sombra
        shadow_offset = random.randint(3, 8)
        shadow_color = tuple(max(0, c - 100) for c in bg_color)
        if container_type == 'rectangle':
            draw.rectangle((text_x - padding + shadow_offset, text_y - padding + shadow_offset,
                           text_x + text_width + padding + shadow_offset, text_y + container_height + shadow_offset),
                          fill=shadow_color)
    
    if random.random() < 0.2:
        # Brillo interno
        shine_color = tuple(min(255, c + 50) for c in bg_color)
        shine_size = random.randint(5, 10)
        draw.ellipse((text_x + shine_size, text_y + shine_size,
                     text_x + shine_size + 20, text_y + shine_size + 20),
                    fill=shine_color)
    
    return text_color

def create_girasol(numero):
    """Crea un girasol único con variaciones aleatorias"""
    size = 600
    
    # Crear imagen base con fondo aleatorio
    image = create_gradient_sky(size)
    draw = ImageDraw.Draw(image)
    
    # Posición del girasol con variación
    center_variation = random.randint(-50, 50)
    cx = size // 2 + center_variation
    cy = size // 2 - random.randint(50, 100)
    
    # Dibujar flores de fondo
    draw_background_flowers(draw, size, cx, cy)
    
    # Dibujar tallo y hojas
    draw_stem_and_leaves(draw, cx, cy, size)
    
    # Pétalos con variación
    petal_colors = [
        [(255, 215, 0), (255, 140, 0), (184, 134, 11)],    # Amarillo dorado
        [(255, 255, 0), (255, 215, 0), (184, 134, 11)],    # Amarillo clásico
        [(255, 165, 0), (255, 140, 0), (184, 134, 11)],    # Naranja
        [(255, 235, 59), (255, 193, 7), (184, 134, 11)],   # Amarillo brillante
        [(255, 183, 77), (255, 152, 0), (184, 134, 11)],   # Ámbar
    ]
    
    selected_colors = random.choice(petal_colors)
    petal_color, petal_accent, petal_line = selected_colors
    
    # Número de pétalos variable
    num_petals = random.randint(16, 24)
    
    # Longitud y ancho de pétalos con variación
    petal_length = random.randint(90, 130)
    petal_width = random.randint(35, 55)
    
    # Dibujar pétalos
    for i in range(num_petals):
        angle = (360 / num_petals) * i + random.randint(-5, 5)
        # Variación individual por pétalo
        individual_length = petal_length + random.randint(-15, 15)
        individual_width = petal_width + random.randint(-8, 8)
        
        draw_geometric_petal_enhanced(draw, cx, cy, angle, individual_length, 
                                    individual_width, petal_color, petal_line)
    
    # Centro del girasol
    center_radius = random.randint(45, 65)
    draw_enhanced_center(draw, cx, cy, center_radius)
    
    # Efectos atmosféricos aleatorios
    if random.random() < 0.4:
        # Partículas flotantes (polen, polvo)
        num_particles = random.randint(10, 30)
        for _ in range(num_particles):
            px = random.randint(0, size)
            py = random.randint(0, size)
            particle_size = random.randint(1, 4)
            particle_colors = [(255, 255, 200), (255, 215, 0), (255, 255, 255), (200, 200, 200)]
            particle_color = random.choice(particle_colors)
            draw.ellipse((px-particle_size, py-particle_size, 
                         px+particle_size, py+particle_size), 
                        fill=particle_color)
    
    # Efectos de luz aleatorios
    if random.random() < 0.3:
        # Rayos de sol
        num_rays = random.randint(3, 8)
        for _ in range(num_rays):
            ray_x = random.randint(0, size)
            ray_y = random.randint(0, size//3)
            ray_length = random.randint(50, 150)
            ray_angle = random.randint(45, 135)
            ray_color = (255, 255, 200, 50)  # Semi-transparente
            
            ray_end_x = ray_x + ray_length * math.cos(math.radians(ray_angle))
            ray_end_y = ray_y + ray_length * math.sin(math.radians(ray_angle))
            
            # Simular transparencia con líneas más claras
            for i in range(3):
                offset = i * 2
                light_color = tuple(max(0, min(255, c + 30 - i*10)) for c in (255, 255, 150))
                draw.line([(ray_x + offset, ray_y + offset), 
                          (ray_end_x + offset, ray_end_y + offset)], 
                         fill=light_color, width=2)
    
    # Mensaje con contenedor aleatorio
    message = f"Te quiero ❤️ #{numero}"
    text_color = draw_message_container(draw, cx, size, message)
    
    # Dibujar texto
    text_y = size - 70
    bbox = draw.textbbox((0, 0), message)
    text_width = bbox[2] - bbox[0]
    text_x = cx - text_width // 2
    
    # Fuente simulada más grande
    font_size = random.randint(16, 24)
    for offset_x in range(-1, 2):
        for offset_y in range(-1, 2):
            if offset_x == 0 and offset_y == 0:
                continue
            draw.text((text_x + offset_x, text_y + offset_y), message, 
                     fill=(0, 0, 0), anchor="lt")
    
    draw.text((text_x, text_y), message, fill=text_color, anchor="lt")
    
    # Efectos finales aleatorios
    if random.random() < 0.2:
        # Mariposa ocasional
        butterfly_x = random.randint(100, size-100)
        butterfly_y = random.randint(100, size-200)
        butterfly_colors = [(255, 0, 255), (0, 255, 255), (255, 255, 0), (255, 0, 0)]
        butterfly_color = random.choice(butterfly_colors)
        
        # Alas de mariposa simples
        wing_size = random.randint(8, 15)
        draw.ellipse((butterfly_x-wing_size, butterfly_y-wing_size//2,
                     butterfly_x, butterfly_y+wing_size//2), fill=butterfly_color)
        draw.ellipse((butterfly_x, butterfly_y-wing_size//2,
                     butterfly_x+wing_size, butterfly_y+wing_size//2), fill=butterfly_color)
        
        # Cuerpo
        draw.line([(butterfly_x, butterfly_y-wing_size//2),
                  (butterfly_x, butterfly_y+wing_size//2)], fill=(0, 0, 0), width=2)
    
    if random.random() < 0.25:
        # Abeja ocasional
        bee_x = random.randint(150, size-150)
        bee_y = random.randint(150, size-150)
        
        # Cuerpo de abeja
        draw.ellipse((bee_x-8, bee_y-4, bee_x+8, bee_y+4), fill=(255, 255, 0))
        draw.ellipse((bee_x-6, bee_y-3, bee_x+6, bee_y+3), fill=(0, 0, 0))
        
        # Rayas
        for i in range(3):
            stripe_x = bee_x - 6 + i * 4
            draw.line([(stripe_x, bee_y-3), (stripe_x, bee_y+3)], fill=(0, 0, 0), width=1)
        
        # Alas
        draw.ellipse((bee_x-4, bee_y-6, bee_x+4, bee_y-2), fill=(255, 255, 255, 128))
    
    # Aplicar filtro final ocasional
    if random.random() < 0.1:
        # Ligero desenfoque para efecto dreamy
        image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    return image

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
        
        # Paleta de colores expandida
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
            "confetti_colors": ["#4CAF50", "#FFC107", "#2196F3", "#FF5722", "#9C27B0", "#3F51B5", "#00BCD4", "#009688"],
            "cake_colors": ["#ff69b4", "#98fb98", "#ffd700", "#ff6347", "#dda0dd", "#f0e68c", "#ffa07a", "#87ceeb"],
            "text_colors": ["#ff1493", "#ff4500", "#9932cc", "#228b22", "#dc143c", "#ff8c00", "#4169e1", "#8b008b"]
        }
        
        # CARACTERÍSTICAS ALEATORIAS ESPECIALES
        # 1. Determinar número de pisos (2-4 pisos)
        num_layers = random.choice([2, 3, 4])
        
        # 2. Determinar si habrá globos
        has_balloons = random.choice([True, False])
        
        # 3. Determinar estilo del texto
        text_style = random.choice(['normal', 'rainbow', 'shadow_heavy', 'outline'])
        text_color = random.choice(colors["text_colors"])
        
        # 4. Determinar decoraciones especiales
        special_decoration = random.choice(['stars', 'hearts', 'flowers', 'sparkles', 'none'])
        
        # 5. Determinar si tendrá cobertura extra
        has_extra_frosting = random.choice([True, False])
        
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
        
        # NUEVA: Función para dibujar globos
        def draw_balloon(x, y, balloon_color):
            # Globo
            draw.ellipse([x-15, y-25, x+15, y+25], fill=balloon_color, outline="#ffffff", width=2)
            # Highlight del globo
            draw.ellipse([x-8, y-15, x-3, y-10], fill="#ffffff", outline=None)
            # Cuerda del globo
            draw.line([x, y+25, x+random.randint(-5, 5), y+60], fill="#333333", width=2)
        
        # NUEVA: Función para decoraciones especiales
        def draw_special_decoration(decoration_type, x, y):
            if decoration_type == 'stars':
                # Dibujar estrella
                points = []
                for i in range(10):
                    angle = i * 36 * 3.14159 / 180
                    radius = 8 if i % 2 == 0 else 4
                    px = x + radius * math.cos(angle)
                    py = y + radius * math.sin(angle)
                    points.append((px, py))
                draw.polygon(points, fill=colors["golden_yellow"], outline="#ffffff")
            
            elif decoration_type == 'hearts':
                # Dibujar corazón simplificado
                draw.ellipse([x-6, y-4, x+2, y+4], fill="#ff69b4", outline="#ffffff")
                draw.ellipse([x-2, y-4, x+6, y+4], fill="#ff69b4", outline="#ffffff")
                draw.polygon([(x-6, y), (x, y+8), (x+6, y)], fill="#ff69b4", outline="#ffffff")
            
            elif decoration_type == 'flowers':
                # Dibujar flor simple
                center_color = random.choice(colors["confetti_colors"])
                petal_color = random.choice(colors["cake_colors"])
                # Pétalos
                for i in range(6):
                    angle = i * 60 * 3.14159 / 180
                    px = x + 6 * math.cos(angle)
                    py = y + 6 * math.sin(angle)
                    draw.ellipse([px-3, py-3, px+3, py+3], fill=petal_color, outline="#ffffff")
                # Centro
                draw.ellipse([x-2, y-2, x+2, y+2], fill=center_color, outline="#ffffff")
            
            elif decoration_type == 'sparkles':
                # Dibujar destello
                draw.line([x-6, y, x+6, y], fill="#ffff00", width=2)
                draw.line([x, y-6, x, y+6], fill="#ffff00", width=2)
                draw.line([x-4, y-4, x+4, y+4], fill="#ffff00", width=2)
                draw.line([x-4, y+4, x+4, y-4], fill="#ffff00", width=2)
        
        # Importar math para las decoraciones
        import math
        
        # Dibujar el pastel por capas (de abajo hacia arriba) - NÚMERO VARIABLE DE PISOS
        center_x = width // 2
        
        # Configurar pisos según el número aleatorio
        if num_layers == 2:
            # Pastel de 2 pisos
            base_y = height - 150
            draw_cake_layer(center_x, base_y, 140, 80, random.choice(colors["cake_colors"]), "#ffffff")
            
            top_y = base_y - 70
            draw_cake_layer(center_x, top_y, 90, 60, random.choice(colors["cake_colors"]), "#ffffff")
            
            candle_y = top_y - 60
            
        elif num_layers == 3:
            # Pastel de 3 pisos (original)
            base_y = height - 150
            draw_cake_layer(center_x, base_y, 150, 80, random.choice(colors["cake_colors"]), "#ffffff")
            
            middle_y = base_y - 70
            draw_cake_layer(center_x, middle_y, 120, 70, random.choice(colors["cake_colors"]), "#ffffff")
            
            top_y = middle_y - 60
            draw_cake_layer(center_x, top_y, 80, 50, random.choice(colors["cake_colors"]), "#ffffff")
            
            candle_y = top_y - 50
            
        else:  # num_layers == 4
            # Pastel de 4 pisos
            base_y = height - 160
            draw_cake_layer(center_x, base_y, 160, 70, random.choice(colors["cake_colors"]), "#ffffff")
            
            second_y = base_y - 60
            draw_cake_layer(center_x, second_y, 130, 60, random.choice(colors["cake_colors"]), "#ffffff")
            
            third_y = second_y - 55
            draw_cake_layer(center_x, third_y, 100, 50, random.choice(colors["cake_colors"]), "#ffffff")
            
            top_y = third_y - 50
            draw_cake_layer(center_x, top_y, 70, 40, random.choice(colors["cake_colors"]), "#ffffff")
            
            candle_y = top_y - 40
        
        # Cobertura superior (opcional)
        if has_extra_frosting:
            frosting_width = 60 if num_layers == 4 else 70
            draw_ellipse_layer(center_x, candle_y, frosting_width, 20, colors["cream"], colors["dark_brown"])
        
        # Posiciones de las velas (adaptadas al número de pisos)
        if num_layers == 2:
            candle_positions = [
                (center_x, candle_y),
                (center_x - 30, candle_y + 5),
                (center_x + 30, candle_y + 5)
            ]
        elif num_layers == 3:
            candle_positions = [
                (center_x, candle_y),
                (center_x - 40, candle_y + 5),
                (center_x + 40, candle_y + 5),
                (center_x - 20, candle_y - 5),
                (center_x + 20, candle_y - 5)
            ]
        else:  # 4 pisos
            candle_positions = [
                (center_x, candle_y),
                (center_x - 25, candle_y + 3),
                (center_x + 25, candle_y + 3),
                (center_x - 12, candle_y - 3),
                (center_x + 12, candle_y - 3),
                (center_x - 35, candle_y + 8),
                (center_x + 35, candle_y + 8)
            ]
        
        # Dibujar velas
        for pos in candle_positions:
            draw_candle(pos[0], pos[1])
        
        # Dibujar globos si fueron seleccionados
        if has_balloons:
            balloon_colors = random.sample(colors["confetti_colors"], 3)
            balloon_positions = [
                (150, 200),
                (750, 180),
                (100, 300)
            ]
            for i, pos in enumerate(balloon_positions):
                draw_balloon(pos[0], pos[1], balloon_colors[i])
        
        # Agregar confeti de fondo
        add_confetti(30)
        
        # Decoraciones adicionales en el pastel
        # Puntos decorativos en las capas (adaptados al número de pisos)
        for layer in range(num_layers):
            num_dots = random.randint(8, 15)
            for _ in range(num_dots):
                x = random.randint(center_x - 140, center_x + 140)
                y_base = height - 150 - (layer * 65)
                y = random.randint(y_base - 30, y_base + 15)
                color = random.choice(colors["confetti_colors"])
                draw.ellipse([x-3, y-3, x+3, y+3], fill=color)
        
        # Decoraciones especiales
        if special_decoration != 'none':
            for _ in range(random.randint(5, 12)):
                x = random.randint(100, width-100)
                y = random.randint(150, height-150)
                draw_special_decoration(special_decoration, x, y)
        
        # Texto "Happy Birthday" con estilos variables
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
            
            # Variar el texto ocasionalmente
            text_variations = [
                "Happy Birthday",
                "¡Feliz Cumpleaños!",
                "Happy B-Day!",
                "Celebration Time!",
                "¡Que lo disfrutes!"
            ]
            text = random.choice(text_variations)
            
            # Calcular posición centrada para el texto
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = (width - text_width) // 2
            text_y = 50
            
            # Aplicar estilo del texto
            if text_style == 'normal':
                draw.text((text_x + 2, text_y + 2), text, fill="#333333", font=font)
                draw.text((text_x, text_y), text, fill=text_color, font=font)
            
            elif text_style == 'rainbow':
                # Texto arcoíris
                rainbow_colors = ["#ff0000", "#ff7f00", "#ffff00", "#00ff00", "#0000ff", "#4b0082", "#9400d3"]
                for i, char in enumerate(text):
                    char_color = rainbow_colors[i % len(rainbow_colors)]
                    char_bbox = draw.textbbox((0, 0), text[:i], font=font)
                    char_x = text_x + (char_bbox[2] - char_bbox[0]) if i > 0 else text_x
                    draw.text((char_x, text_y), char, fill=char_color, font=font)
            
            elif text_style == 'shadow_heavy':
                # Sombra pesada
                for offset in range(1, 6):
                    draw.text((text_x + offset, text_y + offset), text, fill="#333333", font=font)
                draw.text((text_x, text_y), text, fill=text_color, font=font)
            
            elif text_style == 'outline':
                # Texto con contorno
                for adj in range(-2, 3):
                    for adj2 in range(-2, 3):
                        draw.text((text_x + adj, text_y + adj2), text, fill="#000000", font=font)
                draw.text((text_x, text_y), text, fill=text_color, font=font)
            
        except Exception as e:
            print(f"Error con fuente: {e}")
            # Fallback sin fuente especial
            draw.text((center_x - 100, 50), "Happy Birthday!", fill=text_color)
        
        # Más confeti decorativo
        add_confetti(20)
        
        # Guardar imagen
        img.save(png_path, 'PNG', quality=95)
        
        # Mensaje personalizado basado en las características especiales
        special_features = []
        if num_layers == 4:
            special_features.append("¡4 pisos de delicia!")
        elif num_layers == 2:
            special_features.append("¡Diseño minimalista de 2 pisos!")
        if has_balloons:
            special_features.append("¡Con globos festivos!")
        if special_decoration != 'none':
            special_features.append(f"¡Decorado con mucho cariño!")
        if has_extra_frosting:
            special_features.append("¡Con cobertura extra!")
        
        message = f"¡Pastel horneado exitosamente! {' '.join(special_features)} ¡Disfrutalo!"
        
        return jsonify({
            'success': True,
            'image_url': url_for('static', filename=f'mensajes/{filename}'),
            'message': message
        })
        
    except Exception as e:
        print(f"Error generando pastel: {e}")
        return jsonify({
            'success': False,
            'error': f'Error al generar el pastel: {str(e)}'
        }), 500
    

@app.route('/generate_song')
def generate_song():
    import time
    import os
    import random
    from flask import jsonify, url_for, Response
    import json
    
    try:
        songs = {
        "motivational": {
            "title": "Canción Motivacional",
            "lyrics": [
                ("Ya sé que los recuerdos no siguen la ley de gravedad", 0.07),
                ("Que el tiempo pasa y nos convierte en lo que fuimos", 0.07),
                ("Lo que me aterra comprobar es que la vida va a toda velocidad", 0.07),
                ("No tiene sentido", 0.07),
                ("Me duele la verdad", 0.07),
                ("Que pronto crecimos", 0.07)
            ],
            "delays": [0.3, 3.2, 6.5, 10.0, 12.5, 15.0],
            "background_color": "#2c3e50",
            "text_color": "#ecf0f1"
        },
        "happy_birthday": {
            "title": "Feliz Cumpleaños",
            "lyrics": [
                ("🎵 Happy birthday to you", 0.08),
                ("Happy birthday to you", 0.08),
                ("Happy birthday Nicolle", 0.09),
                ("Happy birthday to you! 🎵", 0.08),
                ("🎉 Make a wish!", 0.12),
                ("Blow out the candles", 0.10),
                ("May all your dreams", 0.08),
                ("Come true today! ✨", 0.08)
            ],
            "delays": [0.5, 4.0, 8.0, 12.5, 17.0, 20.0, 24.0, 28.0],
            "background_color": "#e74c3c",
            "text_color": "#ffffff"
        },
        "celebration": {
            "title": "Celebración",
            "lyrics": [
                ("Alzaré mis ojos a los montes", 0.08),
                ("Te veré radiante como el sol", 0.08),
                ("Seguiré el brillo de tu gracia", 0.08),
                ("Porque sé que Tú sigues siendo Dios", 0.08),
                ("Tú sigues siendo Diooooos", 0.10)
            ],
            "delays": [0.5, 3.5, 7.0, 10.5, 14.0],
            "background_color": "#9b59b6",
            "text_color": "#ffffff"
        },
        "friendship": {
            "title": "Amistad",
            "lyrics": [
                ("Porque un amigo es una luz", 0.08),
                ("Brillando en la oscuridad", 0.08),
                ("Siempre serás mi amigaaa", 0.08),
                ("No importa nada más", 0.08),
                ("Porque siempre estarán en mí", 0.09),
                ("Esos buenos momentos que pasamos sin saber", 0.08)
            ],
            "delays": [0.5, 4.0, 8.0, 12.0, 16.0, 19.5],
            "background_color": "#27ae60",
            "text_color": "#ffffff"
        }
    }
        
        # Seleccionar canción aleatoria
        song_key = random.choice(list(songs.keys()))
        selected_song = songs[song_key]
        
        # Crear timestamp para identificar la sesión
        timestamp = int(time.time())
        session_id = f"song_{timestamp}"
        
        # Preparar datos para enviar al frontend
        song_data = {
            "session_id": session_id,
            "title": selected_song["title"],
            "lyrics": selected_song["lyrics"],
            "delays": selected_song["delays"],
            "background_color": selected_song["background_color"],
            "text_color": selected_song["text_color"],
            "total_duration": max(selected_song["delays"]) + 5  # Duración total aproximada
        }
        
        # Mensajes motivacionales aleatorios
        motivational_messages = [
            "🎵 ¡La música alimenta el alma!",
            "🎶 ¡Que la melodía llene tu corazón!",
            "✨ ¡Cada nota es un momento especial!",
            "🎼 ¡La música es el lenguaje universal!",
            "🌟 ¡Deja que la canción te inspire!",
            "💫 ¡Música para momentos únicos!",
            "🎵 ¡Cantemos juntos esta melodía!",
            "🎉 ¡Que la música ilumine tu día!"
        ]
        
        return jsonify({
            'success': True,
            'song_data': song_data,
            'message': random.choice(motivational_messages)
        })
        
    except Exception as e:
        print(f"Error generando canción: {e}")
        return jsonify({
            'success': False,
            'error': f'Error al generar la canción: {str(e)}'
        }), 500


# Función adicional para obtener el progreso de la canción en tiempo real
@app.route('/song_progress/<session_id>')
def song_progress(session_id):
    """Endpoint para obtener el progreso de la canción en tiempo real"""
    try:
        # Aquí podrías implementar lógica para trackear el progreso
        # Por simplicidad, devolvemos un estado básico
        return jsonify({
            'success': True,
            'status': 'playing',
            'session_id': session_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Función para crear una canción personalizada
@app.route('/create_custom_song', methods=['POST'])
def create_custom_song():
    """Permite crear una canción personalizada con texto del usuario"""
    try:
        from flask import request
        
        data = request.get_json()
        
        # Validar datos recibidos
        if not data or 'custom_lyrics' not in data:
            return jsonify({
                'success': False,
                'error': 'No se proporcionaron letras personalizadas'
            }), 400
        
        custom_lyrics = data['custom_lyrics']
        
        # Procesar las letras personalizadas
        processed_lyrics = []
        delays = []
        
        lines = custom_lyrics.split('\n')
        current_delay = 0.5
        
        for line in lines:
            if line.strip():  # Ignorar líneas vacías
                # Ajustar velocidad basada en la longitud de la línea
                speed = 0.08 if len(line) < 20 else 0.06 if len(line) < 40 else 0.04
                processed_lyrics.append((line.strip(), speed))
                delays.append(current_delay)
                current_delay += len(line) * speed + 1.5  # Pausa entre líneas
        
        # Colores aleatorios para canciones personalizadas
        color_themes = [
            {"background": "#3498db", "text": "#ffffff"},
            {"background": "#e67e22", "text": "#ffffff"},
            {"background": "#1abc9c", "text": "#ffffff"},
            {"background": "#34495e", "text": "#ecf0f1"},
            {"background": "#8e44ad", "text": "#ffffff"},
        ]
        
        theme = random.choice(color_themes)
        
        # Crear timestamp
        timestamp = int(time.time())
        session_id = f"custom_song_{timestamp}"
        
        song_data = {
            "session_id": session_id,
            "title": "Canción Personalizada",
            "lyrics": processed_lyrics,
            "delays": delays,
            "background_color": theme["background"],
            "text_color": theme["text"],
            "total_duration": current_delay + 3
        }
        
        return jsonify({
            'success': True,
            'song_data': song_data,
            'message': '🎵 ¡Tu canción personalizada está lista!'
        })
        
    except Exception as e:
        print(f"Error creando canción personalizada: {e}")
        return jsonify({
            'success': False,
            'error': f'Error al crear la canción personalizada: {str(e)}'
        }), 500    


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
