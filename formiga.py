#!/usr/bin/python3
from random import *
import numpy as np
import sys, getopt
import vispy
from vispy import app
from vispy import gloo


class Map:
    def __init__(self,mapSizeX,mapSizeY,numberObjects,numberAnts):
        self.mapSizeX = mapSizeX
        self.mapSizeY = mapSizeY
        self.numberObjects = numberObjects
        self.numberAnts = numberAnts

        if(numberObjects>(mapSizeX*mapSizeY)):
            raise ValueError("Numero de Objetos e maior que o numero de celulas do mapa")

        self.map = np.zeros((mapSizeX, mapSizeY))
        self.DistributeObjects()
        self.gl_mapPositions = np.zeros((6*mapSizeX, 6*mapSizeY, 2))
        tempx = np.linspace(-1.0, +1.0, mapSizeX).astype(np.float32)
        tempy = np.linspace(-1.0, +1.0, mapSizeY).astype(np.float32)
        self.gl_Xsize = 2.0/mapSizeX
        self.gl_Ysize = 2.0/mapSizeY
        for x in range(mapSizeX):
            for y in range(mapSizeY):
                self.gl_mapPositions[6*x][6*y][0] = tempx[x]
                self.gl_mapPositions[6*x][6*y][1] = tempy[y]
                self.gl_mapPositions[6*x+1][6*y+1][0] = tempx[x]+self.gl_Xsize
                self.gl_mapPositions[6*x+1][6*y+1][1] = tempy[y]
                self.gl_mapPositions[6*x+2][6*y+2][0] = tempx[x]
                self.gl_mapPositions[6*x+2][6*y+2][1] = tempy[y]+self.gl_Ysize
                self.gl_mapPositions[6*x+3][6*y+3][0] = tempx[x]+self.gl_Xsize
                self.gl_mapPositions[6*x+3][6*y+3][1] = tempy[y]
                self.gl_mapPositions[6*x+4][6*y+4][0] = tempx[x]
                self.gl_mapPositions[6*x+4][6*y+4][1] = tempy[y]+self.gl_Ysize
                self.gl_mapPositions[6*x+5][6*y+5][0] = tempx[x]+self.gl_Xsize
                self.gl_mapPositions[6*x+5][6*y+5][1] = tempy[y]+self.gl_Ysize


        print(self.gl_mapPositions)
        #self.gl_mapPositions = np.c_[
        #    np.linspace(-1.0, +1.0, 100).astype(np.float32),
        #    np.linspace(-1.0, +1.0, 100).astype(np.float32)]
        #print(self.gl_mapPositions)

    def DistributeObjects(self):
        self.map = self.map.reshape(self.mapSizeX*self.mapSizeY)
        for i in range(self.numberObjects):
            self.map[i] = 1
        np.random.shuffle(self.map)
        self.map = self.map.reshape((self.mapSizeX, self.mapSizeY))

    def PrintMap(self):
        for x in range(self.mapSizeX):
            for y in range(self.mapSizeY):
                print(int(self.map[x][y]), end="")
            print('\n', end=""),


class Ant:
    def __init__(self,fieldOfView):
        self.fixieldOfView = fieldOfView
        self.viewCells = (fieldOfView+2)*(fieldOfView+2)-1
    def ProbDrop(self, itemsAround):
        return float(itemsAround)/self.viewCells
    def ProbCatch(self,itemsAround):
        return 1-self.ProbDrop(itemsAround)



vertex = """
attribute vec2 a_position;
void main (void)
{
    gl_Position = vec4(a_position, 0.0, 1.0);
}
"""

fragment = """
void main()
{
    gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
}
"""

def main(argv):
    mapSizeX = 20
    mapSizeY = 20
    numberObjects = 100
    numberAnts = 10
    helpString = 'help place holder'
    try:
        opts, args = getopt.getopt(argv,"h",["nAnts=","mapX=","mapY=","nObj="])
    except getopt.GetoptError:
        print(helpString)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(helpString)
            sys.exit()
        elif opt in ("--nAnts"):
            numberAnts = int(arg)
        elif opt in ("--mapX"):
            mapSizeX = int(arg)
        elif opt in ("--mapY"):
            mapSizeY = int(arg)
        elif opt in ("--nObj"):
            numberObjects = int(arg)
    #ini
    MyAnt = Ant(1)

    GlobalMap = Map(mapSizeX,mapSizeY,numberObjects,numberAnts)
    GlobalMap.PrintMap()

    c = app.Canvas(keys='interactive')
    program = gloo.Program(vertex, fragment)
    program['a_position'] = GlobalMap.gl_mapPositions.astype(np.float32)
    @c.connect
    def on_resize(event):
        gloo.set_viewport(0, 0, *event.size)
    @c.connect
    def on_draw(event):
        gloo.clear((1,1,1,1))
        program.draw('lines')
    c.show()
    app.run();
    print('oi')

if __name__ == "__main__":
   main(sys.argv[1:])
