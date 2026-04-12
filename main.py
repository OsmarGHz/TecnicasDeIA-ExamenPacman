import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import math
import os
import numpy as np
import pandas as pd
import time

# Se carga el archivo de la clase Cubo
import sys
sys.path.append('..')
from Pacman import Pacman
from Ghost import Ghost


screen_width = 900
screen_height = 800
#vc para el obser.
FOVY=60.0
ZNEAR=0.01
ZFAR=900.0
#Variables para definir la posicion del observador
#gluLookAt(EYE_X,EYE_Y,EYE_Z,CENTER_X,CENTER_Y,CENTER_Z,UP_X,UP_Y,UP_Z)
EYE_X = 200.0
EYE_Y = 400.0
EYE_Z = 200.0
CENTER_X = 200.0
CENTER_Y = 0.0
CENTER_Z = 200.0
UP_X=0.0
UP_Y=0.0
UP_Z=-1.0
#Variables para dibujar los ejes del sistema
X_MIN=-500
X_MAX=500
Y_MIN=-500
Y_MAX=500
Z_MIN=-500
Z_MAX=500
#Dimension del plano
DimBoard = 400


#Arreglo para el manejo de texturas
textures = []
#Nombre de los archivos a usar
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
file_1 = os.path.join(BASE_PATH, 'mapa.bmp')
img_pacman = os.path.join(BASE_PATH, 'pacman.bmp')
img_ghost1 = os.path.join(BASE_PATH, 'fantasma1.bmp')
img_ghost2 = os.path.join(BASE_PATH, 'fantasma2.bmp')
img_ghost3 = os.path.join(BASE_PATH, 'fantasma3.bmp')
img_ghost4 = os.path.join(BASE_PATH, 'fantasma4.bmp')


file_csv = os.path.join(BASE_PATH, 'mapa.csv')
matrix = np.array(pd.io.parsers.read_csv(file_csv, header=None)).astype("int")
zmatrix = len(matrix)
xmatrix = len(matrix[0])


#Arreglos para imprimir intersecciones en el mapa del pacman
zarray = [-180 + 200, -128 + 200, -90 + 200, -50 + 200, -12 + 200, 28 + 200, 64 + 200, 102 + 200, 140 + 200, 180 + 200]
xarray = [-180 + 200, -150 + 200, -108 + 200, -65 + 200, -22 + 200, 21 + 200, 64 + 200, 107 + 200, 149 + 200, 178 + 200]

#Matriz de Control para mapeo entre pixeles <-> coord donde se localizan esquinas
MC = [
    [10,0,21,0,11,10,0,21,0,11],
    [24,0,25,21,23,23,21,25,0,22],
    [12,0,22,12,11,10,13,24,0,13],
    [0,0,0,10,23,23,11,0,0,0],
    [26,0,25,22,0,0,24,25,0,27],
    [0,0,0,24,0,0,22,0,0,0],
    [10,0,25,23,11,10,23,25,0,11],
    [12,11,24,21,23,23,21,22,10,13],
    [10,23,13,12,11,10,13,12,23,11],
    [12,0,0,0,23,23,0,0,0,13]
]

xMC = [0,30,71,114,156,199,242,286,328,358]

#XPxToMC = np.zeros((359,), dtype=int)
XPxToMC = np.full(359, -1, dtype=int)
XPxToMC[0] = 0
XPxToMC[30] = 1
XPxToMC[71] = 2
XPxToMC[114] = 3
XPxToMC[156] = 4
XPxToMC[199] = 5
XPxToMC[242] = 6
XPxToMC[286] = 7
XPxToMC[328] = 8
XPxToMC[358] = 9
 
yMC = [0,51,90,130,168,208,244,282,320,360]
#YPxToMC = np.zeros((361,), dtype=int)
YPxToMC = np.full(361, -1, dtype=int)
YPxToMC[0] = 0
YPxToMC[51] = 1
YPxToMC[90] = 2
YPxToMC[130] = 3
YPxToMC[168] = 4
YPxToMC[208] = 5
YPxToMC[244] = 6
YPxToMC[282] = 7
YPxToMC[320] = 8
YPxToMC[360] = 9

#pathfinding variables
path = []
grid = []

#pacman object
pc = Pacman(matrix, MC, XPxToMC, YPxToMC)
#fantasmas
ghosts = []
ghosts.append(Ghost(matrix, MC, XPxToMC, YPxToMC, 378, 380, 2, 2)) # Naranja Clyde
ghosts.append(Ghost(matrix, MC, XPxToMC, YPxToMC, 378, 20, 0, 2)) # Azul Inky
ghosts.append(Ghost(matrix, MC, XPxToMC, YPxToMC, 20, 380, 3, 1)) # Rosa Pinky
ghosts.append(Ghost(matrix, MC, XPxToMC, YPxToMC, 20, 380, 3, 0)) # Rojo Blinky


