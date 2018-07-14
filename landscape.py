from math import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
from linear_algebra import *
import numpy as np
import numpy.random as rnd
from random import randint
import time

window_width = 800
window_height = 600

camPos = (1,1,1)
camDir = (1,1,0)
camUp = (0,0,1)
camMode = False

objPos = (1,1,1)
objDir = (1,1,0)
objMass = 1
objVel = (0,0,0)

mg = VxR((0,0,-1),objMass*0.1)

image = Image.open("map.bmp")
width  = image.size[0]
height = image.size[1]
pix = image.load()

heights = np.array([[0 for i in range(width)] for i in range(height)],dtype=np.float)
for x in range(width):
        for y in range(height):
            heights[x,y] = pix[x,y]/10
map = heights
spheres = np.array([((randint(1,10),randint(1,10)),0.5) for i in range(10)])

def loadImage(imageName):
    im = Image.open(imageName)
    try:
        ix, iy, image = im.size[0], im.size[1], im.tobytes("raw", "RGB", 0, -1)
    except SystemError:
        ix, iy, image = im.size[0], im.size[1], im.tobytes("raw", "RGB", 0, -1)
    glEnable(GL_TEXTURE_2D)
    ID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, ID)

    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGB, GL_UNSIGNED_BYTE, image)
    return ID

def landscape(map):
    global texID
    k=8.0
    for x in range(1,128,2):
        for y in range(1,128,2):
            glBegin(GL_TRIANGLE_FAN)
            glColor3f(1,1,1)
            glTexCoord2f((x%k)/k, (y%k)/k)
            glVertex3d( x,  y, map[x,y])

            glTexCoord2f(((x-1)%k)/k, (y%k)/k)
            glVertex3d( x-1,  y, map[x-1,y])

            glTexCoord2f(((x-1)%k)/k, ((y-1)%k)/k)
            glVertex3d( x-1,  y-1, map[x-1,y-1])

            glTexCoord2f(((x)%k)/k, ((y-1)%k)/k)
            glVertex3d( x,  y-1, map[x,y-1])

            glTexCoord2f(((x+1)%k)/k if ((x+1)%k)!=0 else 1, ((y-1)%k)/k)
            glVertex3d( x+1,  y-1, map[x+1,y-1])

            glTexCoord2f(((x+1)%k)/k if ((x+1)%k)!=0 else 1, ((y)%k)/k)
            glVertex3d( x+1,  y, map[x+1,y])

            glTexCoord2f(((x+1)%k)/k if ((x+1)%k)!=0 else 1, ((y+1)%k)/k if ((y+1)%k)!=0 else 1)
            glVertex3d( x+1,  y+1, map[x+1,y+1])

            glTexCoord2f(((x)%k)/k,((y+1)%k)/k if ((y+1)%k)!=0 else 1)
            glVertex3d( x,  y+1, map[x,y+1])

            glTexCoord2f(((x-1)%k)/k, ((y+1)%k)/k if ((y+1)%k)!=0 else 1)
            glVertex3d( x-1,  y+1, map[x-1,y+1])

            glTexCoord2f(((x-1)%k)/k, ((y)%k)/k)
            glVertex3d( x-1,  y, map[x-1,y])
            glEnd()

def init():
    global lasttime,texID,n,spheres
    glEnable(GL_DEPTH_TEST)
    glClearColor(1.0, 1.0, 1.0, 1.0) # Белый цвет для первоначальной закраски
    # Задаем перспективу
    #gluOrtho2D(-1.0, 1.0, -1.0, 1.0) # Определяем границы рисования по горизонтали и вертикали
    global anglex, angley, anglez, filled
    filled = 0
    lasttime = time.time()
    texID = loadImage("map2.bmp")

    n = glGenLists(1)
    glNewList(n, GL_COMPILE)
    landscape(heights)
    glEndList()

