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
import math



# start_time = time.time()
# f = open('data/108_350_400.csv', 'r')
# lines = f.readlines()
# f.close()
def main_test(lines,fig,data_title,signal_type,file_result):
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
    plt.plot(range(len(ecg_adp)),ecg_adp)
    plt.title('Derivative Result')

    #___________________________________________2.1 FEATURE EXTRACTION__________________________________________________
    # colors = plt.cm.rainbow(len(sample))
    sampled_window = len_sample
    sample = []
    for i in range(sampled_window):
        sample.append(ecg_adp[i-1])
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

# 3. Calculate RR Interval & SET P Q S T peak
    print "Total R peaks : ", len(r_peaks)

    print r_peaks
    rr_list = []
    pr_list = []
    qrs_list = []
    qt_list = []
    qt_corr = []
    bpm_list = []
    fs = 360
    # LOOPING TO GAIN PQST PEAK AND IT'S INTERVAL
    for i in range(len(r_peaks) - 1):
        r1 = r_peaks[i][0]
        r2 = r_peaks[i + 1][0]
        rr = r2 - r1
        rr_list.append(rr)
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
        print "T Peak   : ", t_in

        # SET P
        p_on  = (35 * rr)/100
        p_on  = r1 - p_on
        p_off = (5 * rr)/100
        p_off = r1 - p_off
        print "P onset  : ", p_on
        print "P offset : ", p_off
        # plt.axvspan(p_on, p_off, facecolor='#ff9999', alpha=0.5)

        t = p_on; t_list = []
        while(t <= p_off):
            t_list.append(sample[t])
            t += 1
        p_peak = max(t_list)
        p_in   = sample.index(p_peak)
        p_plot = plt.plot(p_in, p_peak, 'b.', markersize=8) #Plot the P peak
        print "P Peak   : ", p_in

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
        s_plot = plt.plot(s_in, s_peak, 'y.', markersize=8) #Plot the S peak
        print "S Peak   : ", s_in

        # SET Q
        q_on  = (5 * rr)/100
        q_on  = r1 - q_on
        q_off = r1
        print "Q onset  : ", q_on
        print "Q offset : ", q_off
        # plt.axvspan(q_on, q_off, facecolor='#ffffff', alpha=0.5)

        t = q_on; t_list = []
        while(t <= q_off):
            t_list.append(sample[t])
            t += 1
        q_peak = min(t_list)
        q_in   = sample.index(q_peak)
        q_plot = plt.plot(q_in, q_peak, 'r.', markersize=8) #Plot the Q peak
        print "Q Peak   : ", q_in


        # 4. ECG Timing Intervals Calculations
        # PR Interval
        t_pr = (r1 - p_in)/fs
        pr_list.append(t_pr)
        print "PR Interval : ", t_pr

        # QRS Duration
        x = (6.65/100)*rr
        t_qrs = ((s_in + x)-(q_in - x))/fs
        qrs_list.append(t_qrs)
        print "QRS Duration : ", t_qrs

        #QT Interval
        t_qt = (t_in + (rr * 0.13) - (q_in - x))/fs
        qt_list.append(t_qt)
        print "QT Interval : ", t_qt

        #QT Corrected
        t_qt_corr = t_qt / (fs * math.sqrt(rr))
        qt_corr.append(t_qt_corr)
        print "QT Corrected : ", t_qt_corr

        #Vent Rate
        bpm = (fs/rr)*60
        bpm_list.append(bpm)
        print "BPM : ", bpm
    # END LOOPING TO GAIN PQST PEAK AND IT'S INTERVAL

    # LOOPING TO GAIN PQST INTERVAL MEAN
    print "======= INTERVALS ==========="
    print rr_list, len(rr_list)
    rr_temp = 0; pr_temp = 0 ; qrs_temp = 0; qt_temp = 0; qtcorr_temp = 0; bpm_temp = 0
    for k in range(len(rr_list)):
        rr_temp     = rr_temp + rr_list[k]
        pr_temp     = pr_temp + pr_list[k]
        qrs_temp    = qrs_temp + qrs_list[k]
        qt_temp     = qt_temp + qt_list[k]
        qtcorr_temp = qtcorr_temp + qt_corr[k]
        bpm_temp    = bpm_temp + bpm_list[k]

    qtcorr_mean = float(qtcorr_temp)/float(len(qt_corr))
    rr_mean     = float(rr_temp)/float(len(rr_list))
    print "RR Mean  : ", rr_mean
    print "PR Mean  : ", float(pr_temp)/float(len(pr_list))
    print "QRS Mean : ", float(qrs_temp)/float(len(qrs_list))
    print "QT Mean  : ", float(qt_temp)/float(len(qt_list))
    print "QT Corr Mean : ", qtcorr_mean
    print "BPM Mean : ", float(bpm_temp)/float(len(bpm_list))
    # END LOOPING TO GAIN PQST INTERVAL MEAN


    #Detection by QT Correction
    message = ""
    for j in range(len(qt_corr)):
        if(qt_corr[j] < qtcorr_mean ):
            message = "Ventricular Arrhytmia Detected"
        else:
            message = "Normal"
        print "============= MESSAGE ==========="
        print message


    #DETECTION PREMATURITY & COMPENSATORY PAUSE (PEDRO2014)
    print "============= CLASSIFICATION : PEDRO 2014 ==========="

    for i in range(len(rr_list)):
        prematurity = float(rr_mean - rr_list[i])/float(rr_mean)
        print "Prematurity ",i+1," : ", prematurity

        if(i+1 < len(rr_list)):
            compensatory_pause = float(rr_list[i+1] - rr_mean)/float(rr_mean)
            print "Compensatory ",i+1," : ", compensatory_pause

        if(prematurity > 0):
            message = "Ventricular Arrhytmia Detected"
        else:
            message = "Normal"
        print message
        file_result.write(message)
        file_result.write("\n")
    file_result.close()
