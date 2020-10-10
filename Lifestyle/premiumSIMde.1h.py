#!/usr/bin/env python
# -*- coding: utf-8 -*-

# <bitbar.title>PremiumSIM (Deutschland) Balance</bitbar.title>
# <bitbar.version>v1.0.0</bitbar.version>
# <bitbar.author>Jack Higgins</bitbar.author>
# <bitbar.author.github>skhg</bitbar.author.github>
# <bitbar.desc>Displays your current month's PremiumSIM (Deutschland) data balance allowance</bitbar.desc>
# <bitbar.image>TODO</bitbar.image>
# <bitbar.dependencies>python 2.7 or 3.6, pypremiumsim</bitbar.dependencies>
# <bitbar.abouturl>TODO</bitbar.abouturl>







# START USER DETAILS

# Enter your premiumSIM.de login details here. These are sent only to the PremiumSIM
# website and never stored or transmitted anywhere else.

username = "My User Name"
password = "My Password"

# END USER DETAILS






from sys import exit
import sys

# VERIFY DEPENDENCIES
try:
    from pypremiumsim import PremiumSimSession
except ImportError as ex:
    print(sys.version)
    print("PremiumSIM.de")
    print("---")
    print("Looks like the package 'pypremiumsim' isn't installed.")
    print("You need it to run this tool. To install, click 'Install Now',")
    print("then click 'Preferences' -> 'Refresh All...'")
    print("Install Now | bash='/usr/bin/env pip install pypremiumsim'")
    exit()






# START APP

import pickle
import os
import subprocess

class StateMgmt:

    def __init__(self):
        os.chdir(self.get_bitbar_plugins_dir())
        self.relative_state_dir = "./.pypremiumsim_state/"
        self.state_dump_file = self.relative_state_dir+"pypremiumsim_last_state.pickle"

    def get_bitbar_plugins_dir(self):
        bitbar_defaults = subprocess.check_output(["defaults", "read", "com.matryer.BitBar"]).split(";")
        for entry in bitbar_defaults:
            if "pluginsDirectory" in entry:
                return entry.split("\"")[1]

        raise IOError("BitBar plugins directory could not be found")

    def check_state_dir_exists(self, state_dir):
        if os.path.exists(state_dir) is False:
            os.mkdir(state_dir)

    def load_state(self):
        self.check_state_dir_exists(self.relative_state_dir)

        if os.path.exists(self.state_dump_file) is False:
            return None
        else:
            try:
                with open(self.state_dump_file, "r") as f_read:
                    return pickle.load(f_read)
            except:
                return None

    def dump_state(self, current_state):
        self.check_state_dir_exists(self.relative_state_dir)

        with open(self.state_dump_file, "w") as f_write:
            pickle.dump(current_state, f_write)

class ResultsFormatter:
    def print_output(self, data, is_live):
        print(u'👑{:,.1f}%'.format(data.used_percentage).encode("utf-8"))
        print("---")
        if is_live is False:
            print("❌ : Using cached data, last update failed")
            print("---")

        print("User: "+username)
        print("---")
        print(u'{:,.2f} GB total'.format(data.tariff_total_data_gb).encode("utf-8"))
        print(u'{:,.2f} GB used'.format(data.consumed_data_gb).encode("utf-8"))
        print("---")

        print("premiumsim.de | href=https://service.premiumsim.de/")

    def print_error_message(self):
        print("❌")
        print("---")
        print("Error: Unable to retrieve PremiumSIM state.")
        print("---")

        print("premiumsim.de | href=https://service.premiumsim.de/")

def run():
    login_ok= False

    session = PremiumSimSession()

    try:
        login_ok = session.try_login(username, password)
    except Exception:
        pass

    state = StateMgmt()
    formatter = ResultsFormatter()

    if login_ok:
        usage = session.current_month_data_usage()

        state.dump_state(usage)
        formatter.print_output(usage, True)
    else:
        loaded_state = state.load_state()
        if loaded_state is not None:
            formatter.print_output(loaded_state, False)
        else:
            formatter.print_error_message()

run()
