#!/usr/bin/python
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
    program['a_position'] = np.c_[
        np.linspace(-1.0, +1.0, 1000).astype(np.float32),
        np.random.uniform(-0.5, +0.5, 1000).astype(np.float32)]
    @c.connect
    def on_resize(event):
        gloo.set_viewport(0, 0, *event.size)
    @c.connect
    def on_draw(event):
        gloo.clear((1,1,1,1))
        program.draw('points')
    c.show()
    app.run();


if __name__ == "__main__":
   main(sys.argv[1:])
