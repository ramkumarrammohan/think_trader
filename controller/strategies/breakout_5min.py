import sys
from utils.zonal_datetime import *
from models.script import Script
from models.ticker_5min import Ticker5min
from models.strategy_breakout_5min import StrategyBreakout_5Min
from utils.pretty_json import *

# global members'
ScriptIdKey = 'script_id'
DateKey = 'date'
UpperCutOffPriceKey = 'upper_cutoff_price'
LowerCutOffPriceKey = 'lower_cutoff_price'
BuyKey = 'buy'
BuyEntryTimeKey = 'buy_entry_time'
MaxPosAfterBuyEntryKey = 'max_positive_after_buy_entry'
MaxNegAfterBuyEntryKey = 'max_negative_after_buy_entry'
TimeReachOnePercentAfterBuyKey = 'time_to_reach_one_percent_after_buy'
SellKey = 'sell'
SellEntryTimeKey = 'sell_entry_time'
MaxPosAfterSellEntryKey = 'max_positive_after_sell_entry'
MaxNegAfterSellEntryKey = 'max_negative_after_sell_entry'
TimeReachOnePercentAfterSellKey = 'time_to_reach_one_percent_after_sell'


class Breakout5min():
    def __init__(self):
        print("breakout analyser")

    def apply(self):
        if not StrategyBreakout_5Min.table_exists():
            print('StrategyBreakout_5Min table not found')
            StrategyBreakout_5Min.create_table()
            print('StrategyBreakout_5Min created')

        # get all scripts
        # scripts = Script.select(Script.id, Script.symbol,
                                # Script.company_name).where(Script.symbol == 'TATAMOTORS')
        scripts = Script.select(Script.id, Script.symbol,
                                Script.company_name).where(Script.alpha_support == True)
        # Iterate through scripts and backtest the strategy for each script
        for script in scripts:
            print('{}. {}'.format(script.id, script.company_name))
            # get the recent record date for the current iterative script
            # analysis_start_date
            analysis_start_date = (StrategyBreakout_5Min.select().where(
                StrategyBreakout_5Min.script_id == script.id).order_by(
                StrategyBreakout_5Min.date.desc()).limit(1))
            if analysis_start_date:
                # replace analysis_start_date with date in 'DATE_FORMAT'
                print('Records found for the script: {}'.format(script.symbol))
            else:
                analysis_start_date = (Ticker5min.select().where(
                    Ticker5min.script_id == script.id).order_by(
                    Ticker5min.record_datetime.asc()).limit(1))
                if analysis_start_date:  # check for period that remaining data to be fetched
                    analysis_start_date = analysis_start_date[0].record_datetime
                else:
                    print('Required data not avail to start analysis for {}'.format(
                        script.company_name))
                    continue
            self.analyze(script.id, analysis_start_date.strftime(
                DATE_FORMAT) + ' 00:00:00')

    def analyze(self, script_id, from_date):
        date_time_obj = datetime.strptime(from_date, DATE_TIME_FORMAT)
        current_date = datetime.now()
        analysis_list = []
        while (date_time_obj <= current_date):
            result_dict = self.get_one_trade_day_analysis(script_id,
                                                          date_time_obj)
            if result_dict:
                analysis_list.append(result_dict)
            date_time_obj = date_time_obj + timedelta(days=1)
        print_json(analysis_list)

    def get_one_trade_day_analysis(self, script_id, dt_obj):
        # weekend check
        if not is_weekday(dt_obj):
            return None

        filter_start_time = dt_obj
        filter_end_time = dt_obj + timedelta(hours=23, minutes=59, seconds=59)
        ticker_data = (Ticker5min.select()
                       .where(Ticker5min.script_id == script_id,
                              Ticker5min.record_datetime >= filter_start_time,
                              Ticker5min.record_datetime < filter_end_time)
                       .order_by(Ticker5min.record_datetime.asc()))
        if ticker_data:
            expected_start_time = dt_obj + timedelta(hours=9, minutes=15)
            expected_end_time = dt_obj + timedelta(hours=15, minutes=25)
            record_time_start = ticker_data[0].record_datetime
            record_time_end = ticker_data[len(ticker_data)-1].record_datetime
            if (record_time_start != expected_start_time or record_time_end != expected_end_time):
                print('Partial data found for the date: {}'
                      .format(dt_obj.strftime(DATE_FORMAT)))
                return None

            observation_time_end = dt_obj + timedelta(hours=10)
            result_data = {}
            result_data[ScriptIdKey] = script_id
            result_data[DateKey] = dt_obj.strftime(DATE_FORMAT)
            result_data[UpperCutOffPriceKey] = 0.0
            result_data[LowerCutOffPriceKey] = 0.0
            result_data[MaxPosAfterBuyEntryKey] = 0.0
            result_data[MaxNegAfterBuyEntryKey] = 0.0
            result_data[MaxPosAfterSellEntryKey] = 0.0
            result_data[MaxNegAfterSellEntryKey] = 0.0
            result_data[BuyKey] = False
            result_data[SellKey] = False
            result_data[BuyEntryTimeKey] = None
            result_data[SellEntryTimeKey] = None
            result_data[TimeReachOnePercentAfterBuyKey] = None
            result_data[TimeReachOnePercentAfterSellKey] = None
            onePercentProfitBuyPrice = 0.0
            onePercentProfitSellPrice = 0.0

            for ticker in ticker_data:
                if (ticker.record_datetime < observation_time_end):
                    if (result_data[LowerCutOffPriceKey] == 0.0):
                        result_data[LowerCutOffPriceKey] = ticker.low_price
                    else:
                        result_data[LowerCutOffPriceKey] = ((lambda: result_data[LowerCutOffPriceKey],
                                                             lambda: ticker.low_price)
                                                            [ticker.low_price < result_data[LowerCutOffPriceKey]]())
                        onePercentProfitSellPrice = (result_data[LowerCutOffPriceKey] +
                                                     result_data[LowerCutOffPriceKey] / 100)
                    if result_data[UpperCutOffPriceKey] == 0.0:
                        result_data[UpperCutOffPriceKey] = ticker.high_price
                    else:
                        result_data[UpperCutOffPriceKey] = ((lambda: result_data[UpperCutOffPriceKey],
                                                             lambda: ticker.high_price)
                                                            [ticker.high_price > result_data[UpperCutOffPriceKey]]())
                        onePercentProfitBuyPrice = (result_data[UpperCutOffPriceKey] +
                                                    result_data[UpperCutOffPriceKey] / 100)
                else:
                    if (ticker.high_price > result_data[UpperCutOffPriceKey]) and result_data[BuyKey] == False:
                        result_data[BuyKey] = True
                        result_data[BuyEntryTimeKey] = (ticker.record_datetime
                                                        .strftime(TIME_FORMAT))
                        result_data[MaxPosAfterBuyEntryKey] = ticker.high_price
                        result_data[MaxNegAfterBuyEntryKey] = ticker.low_price
                    else:
                        result_data[MaxPosAfterBuyEntryKey] = ((lambda: result_data[MaxPosAfterBuyEntryKey],
                                                                lambda: ticker.high_price)
                                                               [ticker.high_price > result_data[MaxPosAfterBuyEntryKey]]())
                        result_data[MaxNegAfterBuyEntryKey] = ((lambda: result_data[MaxNegAfterBuyEntryKey],
                                                                lambda: ticker.low_price)
                                                               [ticker.low_price < result_data[MaxNegAfterBuyEntryKey]]())
                        if (result_data[TimeReachOnePercentAfterBuyKey] == None and
                                result_data[MaxPosAfterBuyEntryKey] > onePercentProfitBuyPrice):
                            result_data[TimeReachOnePercentAfterBuyKey] = (ticker.record_datetime
                                                                           .strftime(TIME_FORMAT))
                    if (ticker.low_price < result_data[LowerCutOffPriceKey]) and result_data[SellKey] == False:
                        result_data[SellKey] = True
                        result_data[SellEntryTimeKey] = (ticker.record_datetime
                                                         .strftime(TIME_FORMAT))
                        result_data[MaxPosAfterSellEntryKey] = ticker.low_price
                        result_data[MaxNegAfterSellEntryKey] = ticker.high_price
                    else:
                        result_data[MaxPosAfterSellEntryKey] = ((lambda: result_data[MaxPosAfterSellEntryKey],
                                                                 lambda: ticker.low_price)
                                                                [ticker.low_price < result_data[MaxPosAfterSellEntryKey]]())
                        result_data[MaxNegAfterSellEntryKey] = ((lambda: result_data[MaxNegAfterSellEntryKey],
                                                                 lambda: ticker.high_price)
                                                                [ticker.high_price > result_data[MaxNegAfterSellEntryKey]]())
                        if (result_data[TimeReachOnePercentAfterSellKey] == None and
                                result_data[MaxPosAfterSellEntryKey] > onePercentProfitSellPrice):
                            result_data[TimeReachOnePercentAfterSellKey] = (ticker.record_datetime
                                                                            .strftime(TIME_FORMAT))
            return result_data

        else:
            return None
