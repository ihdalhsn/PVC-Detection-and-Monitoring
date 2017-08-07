#DETECTION PREMATURITY & COMPENSATORY PAUSE (PEDRO2014)
def main(rr_list,rr_mean,file_result):
    print "============= CLASSIFICATION : PEDRO 2014 ==========="
    count_normal = 0
    count_pvc    = 0
    for i in range(len(rr_list)):
        prematurity = float(rr_mean - rr_list[i])/float(rr_mean)
        print "Prematurity ",i+1," : ", prematurity

        if(i+1 < len(rr_list)):
            compensatory_pause = float(rr_list[i+1] - rr_mean)/float(rr_mean)
            print "Compensatory ",i+1," : ", compensatory_pause

        if(prematurity > 0 and compensatory_pause < 0):
            message = "PVC Detected"
            count_pvc += 1
        else:
            message = "Normal"
            count_normal += 1
        # print message
    file_result.write("====== PEDRO 2014 ======\n")
    file_result.write("Normal beat : "+ str(count_normal) +"\n")
    file_result.write("PVC beat : "+ str(count_pvc) +"\n")
    print "============= RESULT PEDRO =============="
    print "Normal beat : "+ str(count_normal)
    print "PVC beat : "+ str(count_pvc)
