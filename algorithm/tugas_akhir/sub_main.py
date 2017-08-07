import matplotlib.pyplot as plt
import math
import filtering as filt
import cls_pedro, cls_windowing
import bwr

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

    (baseline, raw_signal) = bwr.bwr(raw_signal)
    # raw_signal = filt.butter_highpass_filter(raw_signal, 0.25, 260)
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

    rr_list = []
    pr_list = []
    pq_list = []
    qrs_list = []
    qt_list = []
    qt_corr = []
    bpm_list = []
    st_level_list = []
    fs = 360
    # LOOPING TO GAIN PQST PEAK AND IT'S INTERVAL
    for i in range(len(r_peaks) - 1):
        r1 = r_peaks[i][0]
        r2 = r_peaks[i + 1][0]
        rr = r2 - r1
        rr_list.append(rr)
        # print "======= Beat ", i + 1, " to Beat ",i+2, " ========="
        # print "R1 : ", r1
        # print "R2 : ", r2
        # print "RR Interval : ", rr

        # T-wave in one R-R interval is selected by starting from 15% of the R-R interval added to the 1st R-peak location
        # and continuing to 55% of the R-R interval added
        t_on  = (15 * rr)/100
        t_on  = t_on + r1
        t_off = (55 * rr)/100
        t_off = t_off + r1
        # print "T onset  : ", t_on, " | offset : ", t_off
        # plt.axvspan(t_on, t_off, facecolor='#f9ff4f', alpha=0.5)
        t = t_on; t_list = []
        while(t <= t_off):
            t_list.append(sample[t])
            t += 1
        t_peak = max(t_list)
        t_in   = sample.index(t_peak)
        plt.plot(t_in, t_peak, 'g.', markersize=8) #Plot the T peak
        # print "T Peak   : ", t_in

        # P-wave in one R-R interval is selected by starting from 65% of the R-R interval added to
        # the 1st R-peak location and continuing to 95% of the R-R interval added to the same location
        p_on  = (35 * rr)/100
        p_on  = r2 - p_on
        p_off = (5 * rr)/100
        p_off = r2 - p_off
        # print "P onset  : ", p_on, " | offset : ", p_off
        # plt.axvspan(p_on, p_off, facecolor='#ff9999', alpha=0.5)
        p = p_on; p_list = []
        while(p <= p_off):
            p_list.append(sample[p])
            p += 1
        p_peak = max(p_list)
        p_in   = sample.index(p_peak)
        p_plot = plt.plot(p_in, p_peak, 'r.', markersize=8) #Plot the P peak
        # print "P Peak   : ", p_in

        # Q-peak is chosen by selecting minimum value in the window starting from 20 ms before
        # the corresponding R-peak and that particular R-peak
        q_on  = (5 * rr)/100
        q_on  = r2 - q_on
        q_off = r2
        # print "Q onset  : ", q_on, " | offset : ", q_off
        # plt.axvspan(q_on, q_off, facecolor='#ffffff', alpha=0.5)
        q = q_on; q_list = []
        while(q <= q_off):
            q_list.append(sample[q])
            q += 1
        q_peak = min(q_list)
        q_in   = sample.index(q_peak)
        plt.plot(q_in, q_peak, 'b.', markersize=8) #Plot the Q peak
        # print "Q Peak   : ", q_in

        # S-peak is chosen by selecting the lowest value in the window starting from R-peak to 20 ms after that R-peak.
        s_on  = r1
        s_off = t_on
        # print "S onset  : ", s_on, " | offset : ", s_off
        # plt.axvspan(s_on, s_off, facecolor='#beff9b', alpha=0.5)
        s = s_on; s_list = []
        while(s <= s_off):
            s_list.append(sample[s])
            s += 1
        s_peak = min(s_list)
        s_in   = sample.index(s_peak)
        plt.plot(s_in, s_peak, 'y.', markersize=8) #Plot the S peak
        # print "S Peak   : ", s_in

        # 4. ECG Timing Intervals Calculations
        # PR Interval
        t_pr = (r1 - p_in)/fs
        pr_list.append(t_pr)
        # print "PR Interval : ", t_pr

        # QRS Duration
        x = (6.65/100)*rr
        t_qrs = ((s_in + x)-(q_in - x))/fs
        qrs_list.append(t_qrs)
        # print "QRS Duration : ", t_qrs

        #QT Interval
        t_qt = (t_in + (rr * 0.13) - (q_in - x))/fs
        qt_list.append(t_qt)
        # print "QT Interval : ", t_qt

        #QT Corrected
        t_qt_corr = t_qt / (fs * math.sqrt(rr))
        qt_corr.append(t_qt_corr)
        # print "QT Corrected : ", t_qt_corr

        #Vent Rate
        bpm = (fs/rr)*60
        bpm_list.append(bpm)
        # print "BPM : ", bpm

        # #PQ Interval
        t_pq = q_in - p_in
        pq_list.append(t_pq)
        # print "PQ Interval : ", t_pq

        if(q_in != p_in):
            print "p exist"
        else:
            print "p absence", i + 2
    # END LOOPING TO GAIN PQST PEAK AND IT'S INTERVAL

    # LOOPING TO GAIN PQST INTERVAL MEAN
    print "======= INTERVALS ==========="
    rr_temp = 0; pr_temp = 0 ; qrs_temp = 0; qt_temp = 0; qtcorr_temp = 0; bpm_temp = 0; st_level = 0; pq_temp = 0;
    for k in range(len(rr_list)):
        rr_temp     = rr_temp + rr_list[k]
        pr_temp     = pr_temp + pr_list[k]
        qrs_temp    = qrs_temp + qrs_list[k]
        qt_temp     = qt_temp + qt_list[k]
        qtcorr_temp = qtcorr_temp + qt_corr[k]
        bpm_temp    = bpm_temp + bpm_list[k]
        # st_level    = st_level + st_level_list[k]
        pq_temp     = pq_temp + pq_list[k]

    qtcorr_mean = float(qtcorr_temp)/float(len(qt_corr))
    rr_mean     = float(rr_temp)/float(len(rr_list))
    # st_mean     = float(st_level)/float(len(st_level_list))
    pq_mean     = float(pq_temp)/float(len(pq_list))
    print "RR Mean  : ", rr_mean
    print "PR Mean  : ", float(pr_temp)/float(len(pr_list))
    print "QRS Mean : ", float(qrs_temp)/float(len(qrs_list))
    print "QT Mean  : ", float(qt_temp)/float(len(qt_list))
    print "QT Corr Mean : ", qtcorr_mean
    print "BPM Mean : ", float(bpm_temp)/float(len(bpm_list))
    print "PQ Mean  : ", pq_mean
    # print "ST Level Mean : ", float(st_level)/float(len(st_level_list))
    # END LOOPING TO GAIN PQST INTERVAL MEAN



    #_______________________________________________2.2 CLASSIFICATION__________________________________________________

    # cls_windowing.main(qt_corr,qtcorr_mean,file_result);
    # cls_pedro.main(rr_list,rr_mean,file_result);

    # Detect by shorter PQ interval
    for k in range(len(pq_list)):
        if(pq_list[k] < pq_mean):
            print "Shorter P - Q Interval ", k
