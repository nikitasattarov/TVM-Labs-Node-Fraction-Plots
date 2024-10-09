import math
import numpy as np
import matplotlib.pyplot as plt 
import streamlit as st
import pandas as pd
from decimal import Decimal, getcontext, ROUND_HALF_UP

getcontext().prec = 150

def dec(number):
    #getcontext().prec = 200
    #return(number)
    return(Decimal(str(number)))

def input_bk_package_price():
    return st.number_input(
        label = r'Insert a package price ($)', 
        help = r"Package price is in $ \lbrack 1, 100\rbrack $", 
        value = 11.0, 
        format = "%f",
        min_value = 1.0,
        max_value = 100000.0
        )

def input_number_of_block_keepers():
    return st.number_input(
        label = r'Insert a total number of Block Keepers', 
        help = r"Number of Block Keepers is in $ \lbrack 100, 10000 \rbrack $", 
        value = 7500, 
        format = "%i",
        min_value = 100,
        max_value = 10000
        )

def expected_apy_calc(YearsNumber, TotalSupply, KFS, u_tokens, SecondsInYear, FRC, ParticipantsNum):
    return FRC * TotalSupply * (dec(1) + KFS) * (dec(1) - dec(math.exp(-u_tokens * dec(YearsNumber) * dec(SecondsInYear)))) / ParticipantsNum

def input_number_of_licenses_per_tier_bk(ParticipantsNum, ServerFraction):
    upper_limit = dec(0.5) * ParticipantsNum * ServerFraction
    #st.write(upper_limit)
    return st.number_input(
        label = r'Insert a number of packages', 
        #help = r"Number of licenses is in $ \left\lbrack 1, \min\left(200, \ \text{Number of Block Keepers}\right) \right\rbrack $", 
        help = rf"Number of packages is in $ \left\lbrack 1, {upper_limit} \right\rbrack $",
        value = 1, 
        format = "%i",
        min_value = 1,
        #max_value = min(200, int(ParticipantsNum))
        max_value = int(upper_limit)
        )

def input_years_number():
    return st.number_input(
        label = r'Insert the number of years since the network launch', 
        help = r"Number of years since the network launch is in $ \lbrack 1, 5\rbrack $", 
        value = 1, 
        format = "%i",
        min_value = 1,
        max_value = 5
        )

def input_plot_scale():
    return st.number_input(
        label = r'Insert a plot scale (in years)', 
        help = r"Plot scale (in years) is in $ \lbrack 1, 60\rbrack $", 
        value = 25, 
        format = "%i",
        min_value = 1,
        max_value = 60
        )

def TMTA_calc(t, TotalSupply, KFS, u_tokens):
    return TotalSupply * (dec(1) + KFS) * (dec(1) - dec(math.exp(-u_tokens* dec(t))))

def minted_tokens_number_calc(t, TotalSupply, KFS, u_tokens, FRC, ParticipantsNum, number_of_purchased_licenses):
    return FRC * TotalSupply * (dec(1) + KFS) * (dec(1) - dec(math.exp(-u_tokens* dec(t)))) / ParticipantsNum * number_of_purchased_licenses

def free_float(t, FFF, maxFF, u_ff):
    return dec(dec(maxFF) * (dec(1) + dec(FFF)) * (dec(1) - dec(math.exp(-u_ff * dec(t)))))

TotalSupply = dec(10400000000)
KFS = dec(10 ** (-5))
TTMT = dec(2000000000)
u_tokens= -dec(1) / TTMT * dec(math.log(KFS / (dec(1) + KFS)))
SecondsInYear = 31557600
SecondsInMonth = 2629800
maxFF = dec(1 / 3)
FFF = dec(10 ** (-2))
u_ff = -dec(1) / dec(TTMT) * dec(math.log(FFF / (dec(1) + FFF)))


st.title("Acki Nacki Node Sale Tokenomics Plots (Fractional)")

package_type_option = st.selectbox(
   r"Select the package:",
   (r"1 core",
    r"5 cores",
    r"10 cores",
    r"50 cores",
    r"100 cores",
    r"250 cores",
    r"500 cores",
    r"1000 cores"),
   index=0,
)

cores_num = int(package_type_option.split()[0])
#st.write(cores_num)
server_fraction = dec(500) / dec(cores_num)
#st.write(server_fraction)

package_price = dec(input_bk_package_price())
ParticipantsNum = dec(input_number_of_block_keepers())
st.write(f"(assuming {round(ParticipantsNum / 10000 * 100, 2)}% node participation)")
number_of_purchased_licenses = dec(input_number_of_licenses_per_tier_bk(ParticipantsNum, server_fraction))

