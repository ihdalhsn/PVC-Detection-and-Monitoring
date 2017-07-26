# ________________________________________DATA DESCRIPTION______________________________________________________________
# MIT BIH DATABASE : PVC Record
# 102_930_940.csv => record ke 102, V5 & V2, durasi 9:30 - 9:40, PVC detected on beat- 9
# 105_010_020.csv => record ke 105, MLII & V1, durasi 0:10 - 0:20, PVC detected on beat- 8
# 108_450_500.csv => record ke 108, MLII, durasi 4:50 - 5:00, PVC on beat- 9
# 108_350_400.csv => record ke 108, MLII, durasi 3:50 - 4:00, PVC on beat- 3
# ______________________________________________________________________________________________________________________
import time
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
from matplotlib.mlab import PCA
import numpy as np
from numpy import array
# import pandas as pd
start_time = time.time()
f = open('data/105_010_020.csv', 'r')
lines = f.readlines()
f.close()

# Discard the first two lines because of header. Takes either column 1 or 2 from each lines (different signal lead)
raw_signal = [0]*(len(lines)-2)
for i in xrange(len(raw_signal)):
	raw_signal[i] = float(lines[i+2].split(',')[1]) #1 for MLII signal
print "==================================="
plt.figure(1)
plt.subplot(411); plt.tight_layout()
plt.title('Raw signal & baseline wander')
plt.plot(range(len(raw_signal)),raw_signal)

# ______________________________________ ECG FILTERING : BANDPASS FILTER________________________________________________
order      = 6
def butter_bandpass_filter(data, lowcut, highcut, fs, order = order):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq

    b, a = butter(order, [low, high], btype='band', analog=False)
    y = lfilter(b, a, data)
    return y
#___________________________________________2.1 ECG FILTERING___________________________________________________________

fps = 360
lowcut = 5
highcut  = 15
filtered_sine = butter_bandpass_filter(raw_signal, lowcut, highcut, fps) #using bandpass filter w/ cutoff 5 Hz & 55Hz [Rodriguez]
plt.subplot(412); plt.tight_layout()
plt.plot(range(len(filtered_sine)),filtered_sine)
plt.title('filtered signal ('+str(order)+' order, '+str(lowcut)+'-'+str(highcut)+' Hz Bandpass filter)')

#__________________________________________2.2 DIFFERENTIATION__________________________________________________________
# Initial conditions
k  = 0; kn = 3600 - 1
y  = []
while (k < kn):
    # print filtered_sine[i], filtered_sine[i+1], filtered_sine[i-1]
    diff = (filtered_sine[k+1] - filtered_sine[k-1])/360
    y.append(diff)
    # print diff, k
    k += 1
plt.subplot(413); plt.tight_layout()
plt.plot(range(len(y)),y)
plt.title('filtered signal after differentiation')
#_________________________________________2.3 HILBERT TRANSFORM_________________________________________________________
from scipy.fftpack import fft, ifft
# STEPS :
# 1. do FFT for y signal and store to vector f
y       = np.array(y);
f       = fft(y);
# 2. create vector h as follows:
#       0 for i = (N/2)+2,..,..N
#       1 for i = (2,3,..,(N/2)
#       2 for i = 1, (N/2)+1
N   = 3599
h   = [0]*N
a   = (N/2)+2
bin = 1; b = N/2
c   = (N/2)+1
while (a < N):
    h[a] = 0
    a   += 1
while (bin < b):
    h[bin] = 1
    bin   += 1
h[0]        = 2
h[(N/2)+1]  = 2
h           = np.array(h)
# 3. Invers FFT of f*h
fh_list = []
for i in range(N):
    fh_temp = f[i]*h[i]
    fh_list.append(fh_temp)
fh = np.array(fh_list)
yh = ifft(fh); H  = yh
# The analytic signal
z = y + yh
# The envelope a of z or instantaneous magnitude of z
y_square  = y**2
yh_square = yh**2
a_temp    = y_square + yh_square
a         = np.sqrt(a_temp)
# The instantaneous phase angle in the complex plane
theta      = np.arctan(yh/y)
print "f :", f, len(f)
print "h :", h, len(h)
print "y :", y, len(y), type(y)
print "fh :", fh, len(fh)
print "yh :", yh, len(yh), type(yh)
print "z :", z, len(z), type(z)
print "a :", a, len(a), type(a)
print "theta :", theta, len(theta), type(theta)
plt.figure(2)
plt.subplot(211); plt.tight_layout()
plt.plot(range(len(z)),np.real(z))
plt.title('Analytic signal(z)')

