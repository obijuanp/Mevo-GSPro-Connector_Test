from src.non_blocking_input import NonBlockingInput
from src.ui import Color, UI

class Menu:
    def __init__(self):
        self.menu_options = {
            'M': 'Display Menu',
            'R': 'Reset ROI',
            'S': 'Restart Connector',
            'G': 'Reset GSPro Connection',
            'D': 'Toggle Debug Log',
            'Q': 'Exit',
        }

    def display(self):
        for key in self.menu_options.keys():
            print(key, '--', self.menu_options[key])

    def process(self, option, process_manager):
        soptions = ', '.join(map(str, list(self.menu_options.keys())))
        if option == 'M':
            self.display()
        elif option == 'S':
            process_manager.restart()
        elif option == 'R':
            i=1
            #try:
            #    obtain_rois(True)
            #except Exception as e:
            #    print_colored_prefix(Color.RED, "Image Processing ||", "An error occurred: {}".format(e))
        else:
            UI.display_message(Color.RED, "", f"Invalid option. Please enter a valid option: {soptions}, press M top display menu")
