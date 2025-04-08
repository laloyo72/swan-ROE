#timegpt for operational forecasting system
# by @laloyo 
#last modifed: 07/04/2025
##############^w^################
#import key from .env
from dotenv import load_dotenv
load_dotenv()

from nixtla import NixtlaClient
nixtla_client = NixtlaClient()
#validate key is okkkk
nixtla_client.validate_api_key()

# import rest libraries
import pandas as pd
import sys
import os
from datetime import date, datetime, timezone, timedelta


# read pass data COMBINED: calculated mareograf (var you want to predict) and exogenous vars from swan forecast: Hsig, RTpeak, Dir
df = pd.read_csv('/home/laloyo/timeGPT/combine/Hsig_exog_vars_swan-mareograf_20240228_20241231.csv', skiprows=1 ,sep=" ", names=['ds', 'Exogenous1', 'Exogenous2', 'Exogenous3', 'y'])
df = df.iloc[1:,:]
df['ds'] = pd.to_datetime(df['ds'])
print(df.tail())

# read future
# first get what has been saved
# find path
future_file_path=sys.argv[1] # swan forecast
# read
df_future = pd.read_csv(future_file_path, sep=r'\s+', skiprows=7, header=None,
                     names=['ds', 'Xp', 'Yp', 'Depth', 'Exogenous1', 'Tm02_swan', 'Exogenous2', 'Exogenous3'], dtype={"ds": str}) #exos: hisg, rtpeak,dir
df_future = df_future[['ds', 'Exogenous1', 'Exogenous2', 'Exogenous3']]
df_future['ds'] = df_future['ds'].str.replace(r'\.', '', regex=True)  # Remove decimal
df_future['ds'] = pd.to_datetime(df_future['ds'], format='%Y%m%d%H%M%S')  # Convert to datetime
df_future=df_future.iloc[1:, :] #primer valor de simulación siempre está mal
print(df_future.head())
print(df_future.tail())

#fcst with timeGPT
#TODO: modify h reading future_file_path, this for when we use different times
timegpt_fcst_ex_vars_df = nixtla_client.forecast(df=df, X_df=df_future, h=24, level=[80, 90], freq="1h")
#save 
today = datetime.now(timezone.utc)
today_str = today.strftime("%Y%m%d")
print(today_str)
time_dir = today.strftime("%Y%m")
save_dir = f"/home/laloyo/swan/timeGPT/prediction/{time_dir}/" # we can change this to be more for any user with a path variable
os.makedirs(save_dir, exist_ok=True)
output_file=os.path.join(save_dir, f"Hsig_swan{today_str}.csv")
print(output_file)
# modify date to today, as we treaked (trampa) timeGPT
n_rows = timegpt_fcst_ex_vars_df.shape[0]

today_utc_midnight = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
new_dates = pd.date_range(start=today_utc_midnight, periods=n_rows, freq='h')
timegpt_fcst_ex_vars_df['ds'] = new_dates

print(timegpt_fcst_ex_vars_df.head())
# and now we can SAVE timeGPT's prediction
timegpt_fcst_ex_vars_df.to_csv(output_file, sep='\t', index=False)

