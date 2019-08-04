import sys
from utils.zonal_datetime import *
from models.script import Script
from models.ticker_5min import Ticker5min
from models.strategy_breakout_5min import StrategyBreakout_5Min
from utils.pretty_json import *
from db.database import atomic_insert
from datetime import datetime
from peewee import fn

# global members'
ScriptIdKey = 'script_id'
DateKey = 'date'
UpperCutOffPriceKey = 'upper_cutoff_price'
LowerCutOffPriceKey = 'lower_cutoff_price'
DayMaxPriceKey = 'day_max_price'
DayMinPriceKey = 'day_min_price'

SellEntryTimeKey = 'sell_entry_time'
SellProfitOnePercentTimeKey = 'sell_profit_one_percent_time'
SellMaxStoplossBeforeOnePercentKey = 'sell_max_stoploss_before_one_percent'

BuyEntryTimeKey = 'buy_entry_time'
BuyProfitOnePercentTimeKey = 'buy_profit_one_percent_time'
BuyMaxStoplossBeforeOnePercentKey = 'buy_max_stoploss_before_one_percent'

MaxPosAfterBuyEntryKey = 'max_positive_after_buy_entry'
MaxNegAfterBuyEntryKey = 'max_negative_after_buy_entry'
TimeReachOnePercentAfterBuyKey = 'time_to_reach_one_percent_after_buy'
SellKey = 'sell'

MaxPosAfterSellEntryKey = 'max_positive_after_sell_entry'
MaxNegAfterSellEntryKey = 'max_negative_after_sell_entry'
TimeReachOnePercentAfterSellKey = 'time_to_reach_one_percent_after_sell'


