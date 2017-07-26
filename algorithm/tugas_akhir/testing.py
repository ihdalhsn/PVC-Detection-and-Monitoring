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

start_time = time.time()
f = open('data/husna3.csv', 'r')
lines = f.readlines()
f.close()

# Discard the first two lines because of header. Takes either column 1 or 2 from each lines (different signal lead)
raw_signal = [0]*(len(lines)-2)
for i in xrange(len(raw_signal)):
	raw_signal[i] = float(lines[i+2].split(',')[0]) #1 for MLII signal
print "==================================="
plt.figure(1)
plt.subplot(311); plt.tight_layout()
plt.title('Raw signal')
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
# Derivate action : H(z) = 0.1*(2+z^-1 - z^-2 - z^-3)
ecg_der = []
for i in xrange(len(raw_signal)):
        der = 0.1 * 2 * (raw_signal[i] + raw_signal[i-1] - raw_signal[i-3] - raw_signal[i-4])
        ecg_der.append(der)

print ecg_der
plt.subplot(312); plt.tight_layout()
plt.plot(range(len(ecg_der)),ecg_der)
plt.title('Derrivative Data')

# Adaptive Filter
ecg_adp = []; a = 0.95;
ecg_adp.append(0.01);
for i in xrange(len(ecg_der)):
        adp = ( a * ecg_adp[i-1] ) + ( (1 - a) * ecg_der[i])
        ecg_adp.append(adp)

print ecg_adp
plt.subplot(313); plt.tight_layout()
plt.plot(range(len(ecg_adp)),ecg_adp)
plt.title('Adaptive Filter')

#___________________________________________2.1 FEATURE EXTRACTION______________________________________________________
sampled_window = 3600
sample = []
for i in range(sampled_window):
        sample.append(ecg_adp[i])
plt.figure(2)
plt.subplot(311); plt.tight_layout()
plt.plot(range(len(sample)),sample)
plt.title('Sample Data')
# 1. Search for a maximum value within the sampled window which represents one of the R peaks (MAX)
MAX = max(sample);
in_max = sample.index(MAX)
plt.plot(in_max, MAX, 'r.', markersize=8)
# 2. Search for a minimum value within the sampled window which represents one of S peaks (MIN)
MIN = min(sample)
in_min = sample.index(MIN)
plt.plot(in_min, MIN, 'g.', markersize=8)
# 3. Obtain a threshold such that: Threshold R = MAX/2 and threshold S = MIN/2
R = MAX/2
S = MIN/2
plt.axhline(y=S, color='#ef796e')
Q = R/10
plt.axhline(y=Q)
Q_2 = Q*3
plt.axhline(y=Q_2)
# 4. Find Ri peaks overall the sampled window which should be above threshold R
list_peaks_index = []
s_points = []
# while(i <= sampled_window):
for i in range(sampled_window):
        upper = False
        if( sample[i] > R ):
                if( sample[i] > sample[i-1] and sample[i] > sample[i+1]): #is peak
                        real_peak = max(sample[i],sample[i+10]);
                        real_peak_2 = max(sample[i],sample[i-10]);
                        if(sample[i] == real_peak and sample[i] == real_peak_2):
                            # plt.axvspan(i-60, i+25, facecolor='#2ca02c', alpha=0.2)
                            plt.plot(i, sample[i], 'g.', markersize=8)
                            list_peaks_index.append(i)
                            i+=10
                        # 5. For each Ri, create a sub-window [Ri to Ri+10]
                        # (S peaks appear normally after the R peaks by a few samples) samples to search for S peaks which should be
                        # below threshold S
                        win_s = 15 #coba di threshold : hitung rata2 jarak R-S dibagi dengan jumlah diferensiasi jarak tsb
                        s = i + win_s
                        for j in range(i, s):
                                if(sample[j] < S):
                                        if( sample[j] < sample[j-1] and sample[j] < sample[j+1]):
                                                plt.axvspan(i, i+win_s, facecolor='#2ca02c', alpha=0.2)
                                                plt.plot(j, sample[j], 'r.', markersize=8)
                        q = i - 100;
                        for j in range(q, i-25):
                                if(sample[j] > Q and sample[j] < Q_2):
                                        if( sample[j] < sample[j-1] and sample[j] < sample[j+1]):
                                                plt.axvspan(i-100, i-25, facecolor='#99c0ff', alpha=0.2)
                                                plt.plot(j, sample[j], 'r.', markersize=8)
print s_points
peaks = len(list_peaks_index) - 1
for i in range(peaks):
        diff = list_peaks_index[i+1] - list_peaks_index[i]
        print diff
        if(diff > 350):
                print "PVC detected on beat ", i+1

print "max: ", sample.index(max(sample[1023],sample[1031]))

print "====== TEST FOR ========"
mylist = [123,2345,345]
print mylist, len(mylist)
mylist = []
fact = len(mylist) == 0
print mylist, len(mylist), fact


# _________________________________________________ESTIMATED TIME_______________________________________________________
print "============= RESPON TIME ============================="
end_time      = time.time()
response_time = end_time - start_time
print "Time : " + str(response_time) + " seconds"
plt.show()