# plt.figure(2)
# plt.subplot(411); plt.tight_layout()
# plt.plot(range(len(theta)),np.real(theta))
# plt.title('Theta')
# ________________________________________2.4 Adaptive Thresholding_____________________________________________________
# The upper threshold
print "=========================================="
alpha = np.amax(y); print "max value of y: ", alpha
upper_th = 0.5 * alpha; print "upper threshold: ", upper_th
lower_th = 0.10 * alpha; print "lower threshold: ", lower_th

# The threshold value are updated in iteration time
# Nu = number peak detected by upper_th
# Nl = number peak detected by lower_th
# The threshold are updated PER iteration, meanwhile the number of detected peak by up and down limit is different
# The updated value of upper_th & lower_th is obtained by
w = 0.125 #error weight
delta = upper_th - lower_th

# === Try to get peak above upper_th & above lower_th ===
old_upper = upper_th
old_lower = lower_th
for i in range(N):
    lower_value = []
    lower_index = []
    if(z[i] > old_lower):
        lower_value.append(z[i])
        lower_index.append(i)
        plt.plot(i, np.real(z[i]), 'g.', markersize=5)
    upper_value = []
    upper_index = []
    if(z[i] > old_upper):
        upper_value.append(z[i])
        upper_index.append(i)
        plt.plot(i, np.real(z[i]), 'r.', markersize=5)

    #IF we update the upper & lower threshold per iteration, put here
    new_upper = old_upper - (w*(old_upper - old_lower))
    new_lower = old_lower + (w*(old_upper - old_lower))
    old_upper = new_upper
    old_lower = new_lower

# === UPDATE THRESHOLD PER ITERATION ===
# upper_th_list = [0]*3599
# lower_th_list = [0]*3599
# upper_th_list.append(upper_th)
# lower_th_list.append(lower_th)
# i = 1
# for i in range(N):
#     upper_th_list[i] = upper_th_list[i-1] - (w*delta)
#     lower_th_list[i] = lower_th_list[i-1] + (w*delta)
# print "upper th list:", upper_th_list #should be decrease
# print "lower th list:", lower_th_list #should be increase

# _________________________________________PRINCIPAL COMPONENT ANALYSIS_________________________________________________
print "=========== PRINCIPAL COMPONENT ANALYSIS =============="
# Transform 1x3600 data to 600x6 vector
# print z, type(z), len(z)
B = np.zeros(shape=(6,599)) #i 0 - 5
i = 0; j = 0; stop = 599;
for i in range(6):
    # print i, j, stop, stop - j
    list = []
    while (j < stop):
        list.append(np.real(z[j]))
        j = j + 1
    B[i] = list
    j = stop + 1
    stop = j + 599
# transpose B
# data = B
B = B.T
print "Represent data to vector M x N : ", B
print "Vector dimension : ", B.shape, type(B)
# 1. Calculate the mean vector each heart beat
print "============== MEAN VECTOR EACH HEART BEAT ================="
mean1 = np.mean(B[:,0])
mean2 = np.mean(B[:,1])
mean3 = np.mean(B[:,2])
mean4 = np.mean(B[:,3])
mean5 = np.mean(B[:,4])
mean6 = np.mean(B[:,5])
print "Means per coloum : ", mean1, mean2, mean3, mean4, mean5, mean6
# 2. Compute the mean adjusted data
B[:,0] = [x - mean1 for x in B[:,0]]
B[:,1] = [x - mean2 for x in B[:,1]]
B[:,2] = [x - mean3 for x in B[:,2]]
B[:,3] = [x - mean4 for x in B[:,3]]
B[:,4] = [x - mean5 for x in B[:,4]]
B[:,5] = [x - mean6 for x in B[:,5]]
print "Mean adjusted data : ", B
# 3. Compute the covariance matrix
print "============== COVARIANCE ================="
B_cov = np.cov(B)
print "Covariance Matrix : ", B_cov, type(B), B.shape
# 4. Calculate the eigen vector (e_i) & eigen value (lambda_i) of the covariance matrix, i=1,..,N
# from numpy import linalg as LA
# Bval_0, Bvec_0 = LA.eig(np.diag(B[:,0]))
# B_val_0 = LA.eigvals(np.array(B_cov.tolist(), dtype=float))
# print "Bval_0 : ", Bval_0, Bval_0.shape
# print "B_val_0 : ", B_val_0, B_val_0.shape
# print "Bvec_0 : ", Bvec_0, Bvec_0.shape



# _________________________________________________ESTIMATED TIME_______________________________________________________
print "============= RESPON TIME ============================="
end_time      = time.time()
response_time = end_time - start_time
print "Time : " + str(response_time) + " seconds"
plt.show()


