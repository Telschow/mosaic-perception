import numpy as np, math
from mosaic_perception.tracking.ekf import ExtendedKalmanFilter as E
from mosaic_perception.domain.models import Pose2D, Vector2, wrap_angle
e=E(dt=0.1)
def fd(f,x,h=1e-6):
    J=[]
    for i in range(4):
        d=np.zeros(4);d[i]=h
        a=f(x+d)-f(x-d)
        a=np.array([wrap_angle(v) if k==1 else v for k,v in enumerate(a)]) if a.size==3 else np.array([wrap_angle(a[0])])
        J.append(a/(2*h))
    return np.array(J).T
rng=np.random.RandomState(1)
worst=0;worstb=0
for _ in range(2000):
    x=rng.uniform(-50,50,4)
    o=Pose2D(position=Vector2(x=rng.uniform(-50,50),y=rng.uniform(-50,50)),heading=rng.uniform(-7,7),velocity=Vector2(x=rng.uniform(-10,10),y=rng.uniform(-10,10)))
    if np.hypot(x[0]-o.position.x,x[1]-o.position.y)<2: continue
    J=e.jacobian_range_bearing(x,o); Jn=fd(lambda s:e.measurement_range_bearing(s,o),x)
    worst=max(worst,np.max(np.abs(J-Jn)/(1+np.abs(Jn))))
    Jb=e.jacobian_bearing(x,o); Jbn=fd(lambda s:e.measurement_bearing(s,o),x)
    worstb=max(worstb,np.max(np.abs(Jb-Jbn)))
print("jac relerr rb",worst,"b",worstb)
# wrap
for a in [math.pi,-math.pi,3*math.pi,1e6,-1e6,float('nan')]:
    print("wrap",a,wrap_angle(a))
# near-pi innovation
x=np.array([-10.,1e-9,0,0]);o=Pose2D()
print("meas near pi",e.measurement_bearing(x,o), e.measurement_bearing(np.array([-10.,-1e-9,0,0]),o))
# repeated updates PSD
P=np.diag([4,4,1,1.]);x=np.array([20.,5,1,0]);o=Pose2D(position=Vector2(x=1,y=2),heading=2.5,velocity=Vector2(x=3,y=-1))
R=np.diag([.25,1e-4,.01]);minev=1;asym=0
for k in range(3000):
    x,P=e.predict(x,P)
    z=e.measurement_range_bearing(x,o)+rng.multivariate_normal(np.zeros(3),R)
    h=e.measurement_range_bearing(x,o);J=e.jacobian_range_bearing(x,o)
    x,P=e.update(x,P,z,J,R,h,(1,))
    minev=min(minev,np.linalg.eigvalsh(P)[0]);asym=max(asym,abs(P-P.T).max())
print("3000 upd minev",minev,"asym",asym)
# tiny-R / singular R
try:
    P0=np.diag([4,4,1,1.]);x0=np.array([20.,5,1,0])
    Rz=np.diag([1e-12,1e-12,1e-12]);h=e.measurement_range_bearing(x0,o)
    x1,P1=e.update(x0,P0,h,e.jacobian_range_bearing(x0,o),Rz,h,(1,));print("tiny R ok",np.linalg.eigvalsh(P1)[0])
except Exception as ex: print("tiny R",type(ex).__name__,ex)
# coincident
for s in [np.array([1.,2,0,0]),np.array([1.+1e-8,2,0,0])]:
    try: print(e.measurement_range_bearing(s,Pose2D(position=Vector2(x=1,y=2))))
    except Exception as ex: print("coinc",ex)
# range near 1e-9 jacobian blowup
x=np.array([1+1e-6,2,0,0]);print("jac at 1e-6",e.jacobian_range_bearing(x,Pose2D(position=Vector2(x=1,y=2)))[1])
# range-rate at tiny range sensitivity
# PSD tolerance: -1e-8*scale then shift
# sensor stats
from mosaic_perception.sensors.range_bearing import RangeBearingSensor