# Процедура обработки обычных клавиш
def keyboardkeys(key, x, y):
    global  filled,camDir,camUp,camPos,objPos,objDir,objVel,camMode,spheres,pos, dtime, force
    if camMode:
        if key == b'\x1b':
            sys.exit(0)
        if key == b's':
            m = MRot(VxV(camDir,camUp),-0.1)
            camUp = MxV(m,camUp)
            camDir = MxV(m,camDir)
        if key == b'w':
            m = MRot(VxV(camDir,camUp),0.1)
            camUp = MxV(m,camUp)
            camDir = MxV(m,camDir)
        if key == b'q':
            camUp = MxV(MRot(camDir,0.1),camUp)
        if key == b'e':
            camUp = MxV(MRot(camDir,-0.1),camUp)
        if key == b'a':
            camDir = MxV(MRot(camUp,-0.1),camDir)
        if key == b'd':
            camDir = MxV(MRot(camUp,0.1),camDir)
        if key == b'-':
            camPos = VminusV(camPos,VxR(camDir,1))
        if key == b'=':
            camPos = VplusV(camPos,VxR(camDir,1))

        if key == b'i':
            objPos=VplusV(objPos,VxR(objDir,0.00001))
        if key == b'k':
            objPos=VminusV(objPos,VxR(objDir,0.00001))
        if key == b'j':
            objDir = MxV(MRot((0,0,1),-0.1),objDir)
        if key == b'l':
            objDir = MxV(MRot((0,0,1),0.1),objDir)
        if key == b'c':
            camMode = not camMode
        if key == b' ':
            filled = 1 - filled
    else:

        if key == b'\x1b':
            sys.exit(0)
        if key == b'y':
            force = VxR(objDir,1.1)
            tforce = VplusV(mg,force)
            a = acceleration(objPos,tforce)
            nvel = VxR(a,dtime)
            objVel = VplusV(objVel,nvel)
            objPos=VplusV(objPos,VxR(objVel,dtime))
        if key == b'h':
            force = VxR(objDir,-1.1)
            tforce = VplusV(mg,force)
            a = acceleration(objPos,tforce)
            nvel = VxR(a,dtime)
            objVel = VplusV(objVel,nvel)
            objPos=VplusV(objPos,VxR(objVel,dtime))
        if key == b'i':
            objPos= VplusV(objPos,VxR(objDir,1))
            objVel=(0,0,0)
            camPos = VplusV(VminusV((objPos[0],objPos[1],getappl(objPos[0],objPos[1])),objDir),(0,0,1))
        if key == b'k':
            objPos= VminusV(objPos,VxR(objDir,1))
            objVel=(0,0,0)
            camPos = VplusV(VminusV((objPos[0],objPos[1],getappl(objPos[0],objPos[1])),objDir),(0,0,1))
        if key == b'j':
            temp = MxV(MRot((0,0,1),-0.1),objDir)
            objDir = temp
            camDir = temp
        if key == b'l':
            temp = MxV(MRot((0,0,1),0.1),objDir)
            objDir = temp
            camDir = temp
        if key == b'c':
            camMode = not camMode
        if key == b'g':
            shoot(pos,objDir,spheres)
        if key == b' ':
            filled = 1 - filled
    #glutPostRedisplay()         # Вызываем процедуру перерисовки

def cilinder():
    R = 0.5

    glBegin(GL_TRIANGLE_FAN)

    glVertex3d( 0,  0, -0.5)
    for i in range(21):
        glVertex3d(R * cos(2*pi*i/20), \
            R * sin(2*pi*i/20), -0.5)

    glEnd()

    glBegin(GL_QUAD_STRIP)

    for i in range(21):
        glVertex3d(R * cos(2*pi*i/20), \
            R * sin(2*pi*i/20), -0.5)
        glVertex3d(R * cos(2*pi*i/20), \
            R * sin(2*pi*i/20), 0.5)

    glEnd()

    glBegin(GL_TRIANGLE_FAN)

    glVertex3d( 0,  0, 0.5)
    for i in range(21):
        glVertex3d(R * cos(2*pi*i/20), \
            R * sin(2*pi*i/20), 0.5)

    glEnd()
def conus():
    R = 0.5

    glBegin(GL_TRIANGLE_FAN)

    glVertex3d( 0,  0, -0.5)
    for i in range(21):
        glVertex3d(R * cos(2*pi*i/20), \
            R * sin(2*pi*i/20), -0.5)

    glEnd()

    glBegin(GL_TRIANGLE_FAN)

    glVertex3d( 0,  0, 0.5)
    for i in range(21):
        glVertex3d(R * cos(2*pi*i/20), \
            R * sin(2*pi*i/20), -0.5)

    glEnd()
