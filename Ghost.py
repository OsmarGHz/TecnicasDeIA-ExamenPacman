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

    def path_ia(self, pacmanXY, lista_fantasmas):
        #posicion del fantasma en la matriz de control
        fantasma_mc = [self.XPxToMC[self.position[0] - 20], self.YPxToMC[self.position[2] - 20]]
        #posicion del pacman en la matriz de control (pacmanXY trae [X_pixeles, Z_pixeles])
        pacman_mc = [self.XPxToMC[pacmanXY[0] - 20], self.YPxToMC[pacmanXY[2] - 20]] 

        aliado_mc = None
        if self.tipo == 2: # Solo Inky y Clyde se buscan entre ellos
            for f in lista_fantasmas:
                # Buscamos al otro fantasma que también sea tipo 2, y que no sea pacman
                if f.tipo == 2 and f != self:
                    aliado_mc = [self.XPxToMC[f.position[0] - 20], self.YPxToMC[f.position[2] - 20]]
                    break
        
        #se obtienen las opciones de movimiento validas desde la posicion actual
        opciones_validas = self.obtener_movimientos_validos(fantasma_mc[0], fantasma_mc[1], self.direction)
        
        mejor_valor = -float('inf')
        mejor_movimiento = self.direction #por defecto sigue igual
        
        #se evalua cada opcion con alfa-beta para elegir la mejor
        for mov in opciones_validas:
            #simulamos el primer paso en esa direccion
            sim_fantasma = list(fantasma_mc)
            if mov == 0: sim_fantasma[1] -= 1
            elif mov == 1: sim_fantasma[0] += 1
            elif mov == 2: sim_fantasma[1] += 1
            elif mov == 3: sim_fantasma[0] -= 1
            
            #profundidad 3: suficiente para tomar "buenas" decisiones sin afectar rendimiento
            valor = self.alfa_beta(3, sim_fantasma, pacman_mc, mov, -float('inf'), float('inf'), False, aliado_mc) 
            
            if valor > mejor_valor:
                mejor_valor = valor
                mejor_movimiento = mov
        
        #se aplica la mejor direccion encontrada
        self.direction = mejor_movimiento
        
        #se avanza un paso en la nueva direccion
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

    def heuristica_combinada(self, nodoXY, pacmanXY):
        manhattan = abs(nodoXY[0] - pacmanXY[0]) + abs(nodoXY[1] - pacmanXY[1])
        euclidiana = math.sqrt((nodoXY[0] - pacmanXY[0])**2 + (nodoXY[1] - pacmanXY[1])**2)
        # Manhattan domina (0.75) porque el laberinto es cuadriculado y el movimiento diagonal es imposible.
        # Euclidiana aporta (0.25) como desempate geométrico cuando dos rutas tienen igual distancia Manhattan.
        return -(0.75 * manhattan + 0.25 * euclidiana)

    def heuristica_colaborativa(self, nodoXY, pacmanXY, aliadoXY):
        #distancia al pacman
        dist_pacman = abs(nodoXY[0] - pacmanXY[0]) + abs(nodoXY[1] - pacmanXY[1])
        
        if aliadoXY:
            dist_aliado = abs(nodoXY[0] - aliadoXY[0]) + abs(nodoXY[1] - aliadoXY[1])
        else:
            dist_aliado = 10 #sin aliado, se comporta como pinky

        bonus_separacion = 0
        
        #si estan a menos de 5 celdas se estorban, hay que separarlos
        if dist_aliado < 5:
            mi_id = getattr(self, 'Id', 2)
            
            if mi_id % 2 == 0:
                dist_eje = abs(nodoXY[0] - aliadoXY[0]) #clyde se separa en horizontal
            else:
                dist_eje = abs(nodoXY[1] - aliadoXY[1]) #inky se separa en vertical
                
            bonus_separacion = dist_eje * 4 #peso alto para que la separacion tenga prioridad temporal

        #se acerca a pacman, pero si necesita separarse del aliado suma el bonus
        return -dist_pacman + bonus_separacion

    def obtener_movimientos_validos(self, pos_x_de_MC, pos_y_de_MC, dir_actual): 
        #se lee la celda de la matriz de control, si se sale del rango retorna vacio
        try:
            celId = self.MC[pos_y_de_MC][pos_x_de_MC]
        except IndexError:
            return []

        #a partir de la celda se generan las opciones posibles (igual que en interseccion_random)
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
        
        #se calcula la direccion inversa para evitar rebote
        if dir_actual == 0: dir_inv = 2
        elif dir_actual == 1: dir_inv = 3
        elif dir_actual == 2: dir_inv = 0
        else: dir_inv = 1

        #se elimina la direccion inversa para que no regrese por donde venia
        if (celId != 0) and (celId != 26) and (celId != 27):
            if dir_inv in opciones_validas:
                opciones_validas.remove(dir_inv)
                
        return opciones_validas

    def alfa_beta(self, profundidad, nodo_fantasma, nodo_pacman, dir_fantasma, alpha, beta, maximizando, aliado_mc=None, lista_tabu=None, profundidad_reposo=0):
        #se inicializa la lista tabu si es la primera llamada
        if lista_tabu is None:
            lista_tabu = []
            
        #se agrega la posicion actual a la lista de visitados
        nueva_lista_tabu = lista_tabu + [nodo_fantasma]

        #distancia actual entre fantasma y pacman
        dist_actual = abs(nodo_fantasma[0] - nodo_pacman[0]) + abs(nodo_fantasma[1] - nodo_pacman[1])

        #busqueda en reposo: si estan a 2 celdas o menos, se extiende la profundidad para no cortar en mal momento
        if profundidad == 0 and dist_actual <= 2 and profundidad_reposo < 2:
            profundidad += 1
            profundidad_reposo += 1

        #caso base: se llego al limite de profundidad o el fantasma alcanzo a pacman
        if profundidad == 0 or (nodo_fantasma == nodo_pacman):
            if self.tipo == 2 and aliado_mc:
                return self.heuristica_colaborativa(nodo_fantasma, nodo_pacman, aliado_mc)
            else:
                return self.heuristica_combinada(nodo_fantasma, nodo_pacman)

        if maximizando: #turno del fantasma, busca acercarse
            max_eval = -float('inf')
            movimientos = self.obtener_movimientos_validos(nodo_fantasma[0], nodo_fantasma[1], dir_fantasma)
            
            if not movimientos: return self.heuristica_combinada(nodo_fantasma, nodo_pacman)

            for mov in movimientos:
                #se simula un paso del fantasma en esa direccion
                nuevo_fantasma = list(nodo_fantasma)
                if mov == 0: nuevo_fantasma[1] -= 1   #arriba
                elif mov == 1: nuevo_fantasma[0] += 1 #derecha
                elif mov == 2: nuevo_fantasma[1] += 1 #abajo
                elif mov == 3: nuevo_fantasma[0] -= 1 #izquierda

                #busqueda tabu: si ya visitamos esa celda en esta simulacion, la saltamos
                if nuevo_fantasma in nueva_lista_tabu:
                    continue

                #llamada recursiva, ahora le toca a pacman
                evaluacion = self.alfa_beta(profundidad - 1, nuevo_fantasma, nodo_pacman, mov, alpha, beta, False, aliado_mc, nueva_lista_tabu, profundidad_reposo)
                
                max_eval = max(max_eval, evaluacion)
                alpha = max(alpha, evaluacion)
                if beta <= alpha:
                    break #poda alfa-beta
            
            #si todos los movimientos eran tabu, se retorna la heuristica actual
            if max_eval == -float('inf'):
                return self.heuristica_combinada(nodo_fantasma, nodo_pacman)
                
            return max_eval

        else: #turno de pacman, busca escapar (valor mas bajo)
            min_eval = float('inf')
            #se simulan las 4 direcciones posibles de pacman
            movimientos_pacman = [0, 1, 2, 3] 
            
            for mov in movimientos_pacman:
                nuevo_pacman = list(nodo_pacman)
                if mov == 0: nuevo_pacman[1] -= 1
                elif mov == 1: nuevo_pacman[0] += 1
                elif mov == 2: nuevo_pacman[1] += 1
                elif mov == 3: nuevo_pacman[0] -= 1
                
                #llamada recursiva, le toca al fantasma de nuevo (pacman no usa la lista tabu)
                evaluacion = self.alfa_beta(profundidad - 1, nodo_fantasma, nuevo_pacman, dir_fantasma, alpha, beta, True, aliado_mc, nueva_lista_tabu, profundidad_reposo)
                
                min_eval = min(min_eval, evaluacion)
                beta = min(beta, evaluacion)
                if beta <= alpha:
                    break #poda alfa-beta
            return min_eval        
    
    def update2(self, pacmanXY, lista_fantasmas=[]):
        if not hasattr(self, 'veces_encontrado'):
            self.veces_encontrado = 0
            self.tocando_pacman = False

        dist_x = abs(self.position[0] - pacmanXY[0])
        dist_z = abs(self.position[2] - pacmanXY[2])
        
        if dist_x < 20 and dist_z < 20:
            if not self.tocando_pacman:
                self.veces_encontrado += 1
                self.tocando_pacman = True #Esto se activa hasta que el pacman se va de los fantasmas
                
                nombres_fantasmas = {
                    5: "Blinky (Rojo)", #ghosts[3].loadTextures(textures,5)
                    4: "Pinky (Rosa)",  #ghosts[2].loadTextures(textures,4)
                    3: "Inky (Azul)",   #ghosts[1].loadTextures(textures,3)
                    2: "Clyde (Naranja)" #ghosts[0].loadTextures(textures,2)
                }
                
                nombre_fantasma = nombres_fantasmas.get(getattr(self, 'Id', -1), "Fantasma no reconocido")
                if self.tipo == 2: comportamiento = "[IA Colaborativa]"
                elif self.tipo == 1: comportamiento = "[IA Alfa-Beta]"
                else: comportamiento = "[Aleatorio]"
                
                print(f"\t\tPacman tocado por {nombre_fantasma} {comportamiento} ({self.veces_encontrado})")
                
            return  #Al llegar aqui, el fantasma se queda congelado, mientras el pacman este tocandolo
            
        else:
            self.tocando_pacman = False

        if ((self.YPxToMC[self.position[2] - 20] != -1) and 
            (self.XPxToMC[self.position[0] - 20] != -1)):
            if self.tipo == 1 or self.tipo == 2:
                self.path_ia(pacmanXY, lista_fantasmas)
            else:
                self.interseccion_random()
        else:
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