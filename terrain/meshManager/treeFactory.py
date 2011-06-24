import math, random

from panda3d.core import Vec3, Quat, GeomVertexFormat, NodePath

import meshManager
import gridFactory


class TreeFactory(gridFactory.GridFactory):
    def __init__(self,barkTexture=None,leafTexture=None,scalar=2.0,gridSize=5.0):
        self.barkTexture=barkTexture
        self.leafTexture=leafTexture
        gridFactory.GridFactory.__init__(self,scalar,gridSize)
        
        self.leafDataIndex={}
        self.trunkDataIndex={}
        
        self.minLOD=meshManager.LOD('inf',2000)
        self.lowLOD=meshManager.LOD(2000,1000)
        self.midLOD=meshManager.LOD(1000,500)
        self.highLOD=meshManager.LOD(500,0)
        
    def getLODs(self):
        return [self.minLOD,self.lowLOD,self.midLOD,self.highLOD]
        
    def regesterGeomRequirements(self,LOD,collection):
        
        n=NodePath('tmp')
        
        if self.barkTexture is not None:
            n.setTexture(self.barkTexture)
            n.setShaderInput('diffTex',self.barkTexture)
        
            trunkRequirements=meshManager.GeomRequirements(
                geomVertexFormat=GeomVertexFormat.getV3n3t2(),
                renderState=n.getState()
                )
        else:
            trunkRequirements=meshManager.GeomRequirements(
                geomVertexFormat=GeomVertexFormat.getV3n3c4(),
                renderState=n.getState()
                )
        
        
        n=NodePath('tmp')
        
        if self.leafTexture is not None:
            n.setTexture(self.leafTexture)
            n.setShaderInput('diffTex',self.leafTexture)
            
            leafRequirements=meshManager.GeomRequirements(
                geomVertexFormat=GeomVertexFormat.getV3n3t2(),
                renderState=n.getState()
                )
        
        else:
            leafRequirements=meshManager.GeomRequirements(
                geomVertexFormat=GeomVertexFormat.getV3n3c4(),
                renderState=n.getState()
                )
        
        self.trunkDataIndex[LOD]=collection.add(trunkRequirements)
        self.leafDataIndex[LOD]=collection.add(leafRequirements)
    
    def drawItem(self,LOD,x,y,drawResourcesFactory,tile,tileCenter,seed=True):
        if seed: random.seed((x,y))
        exists=random.random()
        if exists<.9: return
        
        quat=Quat()
        quat.setHpr((random.random()*360,0,0))
        
        heightOffset=-0.4 # make sure whole bottom of tree is in ground
        pos=Vec3(x,y,tile.height(x,y)+heightOffset)-tileCenter
        
        self.drawTree(LOD,(pos, quat, 0, 0, 0),drawResourcesFactory)
               
    def drawTree(self,LOD,base,drawResourcesFactory):
        age=random.random()**3.5
        
        
        to = 12*age
        
        
        if to<3: return
        
        leafScaler=age**.5
        leafSize=10.0*self.scalar*leafScaler
        skipLeaves=0;
        
        if LOD==self.minLOD:
            numVertices=2
            cutoffRadius=.7
            skipLeaves=(1-leafScaler)*2
            #skipLeaves=.5
        elif LOD==self.lowLOD:
            numVertices=3
            cutoffRadius=.5
            #skipLeaves=.4
        elif LOD==self.midLOD:
            numVertices=4
            cutoffRadius=.1
        else:
            numVertices=6
            cutoffRadius=-1
        
        doLeaves=True
        
        
        
        
        
        dotCount=1#int((2/age))
        
        leafResources=drawResourcesFactory.getDrawResources(self.leafDataIndex[LOD])
        leafTri=leafResources.getGeomTriangles()
        trunkResources=drawResourcesFactory.getDrawResources(self.trunkDataIndex[LOD])
        lines = trunkResources.getGeomTristrips()
        vertWriter = trunkResources.getWriter("vertex")
        normalWriter = trunkResources.getWriter("normal")
        if self.barkTexture:
            texWriter = trunkResources.getWriter("texcoord")
        else:
            colorWriter = trunkResources.getWriter("color")
        
        
        leafVertexWriter=leafResources.getWriter("vertex")
        leafNormalWriter=leafResources.getWriter("normal")
        
        if self.leafTexture:
            leafTexcoordWriter = leafResources.getWriter("texcoord")
        else:
            leafColorWriter = leafResources.getWriter("color")
        
        
        maxbend=40+random.random()*20
        
        forks=int(to/2-1)
        lengthList=[]
        numCopiesList=[]
        radiusList=[]
        currR=age*1.0*(random.random()*2+1)
        forkCount=0
        for i in xrange(forks+1):
            currR*=1/math.sqrt(2)
            endR=currR*.9*.9
            if i==forks:
                endR=0
                forkCount=0
            if i<2:
                lengthList.extend([2.0,2.0,2.0])
                numCopiesList.extend([forkCount,0,0])
                radiusList.extend([currR,currR*.9,endR])
            else:
                lengthList.extend([6.0])
                numCopiesList.extend([forkCount])
                radiusList.extend([endR])
            forkCount=2+(i%2)
                
        stack = [base]
        
        
        
        #cache some info needed for placeing the vertexes
        angleData=[]
        if self.barkTexture:
            vNum=numVertices+1
        else:
            vNum=numVertices
        
        for i in xrange(vNum):  #doubles the last vertex to fix UV seam
            angle=-2 * i * math.pi / numVertices
            angleData.append((math.cos(angle),math.sin(angle),1.0*i / numVertices))
        
        bottom=True
        
        while stack: 
            pos, quat, depth, previousRow, sCoord = stack.pop() 
            length = lengthList[depth]
            radius=radiusList[depth]
            
            startRow = vertWriter.getWriteRow()
            perp1 = quat.getRight() 
            perp2 = quat.getForward() 
            
            if radius>cutoffRadius:
            
                
                
                sCoord += length/4.0
                
                #this draws the body of the tree. This draws a ring of vertices and connects the rings with 
                #triangles to form the body. 
    
                currAngle = 0 
                  
                #vertex information is written here 
                for cos,sin,tex in angleData:
                    adjCircle = pos + (perp1 * cos + perp2 * sin) * radius * self.scalar
                    normal = perp1 * cos + perp2 * sin        
                    normalWriter.addData3f(normal) 
                    vertWriter.addData3f(adjCircle) 
                    if self.barkTexture is not None:
                        texWriter.addData2f(tex,sCoord) 
                    else:
                        colorWriter.addData4f(.4,.3,.3,1)
                #we cant draw quads directly so we use Tristrips 
                
                if bottom: 
                    bottom=False
                else:
                             
                    for i in xrange(vNum): 
                        lines.addVertices(i + previousRow,i + startRow)
                    if not self.barkTexture: lines.addVertices(previousRow,startRow)
                    lines.closePrimitive()
                
            if depth + 1 < len(lengthList):
                #move foward along the right axis 
                newPos = pos + quat.getUp() * length * self.scalar
