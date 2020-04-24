# TIMEBOMB: report me
a = 1  # TIMEBOMB (jsmith): report me
# TIMEBOMB: do not report me (pragma). # no-check-fixmes
# TIMEBOMB(jsmith - 2020-04-25): report me
a = "TIMEBOMB"  # do not report me (within a string)
a = "TIMEBOMB"  # do not report me (within a string)

# TIMEBOMB - FEWTURE-BOOM: report me
