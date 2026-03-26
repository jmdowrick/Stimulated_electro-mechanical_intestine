import numpy

parameter = {
    "C_m": 0,
    "Cor": 1,
    "E_Ca": 2,
    "E_K": 3,
    "E_Na": 4,
    "G_MCa": 5,
    "G_Na": 6,
    "G_max_BK": 7,
    "I_stim": 8,
    "K": 9,
    "P_MV": 10,
    "V_0": 11,
    "V_1": 12,
    "V_M2": 13,
    "V_M3": 14,
    "V_M4": 15,
    "beta_": 16,
    "eta": 17,
    "k_2": 18,
    "k_4": 19,
    "k_Ca": 20,
    "k_a": 21,
    "k_f": 22,
    "k_p": 23,
    "k_r": 24,
    "k_v": 25,
    "m": 26,
    "n": 27,
    "o": 28,
    "q": 29,
    "r": 30,
    "tau_d_Na": 31,
    "tau_f_Na": 32,
    "u": 33,
    "w": 34,
}


def parameter_index(name: str) -> int:
    """Return the index of the parameter with the given name

    Arguments
    ---------
    name : str
        The name of the parameter

    Returns
    -------
    int
        The index of the parameter

    Raises
    ------
    KeyError
        If the name is not a valid parameter
    """

    return parameter[name]


state = {"IP_3": 0, "d_Na_d_Na": 1, "f_Na_f_Na": 2, "Ca_s": 3, "Ca_c": 4, "V_m": 5}


def state_index(name: str) -> int:
    """Return the index of the state with the given name

    Arguments
    ---------
    name : str
        The name of the state

    Returns
    -------
    int
        The index of the state

    Raises
    ------
    KeyError
        If the name is not a valid state
    """

    return state[name]


monitor = {
    "G_Ca": 0,
    "d_BK_d_BK": 1,
    "d_inf_Na": 2,
    "f_inf_Na": 3,
    "I_Na": 4,
    "V_2": 5,
    "V_3": 6,
    "V_in": 7,
    "dIP_3_dt": 8,
    "I_Ca": 9,
    "I_BK": 10,
    "dd_Na_d_Na_dt": 11,
    "df_Na_f_Na_dt": 12,
    "dCa_s_dt": 13,
    "dCa_c_dt": 14,
    "dV_m_dt": 15,
}


def monitor_index(name: str) -> int:
    """Return the index of the monitor with the given name

    Arguments
    ---------
    name : str
        The name of the monitor

    Returns
    -------
    int
        The index of the monitor

    Raises
    ------
    KeyError
        If the name is not a valid monitor
    """

    return monitor[name]


def init_parameter_values(**values):
    """Initialize parameter values"""
    # C_m=26.0, Cor=2.0, E_Ca=-20.0, E_K=-72.0, E_Na=80.0, G_MCa=4.0
    # G_Na=28.0, G_max_BK=1.2, I_stim=0.0, K=0.0006435, P_MV=0.0325
    # V_0=0.0002145, V_1=0.00022094, V_M2=0.0049, V_M3=0.3224
    # V_M4=0.0004875, beta_=0.000975, eta=0.0389, k_2=1.0, k_4=0.5
    # k_Ca=0.94, k_a=0.9, k_f=5.85e-05, k_p=0.65, k_r=2.0
    # k_v=-68.0, m=4.0, n=2.0, o=4.0, q=4.0, r=8.0, tau_d_Na=10.26
    # tau_f_Na=112.82, u=4.0, w=4.0

    parameters = numpy.array(
        [
            26.0,
            2.0,
            -20.0,
            -72.0,
            80.0,
            4.0,
            28.0,
            1.2,
            0.0,
            0.0006435,
            0.0325,
            0.0002145,
            0.00022094,
            0.0049,
            0.3224,
            0.0004875,
            0.000975,
            0.0389,
            1.0,
            0.5,
            0.94,
            0.9,
            5.85e-05,
            0.65,
            2.0,
            -68.0,
            4.0,
            2.0,
            4.0,
            4.0,
            8.0,
            10.26,
            112.82,
            4.0,
            4.0,
        ],
        dtype=numpy.float64,
    )

    for key, value in values.items():
        parameters[parameter_index(key)] = value

    return parameters


def init_state_values(**values):
    """Initialize state values"""
    # IP_3=0.3791, d_Na_d_Na=0, f_Na_f_Na=0.9997, Ca_s=2.0014
    # Ca_c=0.2886, V_m=-70.5156

    states = numpy.array(
        [0.3791, 0, 0.9997, 2.0014, 0.2886, -70.5156], dtype=numpy.float64
    )

    for key, value in values.items():
        states[state_index(key)] = value

    return states


