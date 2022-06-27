"""
raw_adc_traces.py: template for acquiring raw ADC traces from inputs 1 and 2
"""

from qm.qua import *
from qm.QuantumMachinesManager import QuantumMachinesManager
from configuration import *
import matplotlib.pyplot as plt
import numpy as np


##############################
# Program-specific variables #
##############################
n_avg = 100  # Number of averaging loops
cooldown_time = 2000 // 4  # Resonator cooldown time in clock cycles (4ns)

###################
# The QUA program #
###################
with program() as raw_trace_prog:
    n = declare(int)
    adc_st = declare_stream(adc_trace=True)

    with for_(n, 0, n < n_avg, n + 1):
        play("const" * amp(0), "flux_line")
        reset_phase("resonator")
        measure("readout", "resonator", adc_st)
        wait(cooldown_time, "resonator")

    with stream_processing():
        # Will save average:
        adc_st.input1().average().save("adc1")
        adc_st.input2().average().save("adc2")
        # Will save only last run:
        adc_st.input1().save("adc1_single_run")
        adc_st.input2().save("adc2_single_run")

#####################################
#  Open Communication with the QOP  #
#####################################
qmm = QuantumMachinesManager(qop_ip)

qm = qmm.open_qm(config)
job = qm.execute(raw_trace_prog)
res_handles = job.result_handles
res_handles.wait_for_all_values()
adc1 = res_handles.get("adc1").fetch_all() / 2**12
adc2 = res_handles.get("adc2").fetch_all() / 2**12
adc1_single_run = res_handles.get("adc1_single_run").fetch_all() / 2**12
adc2_single_run = res_handles.get("adc2_single_run").fetch_all() / 2**12

plt.figure()
plt.title("Single run (Check ADCs saturation)")
plt.plot(adc1_single_run)
plt.plot(adc2_single_run)

plt.figure()
plt.title("Averaged run")
plt.plot(adc1)
plt.plot(adc2)

print(f"\nInput1 mean: {np.mean(adc1)} V\n" f"Input2 mean: {np.mean(adc2)} V")