class Breakout5min():
    def __init__(self):
        print("Breakout analyzer added")

    def apply(self):
        start_time = datetime.now()
        if not StrategyBreakout_5Min.table_exists():
            StrategyBreakout_5Min.create_table()

        # get all scripts
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
                analysis_start_date = analysis_start_date[0].date + timedelta(
                    days=1)
                print('starting analysis from: '+str(analysis_start_date))
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
        end_time = datetime.now()
        print('elapsed time: ' + str(end_time - start_time))

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
        # print_json(analysis_list)
        atomic_insert(StrategyBreakout_5Min, analysis_list)

    def get_one_trade_day_analysis(self, script_id, dt_obj):
        # weekend check
        if not is_weekday(dt_obj):
            return None

        first_candle_time = dt_obj.replace(hour=9, minute=15)
        last_candle_time = dt_obj.replace(hour=15, minute=25)
        ticker_count_validness = (Ticker5min
                                  .select()
                                  .where(
                                      Ticker5min.script_id == script_id,
                                      Ticker5min.record_datetime.in_(
                                          [last_candle_time, first_candle_time]))
                                  .count()
                                  )

        if ticker_count_validness == 2:
            result_dict = {}
            result_dict[DateKey] = dt_obj
            result_dict[ScriptIdKey] = script_id
            # query day low and high prices
            market_opening_time = dt_obj.replace(hour=9, minute=15, second=00)
            market_closing_time = dt_obj.replace(hour=15, minute=30, second=00)
            day_low_high = (Ticker5min
                            .select(fn.Min(Ticker5min.low_price), fn.Max(Ticker5min.high_price))
                            .where(Ticker5min.script_id == script_id,
                                   Ticker5min.record_datetime >= market_opening_time,
                                   Ticker5min.record_datetime <= market_closing_time)
                            .scalar(as_tuple=True)
                            )
            result_dict[DayMinPriceKey] = round(day_low_high[0], 2)
            result_dict[DayMaxPriceKey] = round(day_low_high[1], 2)
            # query cutoff price for day
            one_hr_start = dt_obj.replace(hour=9, minute=15, second=00)
            one_hr_end = dt_obj.replace(hour=10, minute=00, second=00)
            cut_off_prices = (Ticker5min
                              .select(fn.Min(Ticker5min.low_price), fn.Max(Ticker5min.high_price))
                              .where(Ticker5min.script_id == script_id,
                                     Ticker5min.record_datetime >= one_hr_start,
                                     Ticker5min.record_datetime <= one_hr_end)
                              .scalar(as_tuple=True)
                              )
            result_dict[LowerCutOffPriceKey] = round(cut_off_prices[0], 2)
            result_dict[UpperCutOffPriceKey] = round(cut_off_prices[1], 2)

            # query sell entry time if any
            sell_entry = (Ticker5min
                          .select(Ticker5min.record_datetime)
                          .where(Ticker5min.script_id == script_id,
                                 Ticker5min.low_price < result_dict[LowerCutOffPriceKey],
                                 Ticker5min.record_datetime > one_hr_end,
                                 Ticker5min.record_datetime <= market_closing_time)
                          .order_by(Ticker5min.record_datetime.asc())
                          .limit(1)
                          )
            if sell_entry:
                result_dict[SellEntryTimeKey] = sell_entry[0].record_datetime
                # query for remaining column for sell side
                one_percent_lower_cutoff = (result_dict[LowerCutOffPriceKey] -
                                            result_dict[LowerCutOffPriceKey] * 0.01)
                one_percent_sell_profit = (Ticker5min
                                           .select(Ticker5min.record_datetime)
                                           .where(Ticker5min.script_id == script_id,
                                                  Ticker5min.low_price < one_percent_lower_cutoff,
                                                  Ticker5min.record_datetime >= result_dict[SellEntryTimeKey],
                                                  Ticker5min.record_datetime <= market_closing_time)
                                           .order_by(Ticker5min.record_datetime.asc())
                                           .limit(1)
                                           )
                if one_percent_sell_profit:
                    result_dict[SellProfitOnePercentTimeKey] = one_percent_sell_profit[0].record_datetime
                    sell_max_stop_loss = (Ticker5min
                                          .select(fn.Max(Ticker5min.high_price))
                                          .where(Ticker5min.script_id == script_id,
                                                 Ticker5min.record_datetime >= result_dict[SellEntryTimeKey],
                                                 Ticker5min.record_datetime <= result_dict[SellProfitOnePercentTimeKey])
                                          .scalar()
                                          )
                    sell_max_stop_loss_percent = ((sell_max_stop_loss - result_dict[LowerCutOffPriceKey]) /
                                                  result_dict[LowerCutOffPriceKey]) * 100
                    result_dict[SellMaxStoplossBeforeOnePercentKey] = round(
                        sell_max_stop_loss_percent, 2)
                else:
                    result_dict[SellProfitOnePercentTimeKey] = None
                    result_dict[SellMaxStoplossBeforeOnePercentKey] = None
            else:
                result_dict[SellEntryTimeKey] = None
                result_dict[SellProfitOnePercentTimeKey] = None
                result_dict[SellMaxStoplossBeforeOnePercentKey] = None

            # query buy entry time if any
            buy_entry = (Ticker5min
                         .select(Ticker5min.record_datetime)
                         .where(Ticker5min.script_id == script_id,
                                Ticker5min.high_price > result_dict[UpperCutOffPriceKey],
                                Ticker5min.record_datetime > one_hr_end,
                                Ticker5min.record_datetime <= market_closing_time)
                         .order_by(Ticker5min.record_datetime.asc())
                         .limit(1)
                         )
            if buy_entry:
                result_dict[BuyEntryTimeKey] = buy_entry[0].record_datetime
                # query for remaining column for buy side
                one_percent_upper_cutoff = (result_dict[UpperCutOffPriceKey] +
                                            result_dict[UpperCutOffPriceKey] * 0.01)
                one_percent_buy_profit = (Ticker5min
                                          .select(Ticker5min.record_datetime)
                                          .where(Ticker5min.script_id == script_id,
                                                 Ticker5min.high_price > one_percent_upper_cutoff,
                                                 Ticker5min.record_datetime >= result_dict[BuyEntryTimeKey],
                                                 Ticker5min.record_datetime <= market_closing_time,)
                                          .order_by(Ticker5min.record_datetime.asc())
                                          .limit(1)
                                          )
                if one_percent_buy_profit:
                    result_dict[BuyProfitOnePercentTimeKey] = one_percent_buy_profit[0].record_datetime
                    buy_max_stop_loss = (Ticker5min
                                         .select(fn.Min(Ticker5min.low_price))
                                         .where(Ticker5min.script_id == script_id,
                                                Ticker5min.record_datetime >= result_dict[BuyEntryTimeKey],
                                                Ticker5min.record_datetime <= result_dict[BuyProfitOnePercentTimeKey])
                                         .scalar()
                                         )
                    buy_max_stop_loss_percent = ((result_dict[UpperCutOffPriceKey] - buy_max_stop_loss) /
                                                 result_dict[UpperCutOffPriceKey]) * 100
                    result_dict[BuyMaxStoplossBeforeOnePercentKey] = round(
                        buy_max_stop_loss_percent, 2)
                else:
                    result_dict[BuyProfitOnePercentTimeKey] = None
                    result_dict[BuyMaxStoplossBeforeOnePercentKey] = None
            else:
                result_dict[BuyEntryTimeKey] = None
                result_dict[BuyProfitOnePercentTimeKey] = None
                result_dict[BuyMaxStoplossBeforeOnePercentKey] = None

            return result_dict

        else:
            return None
