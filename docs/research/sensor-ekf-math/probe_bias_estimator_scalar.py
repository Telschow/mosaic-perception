import numpy as np
# scalar replica of tracker._update_bias (tracker.py:299-340, process add at :403)
def run(scale,rb_bias=0.0,n=3000,seed=0):
    rng=np.random.RandomState(seed);b=0.0;v=0.05**2;tv=0.01  # true vision bias
    sv,sr=0.005,0.01
    for _ in range(n):
        v+=1e-8
        d=(tv+rng.normal(0,sv))-(rb_bias+rng.normal(0,sr))-b
        R=(sv**2+sr**2)*scale
        g=v/(v+R);b+=g*d;v*=(1-g)
    return b-tv,np.sqrt(v)
errs=[run(s,seed=k) for s in (1.0,) for k in range(200)]
for s in (1.0,0.1):
    e=np.array([run(s,seed=k)[0] for k in range(300)]);print("scale",s,"rms err",e.std(),"reported sd",run(s)[1])
print("range-bearing bias .005 leaks:",run(1.0,rb_bias=0.005)[0],"(expected -0.005)")