def rhs(t, states, parameters):

    # Assign states
    IP_3 = states[0]
    d_Na_d_Na = states[1]
    f_Na_f_Na = states[2]
    Ca_s = states[3]
    Ca_c = states[4]
    V_m = states[5]

    # Assign parameters
    C_m = parameters[0]
    Cor = parameters[1]
    E_Ca = parameters[2]
    E_K = parameters[3]
    E_Na = parameters[4]
    G_MCa = parameters[5]
    G_Na = parameters[6]
    G_max_BK = parameters[7]
    I_stim = parameters[8]
    K = parameters[9]
    P_MV = parameters[10]
    V_0 = parameters[11]
    V_1 = parameters[12]
    V_M2 = parameters[13]
    V_M3 = parameters[14]
    V_M4 = parameters[15]
    beta_ = parameters[16]
    eta = parameters[17]
    k_2 = parameters[18]
    k_4 = parameters[19]
    k_Ca = parameters[20]
    k_a = parameters[21]
    k_f = parameters[22]
    k_p = parameters[23]
    k_r = parameters[24]
    k_v = parameters[25]
    m = parameters[26]
    n = parameters[27]
    o = parameters[28]
    q = parameters[29]
    r = parameters[30]
    tau_d_Na = parameters[31]
    tau_f_Na = parameters[32]
    u = parameters[33]
    w = parameters[34]

    # Assign expressions

    values = numpy.zeros_like(states, dtype=numpy.float64)
    G_Ca = (Ca_c**q * G_MCa) / (Ca_c**q + k_Ca**q)
    d_BK_d_BK = 1.0 / (1e-06 * Ca_c ** (-2.0) * numpy.exp(V_m / ((17.0 * (-1)))) + 1.0)
    d_inf_Na = 1.0 / (numpy.exp((V_m + 7.0) / ((5.0 * (-1)))) + 1.0)
    f_inf_Na = 1.0 / (numpy.exp((V_m + 37.4) / 4.0) + 1.0)
    I_Na = (d_Na_d_Na * (G_Na * f_Na_f_Na)) * (-E_Na + V_m)
    V_2 = (Ca_c**n * V_M2) / (Ca_c**n + k_2**n)
    V_3 = (
        IP_3**o
        * ((Ca_s**m * ((Ca_c**w * V_M3) / (Ca_c**w + k_a**w))) / (Ca_s**m + k_r**m))
    ) / (IP_3**o + k_p**o)
    V_in = IP_3 * V_1 + V_0
    dIP_3_dt = Cor * (
        P_MV * (1.0 - V_m**r / (V_m**r + k_v**r))
        + (((-(IP_3**u)) * V_M4) / (IP_3**u + k_4**u) + ((-IP_3) * eta + beta_))
    )
    values[0] = dIP_3_dt
    I_Ca = G_Ca * (-E_Ca + V_m)
    I_BK = (G_max_BK * d_BK_d_BK) * (-E_K + V_m)
    dd_Na_d_Na_dt = (Cor * (-d_Na_d_Na + d_inf_Na)) / tau_d_Na
    values[1] = dd_Na_d_Na_dt
    df_Na_f_Na_dt = (Cor * (-f_Na_f_Na + f_inf_Na)) / tau_f_Na
    values[2] = df_Na_f_Na_dt
    dCa_s_dt = Cor * ((-Ca_s) * k_f + (V_2 - V_3))
    values[3] = dCa_s_dt
    dCa_c_dt = Cor * ((-Ca_c) * K + (Ca_s * k_f + (V_3 + (-V_2 + V_in))))
    values[4] = dCa_c_dt
    dV_m_dt = ((-Cor) * (-I_stim + (I_BK + (I_Ca + I_Na)))) / C_m
    values[5] = dV_m_dt

    return values