#                if makeColl: 
#                    self.makeColl(pos, newPos, radiusList[depth]) 
                
                numCopies = numCopiesList[depth]  
                if numCopies:
                    angleOffset=random.random()*2*math.pi
                    
                    for i in xrange(numCopies): 
                        newQuat= _angleRandomAxis(quat, 2 * math.pi * i / numCopies+angleOffset, maxbend)
                        newPos2=pos + newQuat.getUp() * length * self.scalar
                        stack.append((newPos2,newQuat, depth + 1, startRow, sCoord))
                else: 
                    #just make another branch connected to this one with a small variation in direction 
                    stack.append((newPos, _randomBend(quat, 20), depth + 1, startRow, sCoord))
            elif doLeaves and (skipLeaves==0 or (random.random()>=skipLeaves)):
                q=Quat()
                q.setHpr((random.random()*2*math.pi,0,0))
                quat=quat*q
                up=quat.getUp()
                
                # size
                
                s=leafSize
                dir1=perp1*s
                dir2=perp2*s
                bend=-up*(s/4.0)
                
                v0=pos+dir1
                v1=pos+dir2+bend
                v2=pos-dir1
                v3=pos-dir2+bend
                
                norm1=dir1.cross(dir2+bend)
                norm1.normalize()
                norm2=dir1.cross(dir2-bend)
                norm2.normalize()
                
                for x in range(2):
                    leafRow = leafVertexWriter.getWriteRow()
                    leafVertexWriter.addData3f(v0)
                    leafVertexWriter.addData3f(v1)
                    leafVertexWriter.addData3f(v2)
                    leafVertexWriter.addData3f(v3)
                    if self.leafTexture is not None:
                        n=dotCount
                        leafTexcoordWriter.addData2f(0,0)
                        leafTexcoordWriter.addData2f(0,n)
                        leafTexcoordWriter.addData2f(n,n)
                        leafTexcoordWriter.addData2f(n,0)
                    else:
                        leafColorWriter.addData4f(.5,.4,.0,1)
                        leafColorWriter.addData4f(.0,.4,.0,1)
                        leafColorWriter.addData4f(.5,.4,.0,1)
                        leafColorWriter.addData4f(.0,.4,.0,1)
                    
                    if x==1:
                        # back sides
                        up=-up
                        norm1=-norm1
                        norm2=-norm2
                        leafTri.addVertices(leafRow+1,leafRow,leafRow+2)
                        leafTri.addVertices(leafRow+2,leafRow,leafRow+3)
                    else:
                        leafTri.addVertices(leafRow,leafRow+1,leafRow+2)
                        leafTri.addVertices(leafRow,leafRow+2,leafRow+3)
                        
                    leafNormalWriter.addData3f(up)
                    leafNormalWriter.addData3f(norm1) 
                    leafNormalWriter.addData3f(up) 
                    leafNormalWriter.addData3f(norm2)

#this is for making the tree not too straight 
def _randomBend(inQuat, maxAngle=20):
    q=Quat()
    angle=random.random()*2*math.pi
    
    #power of 1/2 here makes distrobution even withint a circle
    # (makes larger bends are more likley as they are further spread) 
    ammount=(math.sqrt(random.random()))*maxAngle
    q.setHpr((math.sin(angle)*ammount,math.cos(angle)*ammount,0))
    return inQuat*q


def _angleRandomAxis(inQuat, angle, maxAngle): 
    q=Quat()
    angleRange=0.125
    nangle = angle + math.pi * (angleRange * random.random() - angleRange/2) 
    #power of 1/2 here makes distrobution even withint a circle
    # (makes larger bends are more likley as they are further spread) 
    ammount=(random.random()**(1.0/2))*maxAngle
    q.setHpr((math.sin(nangle)*ammount,math.cos(nangle)*ammount,0))
    return inQuat*q
