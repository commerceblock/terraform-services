import click
import total_fee_income
import swiss_pay_invoice
import stats
import event_earnings

@click.command(name='total-fee-income' )
@click.option('--hours', default=24, help='Number of hours to aggregate data for. Defaults to 24.')
def execute_total_fee_income(hours):
    result = total_fee_income.execute(hours=hours)

    # Print the result
    for event_type, data in result.items():
        click.echo(f"Type: {event_type}, Credit (msat): {data['credit_msat']}, "
                f"Debit (msat): {data['debit_msat']}, Total (msat): {data['total']}")

@click.command(name='payment' )
@click.option('--hours', default=24, help='Number of hours of earnings to be paid. Default is 24.')
def payment(hours):
    result = swiss_pay_invoice.execute(hours=hours)
    print(result)

@click.command(name='stats' )
@click.option('--hours', default=24, help='Number of hours of stats. Default is 24.')
def execute_stats(hours):
    result = stats.execute(hours=hours)
    print(result)

@click.command(name='event-earnings' )
@click.option('--hours', default=24, help='Number of hours of events. Default is 24.')
def execute_event_earnings(hours):
    result = event_earnings.execute(hours=hours)
    print(result)

@click.group()
def cli():
    pass

cli.add_command(execute_total_fee_income)
cli.add_command(payment)
cli.add_command(execute_stats)
cli.add_command(execute_event_earnings)

# Define rune as a global variable
rune = ""

def ask_for_rune():
    global rune
    rune_value = input("Please enter the rune value: ")
    rune= rune_value

if __name__ == "__main__":
    ask_for_rune()
    cli()
