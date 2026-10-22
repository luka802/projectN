from travel_buddy.bot import TravelBuddy


def main():
    bot = TravelBuddy()
    print(bot.start())
    while not bot.closed:
        try:
            text = input('\nYou: ')
        except (EOFError, KeyboardInterrupt):
            text = 'exit'
            print()
        print('\nTravelBuddy:', bot.reply(text))


if __name__ == '__main__':
    main()
