import pandas
import matplotlib.pyplot as plt

df = pandas.read_csv('/home/mvacanti/External_Repos/bldc_validation/PX4-Autopilot/Tools/jsbsim_bridge/prop_perf.csv')

df['ind_total_prop_torque'] = ( df['/fdm/jsbsim/propulsion/engine/prop_torque_ftlbs'] +
                                df['/fdm/jsbsim/propulsion/engine[1]/prop_torque_ftlbs'] +
                                df['/fdm/jsbsim/propulsion/engine[2]/prop_torque_ftlbs'] +
                                df['/fdm/jsbsim/propulsion/engine[3]/prop_torque_ftlbs'] +
                                df['/fdm/jsbsim/propulsion/engine[4]/prop_torque_ftlbs'] +
                                df['/fdm/jsbsim/propulsion/engine[5]/prop_torque_ftlbs'] ) * -1

df['expected_N_Total'] = ( df['/fdm/jsbsim/propulsion/engine/prop_torque_ftlbs'] +
                                df['/fdm/jsbsim/propulsion/engine[1]/prop_torque_ftlbs'] +
                                df['/fdm/jsbsim/propulsion/engine[2]/prop_torque_ftlbs'] +
                                df['/fdm/jsbsim/propulsion/engine[3]/prop_torque_ftlbs'] +
                                df['/fdm/jsbsim/propulsion/engine[4]/prop_torque_ftlbs'] +
                                df['/fdm/jsbsim/propulsion/engine[5]/prop_torque_ftlbs'] ) * -1 * 2.53


plt.figure(figsize=(11, 8.5))
plt.plot(df['Time'], df['N_{Total} (ft-lbs)'], label='JSBSim N Total ')
plt.plot(df['Time'], df['ind_total_prop_torque'], label='Indepedent Total Prop Torque')
plt.plot(df['Time'], df['expected_N_Total'], label='Expected N Total')
plt.xlabel("Time (Seconds)")
plt.ylabel("Ft-Lbs")
plt.title("JSBSim Time vs. Ft - Lbs")
plt.legend(title='Source')
#plt.show()
plt.savefig('/home/mvacanti/yaw_test.png')
plt.close()