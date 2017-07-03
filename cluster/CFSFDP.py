from common.gps import gps_dist_matrix

class CFSFDP():
    def __init__(self):
        pass

    def fit(self, data):
        gps = data[:,[0,1]]
        density = data[:,2]
        disMat = gps_dist_matrix(data)



