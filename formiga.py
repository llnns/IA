#!/usr/bin/python3
from random import *
import numpy as np
import sys, getopt
import vispy
from vispy import app
from vispy import gloo
import _thread


class Map:
    def __init__(self,mapSizeX,mapSizeY,numberObjects,numberAnts,fieldOfView,maxIteration):
        self.mapSizeX = mapSizeX
        self.mapSizeY = mapSizeY
        self.numberObjects = numberObjects
        self.numberAnts = numberAnts
        self.arrayAnts = []
        self.fieldOfView = fieldOfView
        self.maxIteration = maxIteration
        if(numberObjects>(mapSizeX*mapSizeY)):
            raise ValueError("Numero de Objetos e maior que o numero de celulas do mapa")

        self.map = np.zeros((mapSizeX, mapSizeY))
        self.drawMap = np.zeros((mapSizeX, mapSizeY))
        self.DistributeObjects()
        self.running = True
        self.gl_mapPositions = np.zeros((6*mapSizeX*mapSizeY, 2))
        tempx = np.linspace(-0.9, +0.9, mapSizeX+1).astype(np.float32)
        tempy = np.linspace(+0.9, -0.9, mapSizeY+1).astype(np.float32)
        self.gl_Xsize = 1.8/mapSizeX
        self.gl_Ysize = 1.8/mapSizeY
        for x in range(mapSizeX):
            for y in range(mapSizeY):
                self.gl_mapPositions[6*mapSizeY*y+6*x][0] = tempx[x]
                self.gl_mapPositions[6*mapSizeY*y+6*x][1] = tempy[y]
                self.gl_mapPositions[6*mapSizeY*y+6*x+1][0] = tempx[x]+self.gl_Xsize
                self.gl_mapPositions[6*mapSizeY*y+6*x+1][1] = tempy[y]
                self.gl_mapPositions[6*mapSizeY*y+6*x+2][0] = tempx[x]
                self.gl_mapPositions[6*mapSizeY*y+6*x+2][1] = tempy[y]-self.gl_Ysize
                self.gl_mapPositions[6*mapSizeY*y+6*x+3][0] = tempx[x]+self.gl_Xsize
                self.gl_mapPositions[6*mapSizeY*y+6*x+3][1] = tempy[y]
                self.gl_mapPositions[6*mapSizeY*y+6*x+4][0] = tempx[x]
                self.gl_mapPositions[6*mapSizeY*y+6*x+4][1] = tempy[y]-self.gl_Ysize
                self.gl_mapPositions[6*mapSizeY*y+6*x+5][0] = tempx[x]+self.gl_Xsize
                self.gl_mapPositions[6*mapSizeY*y+6*x+5][1] = tempy[y]-self.gl_Ysize

        for i in range(self.numberAnts):
            self.arrayAnts.append(Ant(self,randint(0,mapSizeX-1),randint(0,mapSizeY-1)))

        #print(self.gl_mapPositions)
        #self.gl_mapPositions = np.c_[
        #    np.linspace(-1.0, +1.0, 100).astype(np.float32),
        #    np.linspace(-1.0, +1.0, 100).astype(np.float32)]
        #print(self.gl_mapPositions)
        self.UpdateAnts()

    def DistributeObjects(self):
        self.map = self.map.reshape(self.mapSizeX*self.mapSizeY)
        for i in range(self.numberObjects):
            self.map[i] = 1
        np.random.shuffle(self.map)
        self.map = self.map.reshape((self.mapSizeX, self.mapSizeY))
    def RandomObjects(self):
        self.map = self.map.reshape(self.mapSizeX*self.mapSizeY)
        np.random.shuffle(self.map)
        self.map = self.map.reshape((self.mapSizeX, self.mapSizeY))

    def PrintMap(self):
        for x in range(self.mapSizeX):
            for y in range(self.mapSizeY):
                print(int(self.map[x][y]), end="")
            print('\n', end=""),

    def UpdateAnts(self):
        for i in range(self.numberAnts):
            self.arrayAnts[i].Mov()

    def ThreadCallUpdate(self):
        while(self.running and (self.maxIteration==-1 or (self.maxIteration)>0)):
            self.UpdateAnts()
            self.maxIteration-=1

    def UpdateDrawMap(self):
        self.drawMap = np.copy(self.map)
        for i in range(self.numberAnts):
            if(self.arrayAnts[i].carring):
                self.drawMap[self.arrayAnts[i].x][self.arrayAnts[i].y] = 3
            else:
                self.drawMap[self.arrayAnts[i].x][self.arrayAnts[i].y] = 2