YearsNumber = dec(input_years_number())
FRC = dec(0.675) # Function Reward Coefficient
expected_bk_reward = expected_apy_calc(YearsNumber, TotalSupply, KFS, u_tokens, SecondsInYear, FRC, ParticipantsNum) / server_fraction * number_of_purchased_licenses
implied_token_price = package_price * number_of_purchased_licenses / expected_bk_reward
TMTA = TMTA_calc(YearsNumber * SecondsInYear, TotalSupply, KFS, u_tokens)
implied_fdv = TMTA * implied_token_price
st.markdown(f"<h2 style='font-weight:bold;'>Total Minted Token Amount (NACKL) = {"{:,}".format(round(TMTA, 0))} </h2>", unsafe_allow_html=True)
st.markdown(f"<h2 style='font-weight:bold;'>Implied {YearsNumber}Y Reward (NACKL) = {"{:,}".format(round(expected_bk_reward, 0))} </h2>", unsafe_allow_html=True)
st.markdown(f"<h2 style='font-weight:bold;'>Implied {YearsNumber}Y Token Cost ($) = {round(implied_token_price, 7)} </h2>", unsafe_allow_html=True)
st.markdown(f"<h2 style='font-weight:bold;'>Implied {YearsNumber}Y Tier FDV ($) = {"{:,}".format(round(implied_fdv, 0))} </h2>", unsafe_allow_html=True)

st.info(rf"""
Implied {YearsNumber}Y Reward is the amount of NACKL that a network participant will receive over {YearsNumber}Y.
Implied {YearsNumber}Y Token Cost is the total expenses over {YearsNumber}Y divided by the Implied {YearsNumber}Y Reward.     
If the Token Cost exceeds Implied {YearsNumber}Y Token Cost, you will make a profit calculated as:    
$P = \left(\text{{Token Cost}} - \text{{Implied {YearsNumber}Y Token Cost}} \right) \cdot \text{{Implied {YearsNumber}Y Reward}}$     
Implied {YearsNumber}Y Tier FDV is the Implied {YearsNumber}Y Token Cost multiplied by the Total Minted Token Amount after {YearsNumber}Y.
""", icon="ℹ️")
plot_scale = input_plot_scale()

fig, ax = plt.subplots()
if plot_scale <= 15:
    values_x = np.arange(0, plot_scale * SecondsInYear * 1.05,  plot_scale * SecondsInYear * 1.05 / 1000)
    ax.set_xlim([0, plot_scale * SecondsInYear * 1.05])
else:
    values_x = np.arange(0, SecondsInYear * (plot_scale + 4) // 5 * 5 * 1.05,  SecondsInYear * (plot_scale + 4) // 5 * 5 * 1.05 / 1000)
    ax.set_xlim([0, (plot_scale + 4) // 5 * 5 * SecondsInYear * 1.05])
values_tokens = np.array([minted_tokens_number_calc(t, TotalSupply, KFS, u_tokens, FRC, ParticipantsNum, number_of_purchased_licenses) / server_fraction for t in values_x])
min_y_value = min(list(values_tokens))
max_y_value = max(list(values_tokens))
ax.plot(values_x, values_tokens, color = "Green", label = "Fractional Reward")
ax.set_ylim([min_y_value, max_y_value * dec(1.2)])
y_ticks = ax.get_yticks()
if max_y_value > 10 ** 9:
    ax.set_ylabel(r'Token Amount (in billions)')
    if any(y_tick % 1e9 != 0 for y_tick in y_ticks):
        new_labels = [f'{y_tick / 1e9:.1f}' for y_tick in y_ticks]
    else:
        new_labels = [f'{int(y_tick / 1e9)}' for y_tick in y_ticks]
elif max_y_value > 10 ** 6:
    ax.set_ylabel(r'Token Amount (in millions)')
    if any(y_tick % 1e6 != 0 for y_tick in y_ticks):
        new_labels = [f'{y_tick / 1e6:.1f}' for y_tick in y_ticks]
    else:
        new_labels = [f'{int(y_tick / 1e6)}' for y_tick in y_ticks]
elif max_y_value > 10 ** 3:
    ax.set_ylabel(r'Token Amount (in thousands)')
    if any(y_tick % 1e6 != 0 for y_tick in y_ticks):
        new_labels = [f'{y_tick / 1e3:.1f}' for y_tick in y_ticks]
    else:
        new_labels = [f'{int(y_tick / 1e3)}' for y_tick in y_ticks]
else:
    ax.set_ylabel(r'Token Amount')
    new_labels = [f'{int(y_tick)}' for y_tick in y_ticks]
new_labels[0] = '0'
ax.set_yticklabels(new_labels)
if plot_scale == 1:
    xlabels = list([i for i in range(0, plot_scale * 12 + 1, 1)])
    xticks = list([i * SecondsInMonth for i in xlabels])
    ax.set_xlabel(r'Time (in months)')
if plot_scale == 2:
    xlabels = list([i for i in range(0, plot_scale * 12 + 1, 2)])
    xticks = list([i * SecondsInMonth for i in xlabels])
    ax.set_xlabel(r'Time (in months)')
if 3 <= plot_scale <= 5:
    xlabels = list([i for i in range(0, plot_scale * 12 + 1, 5)])
    xticks = list([i * SecondsInMonth for i in xlabels])
    ax.set_xlabel(r'Time (in months)')
if 6 <= plot_scale <= 15:
    xlabels = list([i for i in range(0, plot_scale + 1, 1)])
    xticks = list([i * SecondsInYear for i in xlabels])
    ax.set_xlabel(r'Time (in years)')
if plot_scale >= 16:
    xlabels = list([i for i in range(0, (plot_scale + 4) // 5 * 5 + 1, 5)])
    xticks = list([i * SecondsInYear for i in xlabels])
    ax.set_xlabel(r'Time (in years)')
ax.set_xticks(xticks, xlabels)
ax.legend()
ax.grid(True)
st.pyplot(fig)