def monitor_values(t, states, parameters):

    # Assign states
    IP_3 = states[0]
    d_Na_d_Na = states[1]
    f_Na_f_Na = states[2]
    Ca_s = states[3]
    Ca_c = states[4]
    V_m = states[5]

    # Assign parameters
    C_m = parameters[0]
    Cor = parameters[1]
    E_Ca = parameters[2]
    E_K = parameters[3]
    E_Na = parameters[4]
    G_MCa = parameters[5]
    G_Na = parameters[6]
    G_max_BK = parameters[7]
    I_stim = parameters[8]
    K = parameters[9]
    P_MV = parameters[10]
    V_0 = parameters[11]
    V_1 = parameters[12]
    V_M2 = parameters[13]
    V_M3 = parameters[14]
    V_M4 = parameters[15]
    beta_ = parameters[16]
    eta = parameters[17]
    k_2 = parameters[18]
    k_4 = parameters[19]
    k_Ca = parameters[20]
    k_a = parameters[21]
    k_f = parameters[22]
    k_p = parameters[23]
    k_r = parameters[24]
    k_v = parameters[25]
    m = parameters[26]
    n = parameters[27]
    o = parameters[28]
    q = parameters[29]
    r = parameters[30]
    tau_d_Na = parameters[31]
    tau_f_Na = parameters[32]
    u = parameters[33]
    w = parameters[34]

    # Assign expressions
    shape = 16 if len(states.shape) == 1 else (16, states.shape[1])
    values = numpy.zeros(shape)
    G_Ca = (Ca_c**q * G_MCa) / (Ca_c**q + k_Ca**q)
    values[0] = G_Ca
    d_BK_d_BK = 1.0 / (1e-06 * Ca_c ** (-2.0) * numpy.exp(V_m / ((17.0 * (-1)))) + 1.0)
    values[1] = d_BK_d_BK
    d_inf_Na = 1.0 / (numpy.exp((V_m + 7.0) / ((5.0 * (-1)))) + 1.0)
    values[2] = d_inf_Na
    f_inf_Na = 1.0 / (numpy.exp((V_m + 37.4) / 4.0) + 1.0)
    values[3] = f_inf_Na
    I_Na = (d_Na_d_Na * (G_Na * f_Na_f_Na)) * (-E_Na + V_m)
    values[4] = I_Na
    V_2 = (Ca_c**n * V_M2) / (Ca_c**n + k_2**n)
    values[5] = V_2
    V_3 = (
        IP_3**o
        * ((Ca_s**m * ((Ca_c**w * V_M3) / (Ca_c**w + k_a**w))) / (Ca_s**m + k_r**m))
    ) / (IP_3**o + k_p**o)
    values[6] = V_3
    V_in = IP_3 * V_1 + V_0
    values[7] = V_in
    dIP_3_dt = Cor * (
        P_MV * (1.0 - V_m**r / (V_m**r + k_v**r))
        + (((-(IP_3**u)) * V_M4) / (IP_3**u + k_4**u) + ((-IP_3) * eta + beta_))
    )
    values[8] = dIP_3_dt
    I_Ca = G_Ca * (-E_Ca + V_m)
    values[9] = I_Ca
    I_BK = (G_max_BK * d_BK_d_BK) * (-E_K + V_m)
    values[10] = I_BK
    dd_Na_d_Na_dt = (Cor * (-d_Na_d_Na + d_inf_Na)) / tau_d_Na
    values[11] = dd_Na_d_Na_dt
    df_Na_f_Na_dt = (Cor * (-f_Na_f_Na + f_inf_Na)) / tau_f_Na
    values[12] = df_Na_f_Na_dt
    dCa_s_dt = Cor * ((-Ca_s) * k_f + (V_2 - V_3))
    values[13] = dCa_s_dt
    dCa_c_dt = Cor * ((-Ca_c) * K + (Ca_s * k_f + (V_3 + (-V_2 + V_in))))
    values[14] = dCa_c_dt
    dV_m_dt = ((-Cor) * (-I_stim + (I_BK + (I_Ca + I_Na)))) / C_m
    values[15] = dV_m_dt

    return values


