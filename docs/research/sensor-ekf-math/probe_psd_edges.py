import numpy as np
from mosaic_perception.domain.models import *
from mosaic_perception.tracking.ekf import ExtendedKalmanFilter as E
e=E()
# covariance rejection: indefinite shift tolerance, big scale
P=np.diag([1e6,1e6,1e2,1e2.__float__()]);x=np.array([20.,5,1,0]);o=Pose2D(position=Vector2(x=1,y=2),heading=1)
R=np.diag([1e-8,1e-12,1e-8])
for k in range(200):
    x,P=e.predict(x,P);h=e.measurement_range_bearing(x,o)
    try: x,P=e.update(x,P,h+[1e-4,1e-7,1e-4],e.jacobian_range_bearing(x,o),R,h,(1,))
    except ValueError as ex: print("step",k,ex);break
else: print("ok minev",np.linalg.eigvalsh(P)[0])
# PSD shift in _ensure_positive_semidefinite
M=np.diag([1e6,1e6,1,-5e-3.__float__()]);print(e._ensure_positive_semidefinite(M).diagonal(), "(-5e-3 vs scale 1e6 tolerance 1e-8*scale=1e-2 → shifts all diag +5e-3)")
# negative accel_noise 0, zero-cov
print(e.predict(np.zeros(4),np.zeros((4,4)))[1].diagonal())
try: e.update(np.zeros(4)+[10,0,0,0],np.zeros((4,4)),np.array([10,0.0]),e.jacobian_range_bearing(np.array([10.,0,0,0]),None)[:2],np.zeros((2,2)),np.array([10,0.0]),(1,))
except ValueError as ex: print("zero P zero R:",ex)
