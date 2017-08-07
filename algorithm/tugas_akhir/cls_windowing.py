#DETECTION BY QT CORRECTION (NOVELWINDOWING2014)
def main(qt_corr,qtcorr_mean,file_result):
    count_normal = 0
    count_pvc    = 0
    for j in range(len(qt_corr)):
        if(qt_corr[j] < qtcorr_mean ):
            message = "PVC Detected"
            count_pvc += 1
        else:
            message = "Normal"
            count_normal += 1
        # print "============= MESSAGE ==========="
        # print message
    file_result.write("====== Novel Windowing Algorithm 2014 ======\n")
    file_result.write("Normal beat : "+ str(count_normal)+"\n")
    file_result.write("PVC beat : "+ str(count_pvc)+"\n")
    print "============= RESULT WINDOWING =============="
    print "Normal beat : "+ str(count_normal)
    print "PVC beat : "+ str(count_pvc)
