# ________________________________________DATA DESCRIPTION______________________________________________________________
# MIT BIH DATABASE : PVC Record
# 102_930_940.csv => record ke 102, V5 & V2, durasi 9:30 - 9:40, PVC detected on beat- 9
# 105_010_020.csv => record ke 105, MLII & V1, durasi 0:10 - 0:20, PVC detected on beat- 8
# 108_450_500.csv => record ke 108, MLII, durasi 4:50 - 5:00, PVC on beat- 9
# 108_350_400.csv => record ke 108, MLII, durasi 3:50 - 4:00, PVC on beat- 3
# ______________________________________________________________________________________________________________________
import time
import matplotlib.pyplot as plt
import filtering as filt


# start_time = time.time()
# f = open('data/108_350_400.csv', 'r')
# lines = f.readlines()
# f.close()
def main_test(lines,fig,data_title,signal_type):
    # Discard the first two lines because of header. Takes either column 1 or 2 from each lines (different signal lead)
    raw_signal = [0]*(len(lines)-2)
    for i in xrange(len(raw_signal)):
        raw_signal[i] = float(lines[i+2].split(',')[signal_type]) #0 for realtime signal #1 for MLII signal #2 for V signal
    plt.figure(fig)
    plt.subplot(311); plt.tight_layout()
    plt.title('Raw signal '+data_title)
    plt.plot(range(len(raw_signal)),raw_signal)
    len_sample = len(raw_signal)
    #___________________________________________2.1 ECG FILTERING___________________________________________________________

    ecg_der = filt.five_point_derivative(raw_signal)
    ecg_adp = filt.adaptive_filter(ecg_der)

    # print ecg_adp
    # print "Derivative result : ", ecg_der
    plt.subplot(312); plt.tight_layout()
    plt.plot(range(len(ecg_der)),ecg_der)
    plt.title('Derivative Result')

    #___________________________________________2.1 FEATURE EXTRACTION__________________________________________________
    # colors = plt.cm.rainbow(len(sample))
    sampled_window = len_sample
    sample = []
    for i in range(sampled_window):
        sample.append(ecg_adp[i])
    # plt.figure(fig+1)
    plt.subplot(313); plt.tight_layout()
    plt.plot(range(len(sample)),sample)
    plt.title('Sample Data')

    # 1. IDENTIFY R PEAKS
    MAX = max(sample);

    # 2. Obtain a threshold such that: Threshold t = (0.4) * MAX
    R = 0.4 * MAX
    list_upper = []; r_peaks = []
    for i in range(sampled_window - 1):
        if(sample[i] > R):
            #first upper
            if(len(list_upper) == 0):
                list_upper.append(sample[i])
            else:
                list_upper.append(sample[i])
                if(sample[i+1] < R):
                    find_r = max(list_upper)
                    find_r_in = sample.index(find_r)
                    r_plot = plt.plot(find_r_in, find_r, 'r.', markersize=8) #Plot the maximum peak
                    r_detect = [find_r_in, find_r]
                    r_peaks.append(r_detect)
                    list_upper = []

    # 3. Calculate RR Interval & SET PQST peak
    print "Total R peaks : ", len(r_peaks)

    print r_peaks
    for i in range(len(r_peaks) - 1):
        r1 = r_peaks[i][0]
        r2 = r_peaks[i + 1][0]
        rr = r2 - r1
        print "======= Beat ", i + 1, " to Beat ",i+2, " ========="
        print "R1 : ", r1
        print "R2 : ", r2
        print "RR Interval : ", rr
        # SET T
        t_on  = (15 * rr)/100
        t_on  = t_on + r1
        t_off = (55 * rr)/100
        t_off = t_off + r1
        print "T onset  : ", t_on
        print "T offset : ", t_off
        # plt.axvspan(t_on, t_off, facecolor='#f9ff4f', alpha=0.5)

        t = t_on; t_list = []
        while(t <= t_off):
            t_list.append(sample[t])
            t += 1
        t_peak = max(t_list)
        t_in   = sample.index(t_peak)
        t_plot = plt.plot(t_in, t_peak, 'g.', markersize=8) #Plot the T peak
        print "T Peak   : ", t_peak

        # SET P
        p_on  = (65 * rr)/100
        p_on  = p_on + r1
        p_off = (95 * rr)/100
        p_off = p_off + r1
        print "P onset  : ", p_on
        print "P offset : ", p_off
        # plt.axvspan(p_on, p_off, facecolor='#ff9999', alpha=0.5)

        t = p_on; t_list = []
        while(t <= p_off):
            t_list.append(sample[t])
            t += 1
        p_peak = max(t_list)
        p_in   = sample.index(p_peak)
        p_plot = plt.plot(p_in, p_peak, 'b.', markersize=8) #Plot the T peak
        print "P Peak   : ", p_peak

        # SET S
        s_on  = r1
        s_off = t_off
        print "S onset  : ", s_on
        print "S offset : ", s_off
        # plt.axvspan(s_on, s_off, facecolor='#beff9b', alpha=0.5)

        t = s_on; t_list = []
        while(t <= s_off):
            t_list.append(sample[t])
            t += 1
        s_peak = min(t_list)
        s_in   = sample.index(s_peak)
        s_plot = plt.plot(s_in, s_peak, 'y.', markersize=8) #Plot the T peak
        print "S Peak   : ", s_peak

        # SET Q
        q_on  = p_off
        q_off = r2
        print "Q onset  : ", q_on
        print "Q offset : ", q_off
        # plt.axvspan(q_on, q_off, facecolor='#ffffff', alpha=0.5)

        t = q_on; t_list = []
        while(t <= q_off):
            t_list.append(sample[t])
            t += 1
        q_peak = min(t_list)
        q_in   = sample.index(q_peak)
        q_plot = plt.plot(q_in, q_peak, 'r.', markersize=8) #Plot the T peak
        print "Q Peak   : ", q_peak