def sphere():
    R = 0.5

    for j in range(-9,9):
        glBegin(GL_QUAD_STRIP)

        for i in range(21):
            glVertex3d(R * cos(pi*j/18) * cos(2*pi*i/20), \
                R * cos(pi*j/18) * sin(2*pi*i/20), \
                R * sin(pi*j/18))
            glVertex3d(R * cos(pi*(j+1)/18) * cos(2*pi*i/20), \
                R * cos(pi*(j+1)/18) * sin(2*pi*i/20), \
                R * sin(pi*(j+1)/18))

        glEnd()
def sphere2(x,y,z,r):
    R = r
    glColor3d(0,0,0)
    for j in range(-9,9):
        glBegin(GL_QUAD_STRIP)

        for i in range(21):
            glVertex3d(x+R * cos(pi*j/18) * cos(2*pi*i/20), \
                y+R * cos(pi*j/18) * sin(2*pi*i/20), \
                z+R * sin(pi*j/18))
            glVertex3d(x+R * cos(pi*(j+1)/18) * cos(2*pi*i/20), \
                y+R * cos(pi*(j+1)/18) * sin(2*pi*i/20), \
                z+R * sin(pi*(j+1)/18))

        glEnd()
def thor():
    R = 0.5
    R2 = R * 0.3

    for i in range(20):
        glBegin(GL_QUAD_STRIP)

        for j in range(21):
            glVertex3d((R + R2 * cos(2*pi*j/20)) * cos(2*pi*i/20), \
                (R + R2 * cos(2*pi*j/20)) * sin(2*pi*i/20), \
                R2 * sin(2*pi*j/20))
            glVertex3d((R + R2 * cos(2*pi*j/20)) * cos(2*pi*(i+1)/20), \
                (R + R2 * cos(2*pi*j/20)) * sin(2*pi*(i+1)/20), \
                R2 * sin(2*pi*j/20))

        glEnd()
def cube():
    glBegin(GL_QUADS)

    glVertex3d( 0.5,  0.5, 0.5)
    glVertex3d(-0.5,  0.5, 0.5)
    glVertex3d(-0.5, -0.5, 0.5)
    glVertex3d( 0.5, -0.5, 0.5)

    glVertex3d( 0.5,  0.5,-0.5)
    glVertex3d(-0.5,  0.5,-0.5)
    glVertex3d(-0.5, -0.5,-0.5)
    glVertex3d( 0.5, -0.5,-0.5)

    glVertex3d( 0.5,  0.5, 0.5)
    glVertex3d( 0.5,  0.5,-0.5)
    glVertex3d( 0.5, -0.5,-0.5)
    glVertex3d( 0.5, -0.5, 0.5)

    glVertex3d(-0.5,  0.5, 0.5)
    glVertex3d(-0.5,  0.5,-0.5)
    glVertex3d(-0.5, -0.5,-0.5)
    glVertex3d(-0.5, -0.5, 0.5)

    glVertex3d( 0.5,  0.5, 0.5)
    glVertex3d( 0.5,  0.5,-0.5)
    glVertex3d(-0.5,  0.5,-0.5)
    glVertex3d(-0.5,  0.5, 0.5)

    glVertex3d( 0.5, -0.5, 0.5)
    glVertex3d( 0.5, -0.5,-0.5)
    glVertex3d(-0.5, -0.5,-0.5)
    glVertex3d(-0.5, -0.5, 0.5)

    glEnd()
