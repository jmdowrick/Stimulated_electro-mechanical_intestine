import numpy as np
from src.assets.cellml import imtiaz_2002d_noTstart_COR as model
import matplotlib.pyplot as plt

# Import python form of model
rhs = model.rhs
states = model.init_state_values()
parameters = model.init_parameter_values()

dt = 0.1
times = np.arange(0, 100000, dt)
all_states = np.zeros((len(times), len(states)))

for i, t in enumerate(times):
    all_states[i, :] = states
    states += rhs(t, states, parameters)*dt

fig, ax = plt.subplots(2, 1, sharex=True)
ax[0].plot(times, all_states[:, 3], times, all_states[:, 4])
ax[0].set_ylabel("Ca_s")
ax[1].plot(times, all_states[:, 5])
ax[1].set_ylabel("V_m")
ax[1].set_xlabel("Time")
plt.show()