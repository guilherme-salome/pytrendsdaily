# Table of Contents

1.  [pytrendsdaily](#orgca507e0)
    1.  [Usage](#orgad39ac6)


<a id="orgca507e0"></a>

# pytrendsdaily

The [Pytrends](https://github.com/GeneralMills/pytrends) package provides an easy way to obtain data from [Google Trends](https://trends.google.com/trends). This package, `pytrendsdaily`, uses the functionality from `Pytrends` to obtain data from Google Trends at the daily frequency, automatically dealing with scaling issues.


<a id="orgad39ac6"></a>

## Usage

The main functionality of this package is available via the function `getDailyData`.

    from pytrendsdaily import getDailyData

    svi = getDailyData('GOLD PRICES', 2004, 2017)

The variable `svi` contains a Pandas data frame with the original unscaled search volume index (SVI) from Google Trends, and also the scaled data at the daily frequency.