def cube2(x,y,z):
    glBegin(GL_QUADS)

    glVertex3d( 0.5+x,  0.5+y, 0.5+z)
    glVertex3d(-0.5+x,  0.5+y, 0.5+z)
    glVertex3d(-0.5+x, -0.5+y, 0.5+z)
    glVertex3d( 0.5+x, -0.5+y, 0.5+z)

    glVertex3d( 0.5+x,  0.5+y,-0.5+z)
    glVertex3d(-0.5+x,  0.5+y,-0.5+z)
    glVertex3d(-0.5+x, -0.5+y,-0.5+z)
    glVertex3d( 0.5+x, -0.5+y,-0.5+z)

    glVertex3d( 0.5+x,  0.5+y, 0.5+z)
    glVertex3d( 0.5+x,  0.5+y,-0.5+z)
    glVertex3d( 0.5+x, -0.5+y,-0.5+z)
    glVertex3d( 0.5+x, -0.5+y, 0.5+z)

    glVertex3d(-0.5+x,  0.5+y, 0.5+z)
    glVertex3d(-0.5+x,  0.5+y,-0.5+z)
    glVertex3d(-0.5+x, -0.5+y,-0.5+z)
    glVertex3d(-0.5+x, -0.5+y, 0.5+z)

    glVertex3d( 0.5+x,  0.5+y, 0.5+z)
    glVertex3d( 0.5+x,  0.5+y,-0.5+z)
    glVertex3d(-0.5+x,  0.5+y,-0.5+z)
    glVertex3d(-0.5+x,  0.5+y, 0.5+z)

    glVertex3d( 0.5+x, -0.5+y, 0.5+z)
    glVertex3d( 0.5+x, -0.5+y,-0.5+z)
    glVertex3d(-0.5+x, -0.5+y,-0.5+z)
    glVertex3d(-0.5+x, -0.5+y, 0.5+z)

    glEnd()

def plane(p1,p2,p3):
    if p1[0]<0 or p1[1]<0 or p2[0]<0 or p2[1]<0 or p3[0]<0 or p3[1]<0 or p1[0]>128 or p1[1]>128 or p2[0]>128 or p2[1]>128 or p3[0]>128 or p3[1]>128:
        return (0,0,1,-1)
    else:
        v1=VminusV((p2[0],p2[1],heights[p2[0],p2[1]]),(p1[0],p1[1],heights[p1[0],p1[1]]))
        v2=VminusV((p3[0],p3[1],heights[p3[0],p3[1]]),(p1[0],p1[1],heights[p1[0],p1[1]]))
        n=VxV(v1,v2)
        point=(p1[0],p1[1],heights[p1[0],p1[1]])
        d=-(VdotV(n,point))
    return (*n,d)

def normal(x,y):
    if (int(x)+int(y))%2==0:
        if x%1<y%1:
            pl = plane((int(x),int(y)),(int(x),int(y+1)),(int(x+1),int(y+1)))
        else:
            pl = plane((int(x),int(y)),(int(x+1),int(y+1)),(int(x+1),int(y)))
    else:
        if (1-x%1)<y%1:
            pl = plane((int(x+1),int(y)),(int(x),int(y+1)),(int(x+1),int(y+1)))
        else:
            pl = plane((int(x),int(y)),(int(x),int(y+1)),(int(x+1),int(y)))
    pl = (pl[0],pl[1],pl[2])
    if pl[2]<0:
        return Norm(VxR((pl[0],pl[1],pl[2]),-1))
    else:
        return Norm(pl)

def getappl(x,y):
    if x<0 or x>128 or y<0 or y>128:
        return 1
    else:
        if (int(x)+int(y))%2==0:
            if x%1<y%1:
                pl = plane((int(x),int(y)),(int(x),int(y+1)),(int(x+1),int(y+1)))
            else:
                pl = plane((int(x),int(y)),(int(x+1),int(y+1)),(int(x+1),int(y)))
        else:
            if (1-x%1)<y%1:
                pl = plane((int(x+1),int(y)),(int(x),int(y+1)),(int(x+1),int(y+1)))
            else:
                pl = plane((int(x),int(y)),(int(x),int(y+1)),(int(x+1),int(y)))
        return -(pl[0]*x+pl[1]*y+pl[3])/pl[2]

def hor(p1,p2):
    d = VminusV(p2,p1)
    k=int(max(abs(d[0]),abs(d[1])))
    step = 1/k
    for i in range(k):
        cur = VplusV(p1,VxR(d,i*step))
        if cur[2]<getappl(cur[0],cur[1]):
            return False
    return True

def drawlist(clist):
    for c in clist:
        sphere2(*c[0],c[1])

def dist(point,linep,dir):
    return Len(VxV(VminusV(linep,point),dir))/Len(dir)

def closest(pos,dir,clist):
    mindist=dist(clist[0][0],pos,dir)
    mini=0
    for i in range(len(clist)):
        cur=dist(clist[i][0],pos,dir)
        vec = VminusV(clist[i][0],pos)
        if (cur<clist[i][1]) and cur<mindist and VdotV(vec,dir)>=0:
            mindist = cur
            mini = i
    return clist[mini]

