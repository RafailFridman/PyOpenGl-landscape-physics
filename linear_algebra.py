from math import sin,cos,pi,sqrt
def Len(v):
    x=v[0]
    y=v[1]
    z=v[2]
    return sqrt(x**2+y**2+z**2)
def Norm(v):
    x=v[0]
    y=v[1]
    z=v[2]
    vlen = Len(v)
    try:
        return (x/vlen,y/vlen,z/vlen)
    except ZeroDivisionError:
        return (0.,0.,0.)
def VAbs(v):
    return (abs(v[0]),abs(v[1]),abs(v[2]))
def VxR(v,r):
    return tuple(r*v[i] for i in range(len(v)))
def VplusV(v1,v2):
    return tuple(v1[i]+v2[i] for i in range(len(v1)))
def VminusV(v1,v2):
    return tuple(v1[i]-v2[i] for i in range(len(v1)))
def VdotV(v1,v2):
    return sum([v1[i]*v2[i] for i in range(len(v1))])
def VxV(v1,v2):
    return (v1[1]*v2[2]-v2[1]*v1[2],-v1[0]*v2[2]+v2[0]*v1[2],v1[0]*v2[1]-v2[0]*v1[1])
def mI():
    return ((1,0,0),(0,1,0),(0,0,1))
def MxR(m,r):
    return tuple(VxR(v,r) for v in m)
def MplusM(m1,m2):
    return tuple(VplusV(m1[i],m2[i]) for i in range(len(m1)))
def MminusM(m1,m2):
    return tuple(VminusV(m1[i],m2[i]) for i in range(len(m1)))
def MxV(m,v):
    return tuple(VdotV(mv,v) for mv in m)
def transpose(m):
    m1=list(map(list,m))
    for i in range(3):
        for j in range(i,3):
            (m1[i][j],m1[j][i])=(m1[j][i],m1[i][j])
    return m1
def MxM(m1,m2):
    m2c=transpose(m2)
    m=[[0,0,0],[0,0,0],[0,0,0]]
    for i in range(3):
        for j in range(3):
            m[i][j]=VdotV(m1[i],m2c[j])
    return tuple(map(tuple,m))
def MRot(v,f):
    s=((0,v[2],-v[1]),
       (-v[2],0,v[0]),
       (v[1],-v[0],0))
    return MplusM(MplusM(mI(),MxR(s,sin(f))),MxR(MxM(s,s),1-cos(f)))