def generalized_rush_larsen(states, t, dt, parameters):

    # Assign states
    IP_3 = states[0]
    d_Na_d_Na = states[1]
    f_Na_f_Na = states[2]
    Ca_s = states[3]
    Ca_c = states[4]
    V_m = states[5]

    # Assign parameters
    C_m = parameters[0]
    Cor = parameters[1]
    E_Ca = parameters[2]
    E_K = parameters[3]
    E_Na = parameters[4]
    G_MCa = parameters[5]
    G_Na = parameters[6]
    G_max_BK = parameters[7]
    I_stim = parameters[8]
    K = parameters[9]
    P_MV = parameters[10]
    V_0 = parameters[11]
    V_1 = parameters[12]
    V_M2 = parameters[13]
    V_M3 = parameters[14]
    V_M4 = parameters[15]
    beta_ = parameters[16]
    eta = parameters[17]
    k_2 = parameters[18]
    k_4 = parameters[19]
    k_Ca = parameters[20]
    k_a = parameters[21]
    k_f = parameters[22]
    k_p = parameters[23]
    k_r = parameters[24]
    k_v = parameters[25]
    m = parameters[26]
    n = parameters[27]
    o = parameters[28]
    q = parameters[29]
    r = parameters[30]
    tau_d_Na = parameters[31]
    tau_f_Na = parameters[32]
    u = parameters[33]
    w = parameters[34]

    # Assign expressions

    values = numpy.zeros_like(states, dtype=numpy.float64)
    G_Ca = (Ca_c**q * G_MCa) / (Ca_c**q + k_Ca**q)
    d_BK_d_BK = 1.0 / (1e-06 * Ca_c ** (-2.0) * numpy.exp(V_m / ((17.0 * (-1)))) + 1.0)
    d_inf_Na = 1.0 / (numpy.exp((V_m + 7.0) / ((5.0 * (-1)))) + 1.0)
    f_inf_Na = 1.0 / (numpy.exp((V_m + 37.4) / 4.0) + 1.0)
    I_Na = (d_Na_d_Na * (G_Na * f_Na_f_Na)) * (-E_Na + V_m)
    V_2 = (Ca_c**n * V_M2) / (Ca_c**n + k_2**n)
    V_3 = (
        IP_3**o
        * ((Ca_s**m * ((Ca_c**w * V_M3) / (Ca_c**w + k_a**w))) / (Ca_s**m + k_r**m))
    ) / (IP_3**o + k_p**o)
    V_in = IP_3 * V_1 + V_0
    dIP_3_dt = Cor * (
        P_MV * (1.0 - V_m**r / (V_m**r + k_v**r))
        + (((-(IP_3**u)) * V_M4) / (IP_3**u + k_4**u) + ((-IP_3) * eta + beta_))
    )
    dIP_3_dt_linearized = Cor * (
        -eta
        + IP_3 ** (2 * u) * V_M4 * u / (IP_3 * (IP_3**u + k_4**u) ** 2)
        - IP_3**u * V_M4 * u / (IP_3 * (IP_3**u + k_4**u))
    )
    values[0] = IP_3 + numpy.where(
        numpy.logical_or((dIP_3_dt_linearized > 1e-08), (dIP_3_dt_linearized < -1e-08)),
        dIP_3_dt * (numpy.exp(dIP_3_dt_linearized * dt) - 1) / dIP_3_dt_linearized,
        dIP_3_dt * dt,
    )
    I_Ca = G_Ca * (-E_Ca + V_m)
    I_BK = (G_max_BK * d_BK_d_BK) * (-E_K + V_m)
    dd_Na_d_Na_dt = (Cor * (-d_Na_d_Na + d_inf_Na)) / tau_d_Na
    dd_Na_d_Na_dt_linearized = -Cor / tau_d_Na
    values[1] = d_Na_d_Na + numpy.where(
        numpy.logical_or(
            (dd_Na_d_Na_dt_linearized > 1e-08), (dd_Na_d_Na_dt_linearized < -1e-08)
        ),
        dd_Na_d_Na_dt
        * (numpy.exp(dd_Na_d_Na_dt_linearized * dt) - 1)
        / dd_Na_d_Na_dt_linearized,
        dd_Na_d_Na_dt * dt,
    )
    df_Na_f_Na_dt = (Cor * (-f_Na_f_Na + f_inf_Na)) / tau_f_Na
    df_Na_f_Na_dt_linearized = -Cor / tau_f_Na
    values[2] = f_Na_f_Na + numpy.where(
        numpy.logical_or(
            (df_Na_f_Na_dt_linearized > 1e-08), (df_Na_f_Na_dt_linearized < -1e-08)
        ),
        df_Na_f_Na_dt
        * (numpy.exp(df_Na_f_Na_dt_linearized * dt) - 1)
        / df_Na_f_Na_dt_linearized,
        df_Na_f_Na_dt * dt,
    )
    dCa_s_dt = Cor * ((-Ca_s) * k_f + (V_2 - V_3))
    dCa_s_dt_linearized = -Cor * k_f
    values[3] = Ca_s + numpy.where(
        numpy.logical_or((dCa_s_dt_linearized > 1e-08), (dCa_s_dt_linearized < -1e-08)),
        dCa_s_dt * (numpy.exp(dCa_s_dt_linearized * dt) - 1) / dCa_s_dt_linearized,
        dCa_s_dt * dt,
    )
    dCa_c_dt = Cor * ((-Ca_c) * K + (Ca_s * k_f + (V_3 + (-V_2 + V_in))))
    dCa_c_dt_linearized = -Cor * K
    values[4] = Ca_c + numpy.where(
        numpy.logical_or((dCa_c_dt_linearized > 1e-08), (dCa_c_dt_linearized < -1e-08)),
        dCa_c_dt * (numpy.exp(dCa_c_dt_linearized * dt) - 1) / dCa_c_dt_linearized,
        dCa_c_dt * dt,
    )
    dV_m_dt = ((-Cor) * (-I_stim + (I_BK + (I_Ca + I_Na)))) / C_m
    values[5] = V_m + dV_m_dt * dt

    return values
