from luminol.anomaly_detector import AnomalyDetector

ts = {0: 0, 1: 0.5, 2: 1, 3: 1, 4: 1, 5: 0, 6: 8, 7: 0, 8: 0}

my_detector = AnomalyDetector(ts, score_threshold=1.5)
score = my_detector.get_all_scores()
for timestamp, value in score.iteritems():
    print(timestamp, value)

""" Output:
0 0.0
1 0.873128250131
2 1.57163085024
3 2.13633686334
4 1.70906949067
5 2.90541813415
6 1.17154110935
7 0.937232887479
8 0.749786309983
"""

anoms = my_detector.get_anomalies()
result = list()
for anom in anoms:
    entry = list()
    anom_dict = anom.__dict__
    for key in anom_dict:
        entry.append(anom_dict[key])
    result.append(entry)
for r in result:
    print(r)
