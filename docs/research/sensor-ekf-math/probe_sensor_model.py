import numpy as np
from mosaic_perception.domain.models import *
from mosaic_perception.sensors import RangeBearingSensor, VisionBearingSensor
from mosaic_perception.tracking.ekf import ExtendedKalmanFilter as E
def cfg(**k):
    v=dict(sensor_id="r",sensor_type="range_bearing",frame_rate=10.0,noise_std={"range":0.5,"bearing":0.01,"range_rate":0.1},detection_probability=1.0,false_alarm_rate=0.0)
    v.update(k);return SensorConfig(**v)
def ws(obj,obs):
    return WorldState(time=0,objects={"a":ObjectState(object_id="a",position=Vector2(x=obj[0],y=obj[1]),velocity=Vector2(x=obj[2],y=obj[3]))},observer_pose=obs)
e=E()
# 1 consistency: sensor output vs EKF h
obs=Pose2D(position=Vector2(x=3,y=-4),heading=2.9,velocity=Vector2(x=5,y=2))
x=np.array([-20.,30,-3,4])
s=RangeBearingSensor(cfg(noise_std={"range":1e-9,"bearing":1e-9,"range_rate":1e-9}))
o=s.generate_observations(ws(x,obs),0.0)[0]
print("sensor",o.measurements,"ekf",e.measurement_range_bearing(x,obs))
# 2 NIS Monte Carlo with state exactly known (P tiny): mean NIS should be ~3
s=RangeBearingSensor(cfg(),rng=np.random.RandomState(0))
nis=[]
R=np.diag([.25,1e-4,.01]);P=np.diag([1e-9]*4)
for k in range(4000):
    s._last_emit_time=None
    o=s.generate_observations(ws(x,obs),0.0)[0]
    z=np.array([o.measurements[n] for n in("range","bearing","range_rate")])
    h=e.measurement_range_bearing(x,obs)
    r,S=e.innovation(x,P,z,h,e.jacobian_range_bearing(x,obs),np.array(o.measurement_covariance),(1,))
    nis.append(r@np.linalg.solve(S,r))
print("mean NIS (expect 3)",np.mean(nis))
# 3 range clamp: close object, range noise
s=RangeBearingSensor(cfg(noise_std={"range":0.5,"bearing":.01,"range_rate":.1},bias={"range":0.3}),rng=np.random.RandomState(0))
rs=[]
for k in range(5000):
    s._last_emit_time=None
    rs.append(s.generate_observations(ws([0.2,0,0,0],Pose2D()),0.0)[0].measurements["range"])
rs=np.array(rs);print("true 0.2 bias .3: mean",rs.mean(),"expected .5; min",rs.min(),"frac at clamp+bias",np.mean(np.isclose(rs,0.4)))
# 4 near-coincident sensor emits but EKF throws
s=RangeBearingSensor(cfg(noise_std={"range":0,"bearing":0,"range_rate":0}))
o=s.generate_observations(ws([1e-5,0,0,0],Pose2D()),0.0)
print("emitted at 1e-5 m:",len(o), o[0].measurements if o else None)
# 5 bearing noise wrap near pi
s=RangeBearingSensor(cfg(noise_std={"range":.1,"bearing":0.05,"range_rate":.1}),rng=np.random.RandomState(0))
b=[]
for k in range(2000):
    s._last_emit_time=None
    b.append(s.generate_observations(ws([-10,0,0,0],Pose2D()),0.0)[0].measurements["bearing"])
b=np.array(b);print("bearing range",b.min(),b.max(),"frac positive",np.mean(b>0))
# 6 vision sensor ignores nothing; measurement dict keys; vision with reported_cov_scale
v=VisionBearingSensor(SensorConfig(sensor_id="v",sensor_type="vision_bearing",frame_rate=10,noise_std={"bearing":.005},detection_probability=1,false_alarm_rate=0,reported_cov_scale=4.0))
o=v.generate_observations(ws(x,obs),0.0)[0];print("vision cov",o.measurement_covariance,"true var",.005**2)
# 7 frame-rate due: float drift
s=RangeBearingSensor(cfg(frame_rate=30.0))
n=0
for k in range(300):
    n+=len(s.generate_observations(ws(x,obs),k*0.01))
print("30Hz sensor at 100Hz sim 3s:",n,"expected 90")
s=RangeBearingSensor(cfg(frame_rate=10.0));n=0
for k in range(100):
    n+=len(s.generate_observations(ws(x,obs),k*0.07))
print("10Hz sensor at 14.3Hz sim 7s:",n)
# frame_rate zero
try: RangeBearingSensor(cfg(frame_rate=0.0)).generate_observations(ws(x,obs),0.0)
except Exception as ex: print("frame_rate 0:",type(ex).__name__)
