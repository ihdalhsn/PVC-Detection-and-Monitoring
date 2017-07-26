# ________________________________________DATA DESCRIPTION______________________________________________________________
# MIT BIH DATABASE : PVC Record
# 105_010.csv => record ke 105, MLII & V1, durasi 0:10 - 0:20, PVC detected on beat- 8
# 101_010.csv => record ke 101, MLII & V2, durasi 0:00 - 0:10
#
# ______________________________________________________________________________________________________________________
import time
import bwr
import matplotlib.pyplot as plt
import numpy as np
from numpy import array
# import pandas as pd
from scipy.signal import butter, lfilter, find_peaks_cwt
from scipy import interpolate

start_time = time.time()
# Read input csv file from physionet
f = open('data/105_010_020.csv', 'r')
lines = f.readlines()
f.close()

# Discard the first two lines because of header. Takes either column 1 or 2 from each lines (different signal lead)
raw_signal = [0]*(len(lines)-2)
for i in xrange(len(raw_signal)):
	raw_signal[i] = float(lines[i+2].split(',')[1])

# Call the BWR method
(baseline, ecg_out) = bwr.bwr(raw_signal)
print "==================================="

plt.subplot(4,1,1); plt.tight_layout()
plt.title('Raw signal & baseline wander')
plt.plot(raw_signal, 'b-')
plt.plot(baseline, 'r-')

plt.subplot(4,1,2); plt.tight_layout()
plt.plot(range(len(ecg_out)),ecg_out)
plt.title('After baseline cancellation')

# ___________________________________HIGHPASS FILTER____________________________________________________________________
def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def butter_highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y
# ______________________________________BANDPASS FILTER_________________________________________________________________
def butter_bandpass_filter(data, lowcut, highcut, fs, order=6):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq

    b, a = butter(order, [low, high], btype='band', analog=False)
    y = lfilter(b, a, data)
    return y
#_______________________________________________________________________________________________________________________

fps = 360
#filtered_sine = butter_highpass_filter(ecg_out,1,fps) #using highpass only
filtered_sine = butter_bandpass_filter(raw_signal,5, 15, fps) #using bandpass filter w/ cutoff 0.5Hz & 45Hz [UMAJI]

plt.subplot(4,1,3)
plt.plot(range(len(filtered_sine)),filtered_sine)
plt.title('filtered signal')
# ________________________________________EMPIRICAL MODE DECOMPOSITION__________________________________________________
#1. start with the signal d1(t) = x(t), K=1, sifting process hj(t) = dk(t), j=0
x = np.array(filtered_sine) #convert ecg_out from list type to numpy.ndarray
d = np.array([])
h = np.array([])

d_list = []
h_list = []

d_array = []
k = 1
finished = False
while (not finished):
    d = x; d_list.append(d);
    j = 0
#   1. Sifting Process
    h = d; h_list.append(h);
    IMF = False
    while (not IMF):
            IMF = True
            finished = True
#         2. identify all local extrema of h
            step = 400 #step per beat to recognize the R point
            # Using find_peaks_cwt
            # peaks = find_peaks_cwt(h, np.arange(1, step), gap_thresh = 1)
            # print peaks
            # time = np.arange(0,10,360)
            # plt.plot(len(h),h[peaks],'ro')



#         3. compute upper & lower envelope using cubic spline interpolation. Produce : EnvMax(t) & EnvMin(t)
# ____________________________________________CUBIC SPILNE______________________________________________________________
#
# x = np.arange(0, 2*np.pi+np.pi/4, 2*np.pi/8)
# y = np.sin(x)
# tck = interpolate.splrep(x, y, s=0)
# xnew = np.arange(0, 2*np.pi, np.pi/50)
# ynew = interpolate.splev(xnew, tck, der=0)
#
# plt.figure()
# plt.plot(x, y, 'x', xnew, ynew, xnew, np.sin(xnew), x, y, 'b')
# plt.legend(['Linear', 'Cubic Spline', 'True'])
# plt.axis([-0.05, 6.33, -1.05, 1.05])
# plt.title('Cubic-spline interpolation')
# plt.show()
# ______________________________________________________________________________________________________________________
#         4. calculate mean. Produce : m(t) = 1/2(EnvMax(t) + EnvMin(t))
#         5. extract the detail. Produce : h[j+1](t) = h[j](t) - m(t)
#         6. if (h[j+1](t) not IMF(t)):
#               IMF = False; j += 1;
#            else:
#               IMF = True (exit extractionloop)
#           7.  extract the mode. Produce : d[k](t) = h[j+1](t)
#           8.  calculate the residual. Produce r[k](t) = x(t) - d[k](t)
#           9.  if (r[k](t) < 2 local minima or r[k](t) > 2 local extrema :
#                   finished = True
#               else
#                   finished = False; k += 1

end_time      = time.time()
response_time = end_time - start_time
print "Time : " + str(response_time) + "seconds"
plt.show()

# IMF
# 1. jumlah Extrema harus sama dengan jumlah zero crossings ATAU selisih dari jumlah extrema dan
# zero crossing maksimal 1
# 2. untuk setiap point, nilai rata2 envelope didefinisikan oleh local maxima,
# dan envelope yang didefinisikan oleh local minima adalah 0 (tidak boleh ada envelope yang didefinisikan
# oleh local minima)


