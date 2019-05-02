from datetime import date, timedelta
from functools import partial
from time import sleep
from calendar import monthrange
from random import randrange

from pytrends.request import TrendReq
from pytrends.exceptions import ResponseError
import pandas as pd


def getTimeframe(start: date, stop: date) -> str:
    """Given two dates, returns a string representing the interval between the
    dates. This is string is used to retrieve data for a specific time frame
    from Google Trends.
    """
    return f"{start.strftime('%Y-%m-%d')} {stop.strftime('%Y-%m-%d')}"


def _fetchData(pytrends, build_payload, timeframe: str) -> pd.DataFrame:
    """Attempts to fecth data and retries in case of a ResponseError."""
    attempts, fetched = 0, False
    while not fetched:
        try:
            build_payload(timeframe=timeframe)
        except ResponseError:
            wait_time = 300*attempts  # Start with 0 due to timeouts
            print(f'Trying again in {wait_time/60:.0f} minutes.')
            sleep(wait_time)
            attempts += 1
        else:
            fetched = True
    return pytrends.interest_over_time()


def getDailyData(word: str,
                 start_year: int = 2007,
                 stop_year: int = 2018,
                 geo: str = 'US',
                 tz: int = 240,
                 verbose: bool = True,
                 wait_time: float = 5.0) -> pd.DataFrame:
    """Given a word, fetches daily search volume data from Google Trends and
    returns results in a pandas DataFrame.
    Details: Due to the way Google Trends scales and returns data, special
    care needs to be taken to make the daily data comparable over different
    months. To do that, we download daily data on a month by month basis,
    and also monthly data. The monthly data is downloaded in one go, so that
    the monthly values are comparable amongst themselves and can be used to
    scale the daily data. In a given month, the daily data is scaled so that
    the month by month average of daily values is equal to the values at the
    monthly frequency. That is, the daily data is scaled by multiplying the
    daily values by the ratio of the monthly series value to the monthly
    average of the daily data.

    Args:
        word (str): Word to fetch daily data for.
        start_year (int): First year to fetch data for. Starts at the beginning
            of this year (1st of January).
        stop_year (int): Last year to fetch data for (inclusive). Stops at the
            end of this year (31st of December).
        geo (str): Geographical area code. Default at 'US'.
        tz (int): Time zone, minutes offset off GMT (240 for US EST).
        verbose (bool): If True, then prints the word and current time frame
            we are fecthing the data for.
        wait_time (float): Scaling factor for how much to wait between data
            requests. If 0, then a new request is sent at about every 0.5
            second. The default of 5 seconds implies in a new request being
            sent at about every 3 seconds (random).
    Returns:
        complete (pd.DataFrame): Contains 4 columns.
            The column named after the word argument contains the daily search
            volume already scaled and comparable through time.
            The column f'{word}_{geo}_unscaled' is the original daily data
            fetched month by month, and it is not comparable across different
            months (but is comparable within a month).
            The column f'{word}_{geo}_monthly' contains the original monthly
            data fetched at once. The values in this column have been
            backfilled so that there are no NaN present.
            The column 'scale' contains the scale used to obtain the scaled
            daily data.
    """

    # Set up start and stop dates
    start_date = date(start_year, 1, 1)
    # stop_date cannot be later than today's date
    stop_date = min([date(stop_year, 12, 31), date.today()])

    # Start pytrends for US region
    pytrends = TrendReq(hl='en-US', tz=tz)
    # Initialize build_payload with the word we need data for
    build_payload = partial(pytrends.build_payload,
                            kw_list=[word], cat=0, geo=geo, gprop='')

    # Obtain monthly data for all months in years [2004, stop_year]
    monthly = _fetchData(pytrends, build_payload,
                         getTimeframe(date(2004, 1, 1), stop_date))[start_date:stop_date]

    # Get daily data, month by month
    results = {}
    # If a timeout or too many requests error occur we need to adjust wait time
    current = start_date
    while current < stop_date:
        lastDateOfMonth = date(current.year, current.month,
                               monthrange(current.year, current.month)[1])
        timeframe = getTimeframe(current, lastDateOfMonth)
        if verbose:
            print(f'{word}/{geo}:{timeframe}')
        results[current] = _fetchData(pytrends, build_payload, timeframe)
        current = lastDateOfMonth + timedelta(days=1)
        # Don't go too fast or Google will send 429s
        sleep(randrange(10, 10*wait_time)/10)

    # Concatenate daily data into a single dataframe
    daily = pd.concat(results.values()).drop(columns=['isPartial'])
    # Compute month by month averages of daily data
    dailyaverage = daily.resample('M').mean()
    # The above produces weird index dates, so cut them
    dailyaverage.index = dailyaverage.index.values.astype('<M8[M]')
    daily[f'{word}_{geo}_avg'] = dailyaverage
    daily[f'{word}_{geo}_avg'].ffill(inplace=True)  # Fill in forward
    complete = daily.join(monthly, lsuffix=f'_{geo}_unscaled',
                          rsuffix=f'_{geo}_monthly')

    # Scale daily data by monthly weights so the data is comparable
    complete[f'{word}_{geo}_monthly'].ffill(inplace=True)  # fill NaN values
    complete['scale'] = complete[f'{word}_{geo}_monthly']/complete[f'{word}_{geo}_avg']
    complete[f'{word}_{geo}'] = complete[f'{word}_{geo}_unscaled']*complete.scale
    # Drop monthly average and isPartial
    complete.drop(columns=['isPartial', f'{word}_{geo}_avg'], inplace=True)
    return complete