class Ant:
    def __init__(self,Map,posX,posY):
        self.fieldOfView = Map.fieldOfView
        self.viewCells = (self.fieldOfView+2)*(self.fieldOfView+2)-1
        self.x = posX
        self.y = posY
        self.Map = Map
        self.carring = False
        self.itemsAround = 0

    def ProbDrop(self):
        return float(self.itemsAround)/self.viewCells

    def ProbCatch(self):
        return 1-self.ProbDrop()

    def Mov(self):
        probMovX = int(gauss(0,2))
        probMovY = int(gauss(0,2))
        if((self.x+probMovX)>=0 and (self.x+probMovX)<self.Map.mapSizeX):
            self.x+=probMovX
        if((self.y+probMovY)>=0 and (self.y+probMovY)<self.Map.mapSizeY):
            self.y+=probMovY
        self.Act()

    def UpdateAround(self):
        self.itemsAround = 0
        for i in range(-self.fieldOfView,self.fieldOfView+1):
            for y in range(-self.fieldOfView,self.fieldOfView+1):
                if((i==0)and(y==0)):
                    continue
                if((self.x+i)>=0 and (self.x+i)<self.Map.mapSizeX and (self.y+y)>=0 and (self.y+y)<self.Map.mapSizeY):
                    self.itemsAround+=self.Map.map[self.x+i][self.y+y]

    def Act(self):
        self.UpdateAround()
        if(self.carring):
            if(self.Map.map[self.x][self.y]==0):
                if(uniform(0.0,1.0)<self.ProbDrop()):
                    self.carring = False
                    self.Map.map[self.x][self.y]=1
        else:
            if(self.Map.map[self.x][self.y]==1):
                if(uniform(0.0,1.0)<self.ProbCatch()):
                    self.carring = True
                    self.Map.map[self.x][self.y]=0

vertex = """
attribute vec2 a_position;
attribute float a_cor;
varying vec4 f_cor;
void main (void)
{
    if(a_cor==1.0){
        f_cor=vec4(0.0,0.0,0.0,1.0);
    }else if(a_cor==0.0){
        f_cor=vec4(1.0,1.0,1.0,1.0);
    }else if(a_cor==3.0){
        f_cor=vec4(0.0,1.0,0.0,1.0);
    }else{
        f_cor=vec4(1.0,0.0,0.0,1.0);
    }
    gl_Position = vec4(a_position, 0.0, 1.0);
}
"""

fragment = """
varying vec4 f_cor;
void main()
{
    gl_FragColor = f_cor;
}
"""

def main(argv):
    mapSizeX = 20
    mapSizeY = 20
    numberObjects = 100
    numberAnts = 10
    fieldOfView = 1
    maxIteration = 100000
    helpString = 'help place holder'
    try:
        opts, args = getopt.getopt(argv,"h",["nAnts=","mapX=","mapY=","nObj=","View=","maIt="])
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
        elif opt in ("--View"):
            fieldOfView = int(arg)
        elif opt in ("--maIt"):
            maxIteration = int(arg)
    #INI
    GlobalMap = Map(mapSizeX,mapSizeY,numberObjects,numberAnts,fieldOfView,maxIteration)
    #GlobalMap.PrintMap()

    #INTERFACE
    c = app.Canvas(keys='interactive')
    c._timer = app.Timer('auto', connect=c.update, start=True)

    program = gloo.Program(vertex, fragment)
    program['a_position'] = GlobalMap.gl_mapPositions.astype(np.float32)
    program['a_cor'] = np.repeat(GlobalMap.map,6).astype(np.float32)
    c.program = program
    c.GlobalMap = GlobalMap

    @c.connect
    def on_resize(event):
        gloo.set_viewport(0, 0, *event.size)

    @c.connect
    def on_draw(event):
        #print(c.GlobalMap.map)
        gloo.clear((1,1,1,1))

        c.GlobalMap.UpdateDrawMap()
        c.program['a_cor'] = np.repeat(c.GlobalMap.drawMap,6).astype(np.float32)
        program.draw('triangles')
    _thread.start_new_thread( c.GlobalMap.ThreadCallUpdate, () )
    c.show()
    app.run();
    GlobalMap.running = False
    print('Encerrado')

if __name__ == "__main__":
   main(sys.argv[1:])