def shoot(pos,dir,clist):
    for c in clist:
         if dist(c[0],pos,dir)<c[1] and c==closest(pos,dir,clist):
            clist.remove(c)
            print("REMOVED")

def total_force(mg,force):
    return VplusV(mg,force)

def acceleration(objPos,tforce):
    x= objPos[0]
    y=objPos[1]
    n = normal(x,y)
    fnormal = VxR(n,VdotV(n,tforce))
    fp = VminusV(tforce,fnormal)
    return VxR(fp,1/objMass)


spheres = [((*spheres[i,0],getappl(*spheres[i,0])+0.5),0.5) for i in range(len(spheres))]

# Процедура рисования
def draw(*args, **kwargs):
    global camPos,camDir,camUp,spheres,pos,lasttime,dtime, heights,filled, n,objPos, objVel
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # Очищаем экран и заливаем текущим цветом фона

    curtime = time.time()
    dtime = curtime-lasttime
    lasttime = curtime

    glMatrixMode(GL_PROJECTION) # Выбираем матрицу проекций
    glLoadIdentity()            # Сбрасываем все предыдущие трансформации
    gluPerspective(90, window_width / window_height, 0.01, 100)
    glMatrixMode(GL_MODELVIEW) # Выбираем модельно-видовую матрицу
    glLoadIdentity()           # Сбрасываем все предыдущие трансформации
    if not camMode:
        temp = VplusV(VminusV((objPos[0],objPos[1],getappl(objPos[0],objPos[1])),objDir),camUp)
        if getappl(objPos[0],objPos[1])>getappl(camPos[0],camPos[1]):
            camPos = (temp[0],temp[1],getappl(objPos[0],objPos[1])+0.5)
        else:
            camPos = (temp[0],temp[1],getappl(camPos[0],camPos[1])+0.5)
        camDir = objDir
        camUp = (0,0,1)
    gluLookAt(*camPos,        # Положение камеры
        *VplusV(camPos,camDir),           # Точка, на которую смотрит камера
        *camUp)           # Направление "верх" камеры

    glBindTexture(GL_TEXTURE_2D, texID)

    #landscape(heights)
    glCallList(n)

    force = (0,0,0)
    tforce = VplusV(mg,force)
    a = acceleration(objPos,tforce)
    nvel = VxR(a,dtime)
    objVel = VplusV(objVel,nvel)
    objVel = VxR(objVel,0.9999)
    if VAbs(objVel)<(0.0001,0.0001,0.0001):
        objVel=(0,0,0)
    objPos=VplusV(objPos,objVel)

    pos=(objPos[0],objPos[1],getappl(objPos[0],objPos[1])+0.5)

    if pos[0]>128 or pos[0]<0 or pos[1]>128 or pos[1]<0:
        objVel=VxR(objVel,-0.3)
    print(objVel)
    sphere2(*pos,0.5)

    #print(hor((objPos[0],objPos[1],getappl(objPos[0],objPos[1])+0.5),(1,0,1)))
    #drawlist(spheres)

    glBegin(GL_LINES)
    glVertex3d(*pos)
    glVertex3d(1,0,1)

    glVertex3d(*pos)
    glVertex3d(*VplusV(pos,objDir))
    glEnd()

    glMatrixMode(GL_PROJECTION) # Выбираем матрицу проекций
    glLoadIdentity()
    glMatrixMode(GL_MODELVIEW) # Выбираем модельно-видовую матрицу
    glLoadIdentity()

    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glBegin(GL_QUADS)
    glVertex3d(-0.1,-0.1,0)
    glVertex3d(0.1,-0.1,0)
    glVertex3d(0.1,0.1,0)
    glVertex3d(-0.1,0.1,0)
    glEnd()
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    if filled == 0:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)


    #if dtime!=0:
    #    print(1/dtime)

    glutSwapBuffers()           # Меняем буферы
    glutPostRedisplay()         # Вызываем процедуру перерисовки

glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(window_width, window_height)
glutInitWindowPosition(50, 50)
glutInit(sys.argv)
glutCreateWindow(b"OpenGL Second Program!")
# Определяем процедуру, отвечающую за рисование
glutDisplayFunc(draw)
# Определяем процедуру, отвечающую за обработку обычных клавиш
glutKeyboardFunc(keyboardkeys)
# Вызываем нашу функцию инициализации

init()
glutMainLoop()