#posicion inicial de la camara para la animacion de intro (vista cinematica)
INTRO_EYE_START    = [200.0, 600.0, 800.0]
INTRO_CENTER_START = [200.0, 0.0,   200.0]
INTRO_UP_START     = [0.0,   1.0,   0.0]
#posicion final = la posicion normal del juego
INTRO_EYE_END    = [EYE_X, EYE_Y, EYE_Z]
INTRO_CENTER_END = [CENTER_X, CENTER_Y, CENTER_Z]
INTRO_UP_END     = [UP_X, UP_Y, UP_Z]
#duraciones en segundos
INTRO_DURATION = 3.0
READY_DURATION = 1.5
GO_DURATION    = 0.8

#interpolacion lineal entre dos valores
def lerp(a, b, t):
    return a + (b - a) * t

#interpolacion lineal entre dos vectores [x,y,z]
def lerp_vec(v1, v2, t):
    return [lerp(v1[i], v2[i], t) for i in range(3)]

#easing: arranca rapido y frena al final (hace que se vea mas natural)
def ease_out_cubic(t):
    return 1.0 - (1.0 - t) ** 3

#genera un sonido de inicio tipo arcade con tonos ascendentes
def generar_sonido_inicio():
    sample_rate = 44100
    #notas: Do-Mi-Sol-Do alto (acorde mayor ascendente)
    #notas = [523, 659, 784, 1047] #C5, E5, G5, C6 pero puestos en Hz
    notas = [246, 494, 370, 311, 494, 370, 311, 0, 246, 520, 370, 311, 520, 370, 311, 0, 246, 494, 370, 311, 494, 370, 311, 0, 312, 0, 330, 0, 376, 0, 494, 0]
    duracion_nota = 0.15
    
    sonido_completo = np.array([], dtype=np.int16)
    
    for freq in notas:
        t = np.linspace(0, duracion_nota, int(sample_rate * duracion_nota), False)
        onda = np.sin(2 * np.pi * freq * t)
        #envolvente: ataque rapido, decaimiento suave
        envolvente = np.exp(-t * 8) * (1 - np.exp(-t * 100))
        onda = (onda * envolvente * 32767 * 0.5).astype(np.int16)
        sonido_completo = np.concatenate([sonido_completo, onda])
    
    #se hace estereo porque pygame lo necesita por defecto
    stereo = np.column_stack((sonido_completo, sonido_completo))
    return pygame.sndarray.make_sound(stereo)

#renderiza texto con pygame.font y lo convierte a textura de OpenGL
def render_text_to_texture(text, font_size=72, color=(255, 255, 0)):
    font = pygame.font.SysFont('Arial', font_size, bold=True)
    text_surface = font.render(text, True, color)
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    w, h = text_surface.get_size()
    
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    
    return tex_id, w, h

#dibuja una textura de texto centrada en pantalla como overlay 2D
def draw_text_overlay(tex_id, w, h, alpha=1.0):
    #se cambia a proyeccion ortografica 2D para dibujar encima de la escena 3D
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, screen_width, 0, screen_height, -1, 1)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    #desactivamos depth test para que el texto se vea encima de todo
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glColor4f(1.0, 1.0, 1.0, alpha)
    
    #centramos el texto en pantalla
    x = (screen_width - w) / 2
    y = (screen_height - h) / 2
    
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(x, y)
    glTexCoord2f(1, 0); glVertex2f(x + w, y)
    glTexCoord2f(1, 1); glVertex2f(x + w, y + h)
    glTexCoord2f(0, 1); glVertex2f(x, y + h)
    glEnd()
    
    glDisable(GL_BLEND)
    glDisable(GL_TEXTURE_2D)
    glEnable(GL_DEPTH_TEST)
    
    #restauramos las matrices originales
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

pygame.init()

def Axis():
    glShadeModel(GL_FLAT)
    glLineWidth(3.0)
    #X axis in red
    glColor3f(1.0,0.0,0.0)
    glBegin(GL_LINES)
    glVertex3f(X_MIN,0.0,0.0)
    glVertex3f(X_MAX,0.0,0.0)
    glEnd()
    #Y axis in green
    glColor3f(0.0,1.0,0.0)
    glBegin(GL_LINES)
    glVertex3f(0.0,Y_MIN,0.0)
    glVertex3f(0.0,Y_MAX,0.0)
    glEnd()
    #Z axis in blue
    glColor3f(0.0,0.0,1.0)
    glBegin(GL_LINES)
    glVertex3f(0.0,0.0,Z_MIN)
    glVertex3f(0.0,0.0,Z_MAX)
    glEnd()
    glLineWidth(1.0)

def Texturas(filepath):
    textures.append(glGenTextures(1))
    id = len(textures) - 1
    glBindTexture(GL_TEXTURE_2D, textures[id])
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    image = pygame.image.load(filepath).convert()
    w, h = image.get_rect().size
    image_data = pygame.image.tostring(image,"RGBA")
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
    glGenerateMipmap(GL_TEXTURE_2D) 
    
