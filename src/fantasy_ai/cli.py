import argparse
from fantasy_ai.utils.config import LEAGUE_ID
from fantasy_ai.utils.delivery import send_email, send_discord
from fantasy_ai.reports.weekly import weekly_report
from fantasy_ai.reports.waivers import waivers
from fantasy_ai.reports.trade_radar import trade_radar
from fantasy_ai.reports.strategy import generate_weekly_strategy
from fantasy_ai.cli_helpers import get_current_week  # if you keep it separate

def main():
    parser = argparse.ArgumentParser(description="Fantasy AI CLI")
    parser.add_argument(
        "command",
        choices=["weekly-report", "waivers", "trade-radar", "digest", "strategy"],
        help="Command to run"
    )
    parser.add_argument(
        "--week",
        type=int,
        help="NFL week number (optional, auto-detect if omitted)"
    )
    args = parser.parse_args()

    if args.command == "weekly-report":
        weekly_report(args.week)
    elif args.command == "waivers":
        waivers(args.week)
    elif args.command == "trade-radar":
        trade_radar(args.week)
    elif args.command == "digest":
        from io import StringIO
        import sys
        buffer = StringIO()
        sys.stdout = buffer
        weekly_report(args.week)
        waivers(args.week)
        trade_radar(args.week)
        sys.stdout = sys.__stdout__
        output = buffer.getvalue()
        send_email(f"Weekly Digest — Week {args.week or get_current_week()}", output)
        send_discord(output)
    elif args.command == "strategy":
        output = generate_weekly_strategy(args.week)
        print(output)
        send_email(f"Strategy Digest — Week {args.week or get_current_week()}", output)
        send_discord(output)

if __name__ == "__main__":
    main()