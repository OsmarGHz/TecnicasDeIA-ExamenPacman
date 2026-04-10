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
import random

class Ghost:
    def __init__(self,mapa, mc, x_mc, y_mc, xini, yini, dir, tipo):
        #Matriz de control que almacena los IDs de las intersecciones
        self.MC = mc
        #Vectores que almacenan las coordenadas 
        self.XPxToMC = x_mc
        self.YPxToMC = y_mc
        #se resplanda el mapa en terminos de pixeles
        self.mapa = mapa
        #se inicializa la posicion del fantasma en terminos de pixeles
        self.position = []
        self.position.append(xini)
        self.position.append(1) #YPos
        self.position.append(yini)
        #se define el arreglo para la posicion en la matriz de control
        self.positionMC = []
        self.positionMC.append(self.XPxToMC[self.position[0] - 20]) #coord en x
        self.positionMC.append(self.YPxToMC[self.position[2] - 20]) #coord en y
        #se inicializa una direccion valida
        self.direction = dir
        #se almacena que tipo de fantasma sera:
        #0: fantasma aleatorio
        #1: fantasma con pathfinding
        self.tipo = tipo
        #arreglo para almacenar las opciones del fantasma
        self.options = [
            [1,2],
            [2,3],
            [0,1],
            [0,3],
            [1,2,3],
            [0,2,3],
            [0,1,3],
            [0,1,2],
            [0,1,2,3],
            [1],
            [3]
        ]
        self.option = []
        self.dir_inv = 0
        
    def loadTextures(self, texturas, id):
        self.texturas = texturas
        self.Id = id

    def drawFace(self, x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4):
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(x1, y1, z1)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(x2, y2, z2)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(x3, y3, z3)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(x4, y4, z4)
        glEnd()
   
    def sigue_adelante(self):
        #si el fantasma esta en un tunel, no es necesario calcular la siguiente posicion a traves del path
        #solo se sigue la direccion actual y se aumenta el contador que accede a la posicion del path actual
        if self.direction == 0: #up
            self.position[2] -= 1
        elif self.direction == 1: #right
            self.position[0] += 1
        elif self.direction == 2: #down
            self.position[2] += 1
        else: #left
            self.position[0] -= 1
        #Comentamos la parte donde se actualiza la variable de posicion sobre el path, porque no se usará una lista de path pregrabada, sino la IA en tiempo real
        # if self.tipo == 1: #fantasma inteligente
        #     self.path_n += 1

    def path_ia(self, pacmanXY):
        # 1. Obtenemos nuestras coordenadas actuales en la matriz
        fantasma_mc = [self.XPxToMC[self.position[0] - 20], self.YPxToMC[self.position[2] - 20]]
        
        # 2. Traducimos la posición real de Pacman a coordenadas de la matriz
        # Asumiendo que pacmanXY trae [X_pixeles, Z_pixeles]
        pacman_mc = [self.XPxToMC[pacmanXY[0] - 20], self.YPxToMC[pacmanXY[2] - 20]] 
        
        # 3. ¿Qué opciones reales tiene Pinky ahorita?
        opciones_validas = self.obtener_movimientos_validos(fantasma_mc[0], fantasma_mc[1], self.direction)
        
        mejor_valor = -float('inf')
        mejor_movimiento = self.direction # Por defecto sigue igual por si hay un error
        
        # 4. Probamos cada opción real usando Alfa-Beta para ver cuál es la mejor a futuro
        for mov in opciones_validas:
            # Simulamos ese primer paso
            sim_fantasma = list(fantasma_mc)
            if mov == 0: sim_fantasma[1] -= 1
            elif mov == 1: sim_fantasma[0] += 1
            elif mov == 2: sim_fantasma[1] += 1
            elif mov == 3: sim_fantasma[0] -= 1
            
            # Lanzamos la predicción a profundidad 3 (Suficiente inteligencia sin lag)
            valor = self.alfa_beta(3, sim_fantasma, pacman_mc, mov, -float('inf'), float('inf'), False) 
            
            if valor > mejor_valor:
                mejor_valor = valor
                mejor_movimiento = mov
                
        # 5. Ejecutamos la decisión maestra
        self.direction = mejor_movimiento
        
        # 6. Actualizamos el modelo 3D para que avance un paso en la nueva dirección
        if self.direction == 0: self.position[2] -= 1
        elif self.direction == 1: self.position[0] += 1
        elif self.direction == 2: self.position[2] += 1
        elif self.direction == 3: self.position[0] -= 1
        
    def interseccion_random(self):
        #se determina en que tipo de celda esta el fantasma
        self.positionMC[0] = self.XPxToMC[self.position[0] - 20]
        self.positionMC[1] = self.YPxToMC[self.position[2] - 20]
        celId = self.MC[self.positionMC[1]][self.positionMC[0]]
        #a partir de la celda actual se generan sus opciones posibles
        if celId == 0:
            self.option = [self.direction]
        elif celId == 10: #options = [1, 2]
            self.option = self.options[0]
        elif celId == 11: #options = [2, 3]
            self.option = self.options[1]
        elif celId == 12: #options = [0, 1]
            self.option = self.options[2]
        elif celId == 13: #options = [0, 3]
            self.option = self.options[3]
        elif celId == 21: #options = [1, 2, 3]
            self.option = self.options[4]
        elif celId == 22: #options = [0, 2, 3]
            self.option = self.options[5]
        elif celId == 23: #options = [0, 1, 3]
            self.option = self.options[6]
        elif celId == 24: #options = [0, 1, 2]
            self.option = self.options[7]
        elif celId == 25: #options = [0, 1, 2, 3]
            self.option = self.options[8]
        elif celId == 26: #options = [1]
            self.option = self.options[9]
        elif celId == 27: #options = [3]
            self.option = self.options[10]
        
        #se calcula la direccion inversa a la actual
        if self.direction == 0:
            self.dir_inv = 2
        elif self.direction == 1:
            self.dir_inv = 3
        elif self.direction == 2:
            self.dir_inv = 0
        else:
            self.dir_inv = 1

        opciones_validas = list(self.option)

        #se elimina la direccion invertida a la actual, evitando que el
        #fantasma regrese por el camion por donde llego (rebote)
        if (celId != 0) and (celId != 26) and (celId != 27):
            # Validamos que la dirección inversa sí esté en la lista antes de intentar borrarla
            if self.dir_inv in opciones_validas:
                opciones_validas.remove(self.dir_inv)
        
        # Elegimos aleatoriamente usando random.choice que es más limpio en Python
        self.direction = random.choice(opciones_validas)
        
        if self.direction == 0:
            self.position[2] -= 1
        elif self.direction == 1:
            self.position[0] += 1
        elif self.direction == 2:
            self.position[2] += 1
        elif self.direction == 3:
            self.position[0] -= 1


    #------------Esta es la Parte especial de Pinky-------------------

    def distancia_manhattan(self, nodoXY, pacmanXY):
        distancia = abs(nodoXY[0] - pacmanXY[0]) + abs(nodoXY[1] - pacmanXY[1])
        return -distancia   #Vamos a retornar en negativo, para que las distancias más cortas tengan mayor peso en el Minimax ya que Pinky es el jugador MAX

    def distancia_euclidiana(self, nodoXY, pacmanXY):
        distancia = math.sqrt( ((nodoXY[0] - pacmanXY[0]) ** 2) + ((nodoXY[1] - pacmanXY[1]) ** 2) )  
        return -distancia

    def obtener_movimientos_validos(self, pos_x_de_MC, pos_y_de_MC, dir_actual): 
        try:
            celId = self.MC[pos_y_de_MC][pos_x_de_MC]   # Intentamos leer la celda en la Matriz de Control simulada con coordenadass simuladas
        except IndexError:
            return [] # Si la simulación se sale del mapa, es un callejón sin salida

        opciones_celda = []
        if celId == 0: opciones_celda = [dir_actual]
        elif celId == 10: opciones_celda = self.options[0]
        elif celId == 11: opciones_celda = self.options[1]
        elif celId == 12: opciones_celda = self.options[2]
        elif celId == 13: opciones_celda = self.options[3]
        elif celId == 21: opciones_celda = self.options[4]
        elif celId == 22: opciones_celda = self.options[5]
        elif celId == 23: opciones_celda = self.options[6]
        elif celId == 24: opciones_celda = self.options[7]
        elif celId == 25: opciones_celda = self.options[8]
        elif celId == 26: opciones_celda = self.options[9]
        elif celId == 27: opciones_celda = self.options[10]
        else: return []

        opciones_validas = list(opciones_celda)
        
        # calculamos la inversa simulada
        if dir_actual == 0: dir_inv = 2
        elif dir_actual == 1: dir_inv = 3
        elif dir_actual == 2: dir_inv = 0
        else: dir_inv = 1

        # aqui evitamos el regreso en la simulación
        if (celId != 0) and (celId != 26) and (celId != 27):
            if dir_inv in opciones_validas:
                opciones_validas.remove(dir_inv)
                
        return opciones_validas

    def alfa_beta(self, profundidad, nodo_fantasma, nodo_pacman, dir_fantasma, alpha, beta, maximizando):
        # CONDICIÓN DE PARADA: Si llegamos al límite de predicción o atraparon a Pacman
        if profundidad == 0 or (nodo_fantasma == nodo_pacman):
            # Aquí es donde usamos la heurística que programamos antes
            return self.distancia_manhattan(nodo_fantasma, nodo_pacman)

        if maximizando: # TURNO DE PINKY (Busca el valor más alto / más cerca)
            max_eval = -float('inf')
            movimientos = self.obtener_movimientos_validos(nodo_fantasma[0], nodo_fantasma[1], dir_fantasma)
            
            if not movimientos: return self.distancia_manhattan(nodo_fantasma, nodo_pacman)

            for mov in movimientos:
                # Imaginamos a Pinky dando un paso en esa dirección
                nuevo_fantasma = list(nodo_fantasma)
                if mov == 0: nuevo_fantasma[1] -= 1   # Arriba
                elif mov == 1: nuevo_fantasma[0] += 1 # Derecha
                elif mov == 2: nuevo_fantasma[1] += 1 # Abajo
                elif mov == 3: nuevo_fantasma[0] -= 1 # Izquierda
                
                # Llamada recursiva (Ahora imaginamos qué haría Pacman)
                evaluacion = self.alfa_beta(profundidad - 1, nuevo_fantasma, nodo_pacman, mov, alpha, beta, False)
                
                max_eval = max(max_eval, evaluacion)
                alpha = max(alpha, evaluacion)
                if beta <= alpha:
                    break # ¡ZAS! PODA ALFA-BETA. Rama descartada.
            return max_eval

        else: # TURNO DE PACMAN (Busca el valor más bajo / escapar)
            min_eval = float('inf')
            # Simulamos que Pacman evalúa sus 4 lados para intentar huir
            movimientos_pacman = [0, 1, 2, 3] 
            
            for mov in movimientos_pacman:
                nuevo_pacman = list(nodo_pacman)
                if mov == 0: nuevo_pacman[1] -= 1
                elif mov == 1: nuevo_pacman[0] += 1
                elif mov == 2: nuevo_pacman[1] += 1
                elif mov == 3: nuevo_pacman[0] -= 1
                
                # Llamada recursiva (Le toca a Pinky de nuevo)
                evaluacion = self.alfa_beta(profundidad - 1, nodo_fantasma, nuevo_pacman, dir_fantasma, alpha, beta, True)
                
                min_eval = min(min_eval, evaluacion)
                beta = min(beta, evaluacion)
                if beta <= alpha:
                    break # ¡ZAS! PODA ALFA-BETA. Rama descartada.
            return min_eval        

    #------------Este es el Fin de la Parte especial de Pinky-------------------
    
    def update2(self, pacmanXY):
        dist_x = abs(self.position[0] - pacmanXY[0])
        dist_z = abs(self.position[2] - pacmanXY[2])
        
        if dist_x < 20 and dist_z < 20:
            # Usamos hasattr para asegurar que el letrero se imprima una sola vez por choque entre pacman y fantasmita
            if not hasattr(self, 'pacman_atrapado'):

                nombres_fantasmas = {
                    0: "Blinky (Rojo)",
                    1: "Pinky (Rosa)",
                    2: "Inky (Azul)",
                    3: "Clyde (Naranja)"
                }
                
                nombre_fantasma = nombres_fantasmas.get(getattr(self, 'Id', -1), "Un fantasma")
                comportamiento = "[IA Alfa-Beta]" if self.tipo == 1 else "[Aleatorio]"
                
                print(f"\t\t¡Pacman encontrado por {nombre_fantasma} {comportamiento}!")
                self.pacman_atrapado = True
            
            #congelar al fantasma
            return
            
        # 2: Logica de movimiento
        if ((self.YPxToMC[self.position[2] - 20] != -1) and 
            (self.XPxToMC[self.position[0] - 20] != -1)):
            if self.tipo == 1: 
                self.path_ia(pacmanXY)
            else:
                self.interseccion_random()
        else: # si no se encuentra en una interseccion
            self.sigue_adelante()
        
    def draw(self):
        glPushMatrix()
        glColor3f(1.0, 1.0, 1.0)
        glTranslatef(self.position[0], self.position[1], self.position[2])
        glScaled(10,1,10)
        #Activate textures
        glEnable(GL_TEXTURE_2D)
        #front face
        glBindTexture(GL_TEXTURE_2D, self.texturas[self.Id])
        self.drawFace(-1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0)    
        glDisable(GL_TEXTURE_2D)  
        glPopMatrix()        