def Init():
    screen = pygame.display.set_mode(
        (screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL: cubos")

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOVY, screen_width/screen_height, ZNEAR, ZFAR)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(EYE_X,EYE_Y,EYE_Z,CENTER_X,CENTER_Y,CENTER_Z,UP_X,UP_Y,UP_Z)
    glClearColor(0,0,0,0)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    #textures[0]: plano
    Texturas(file_1)
    #textures[1]: pacman
    Texturas(img_pacman)
    #textures[2]: fantasma1
    Texturas(img_ghost1)
    #textures[3]: fantasma2
    Texturas(img_ghost2)
    #textures[4]: fantasma3
    Texturas(img_ghost3)
    #textures[5]: fantasma4
    Texturas(img_ghost4)

    #se pasan las texturas a los objetos
    pc.loadTextures(textures,1)
    ghosts[0].loadTextures(textures,2)
    ghosts[1].loadTextures(textures,3)
    ghosts[2].loadTextures(textures,4)
    ghosts[3].loadTextures(textures,5)
    
def PlanoTexturizado():
    #Activate textures
    glColor3f(1.0,1.0,1.0)
    glEnable(GL_TEXTURE_2D)
    #front face
    glBindTexture(GL_TEXTURE_2D, textures[0])    
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(0, 0, 0)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(0, 0, DimBoard)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(DimBoard, 0, DimBoard)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(DimBoard, 0, 0)
    glEnd()              
    glDisable(GL_TEXTURE_2D)

#configura la camara con los parametros dados
def setup_camera(eye, center, up):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOVY, screen_width/screen_height, ZNEAR, ZFAR)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(eye[0], eye[1], eye[2],
              center[0], center[1], center[2],
              up[0], up[1], up[2])

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    PlanoTexturizado()
    pc.draw()
    for g in ghosts:
        g.draw()
        g.update2(pc.position, ghosts)

#dibuja la escena sin mover fantasmas (para la intro y el ready/go)
def display_intro():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    PlanoTexturizado()
    pc.draw()
    for g in ghosts:
        g.draw()

done = False
Init()

#sonido de inicio
sonido_inicio = generar_sonido_inicio()
sonido_inicio.play()

#texturas de texto para READY y GO
tex_ready, w_ready, h_ready = render_text_to_texture("LISTO?", 96, (255, 255, 0))
tex_go, w_go, h_go = render_text_to_texture("VAMOS!", 120, (0, 255, 100))

#estados del juego: 0=intro, 1=ready, 2=go, 3=jugando
game_state = 0
state_timer = time.time()

while not done:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True
    
    current_time = time.time()
    
    #fase de intro: animacion de camara
    if game_state == 0:
        elapsed = current_time - state_timer
        t = min(elapsed / INTRO_DURATION, 1.0)
        t_eased = ease_out_cubic(t)
        
        #se interpolan las posiciones de la camara entre inicio y fin
        current_eye = lerp_vec(INTRO_EYE_START, INTRO_EYE_END, t_eased)
        current_center = lerp_vec(INTRO_CENTER_START, INTRO_CENTER_END, t_eased)
        current_up = lerp_vec(INTRO_UP_START, INTRO_UP_END, t_eased)
        
        #se normaliza el vector UP para evitar distorsiones
        up_len = math.sqrt(sum(x*x for x in current_up))
        if up_len > 0:
            current_up = [x/up_len for x in current_up]
        
        setup_camera(current_eye, current_center, current_up)
        display_intro()
        
        if t >= 1.0:
            game_state = 1
            state_timer = current_time
    
    #ready
    elif game_state == 1:
        elapsed = current_time - state_timer
        display_intro()
        #parpadeo sutil con sin()
        alpha = 0.7 + 0.3 * math.sin(elapsed * 5)
        draw_text_overlay(tex_ready, w_ready, h_ready, alpha)
        
        if elapsed >= READY_DURATION:
            game_state = 2
            state_timer = current_time
    
    #go
    elif game_state == 2:
        elapsed = current_time - state_timer
        display_intro()
        #fade-out gradual
        alpha = max(0, 1.0 - elapsed / GO_DURATION)
        #efecto de escala que crece un poco
        scale = 1.0 + elapsed * 0.5
        draw_text_overlay(tex_go, int(w_go * scale), int(h_go * scale), alpha)
        
        if elapsed >= GO_DURATION:
            game_state = 3
    
    #fase de juego normal
    elif game_state == 3:
        keys = pygame.key.get_pressed()
        #Se verifica la direccion para el pacman    
        if keys[pygame.K_w]:
            #direccion 0
            pc.update(0)
        elif keys[pygame.K_d]:
            #direccion 1
            pc.update(1)
        elif keys[pygame.K_s]:
            #direccion 2
            pc.update(2)
        elif keys[pygame.K_a]:
            #direccion 1
            pc.update(3)
        else:
            pc.update(-1)

        display()

    pygame.display.flip()
    pygame.time.wait(10)

pygame.quit()
