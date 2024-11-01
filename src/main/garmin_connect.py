import streamlit as st
from datetime import datetime, timedelta
import plotly.express as px
from data.db_utils import *
from main.garmin import *

show_heartrate()
show_totalsteps()
show_stress()
show_sleeping_sec()
show_active_sec()
show_sleep_quality()