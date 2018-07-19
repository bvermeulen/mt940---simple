from tkinter import Tk, Text
import re


class Editor:
    '''  Class for editor to edit entries in Tkinter that can not be parsed
         automatically
         Methods:
         - edit
         - handle_input
         - display
         - parse
    '''
    TEXT1 = '         1         2         3         4         5'\
            '         6         7         8         9         0'\
            '         1         2         3         4         6\n'
    TEXT2 = '12345678901234567890123456789012345678901234567890'\
            '12345678901234567890123456789012345678901234567890'\
            '12345678901234567890123456789012345678901234567890\n'
    TEXT3 = 'GIF> '

    @classmethod
    def edit(cls, string86, bank_account, date, amount):
        '''  main method for the class creating a tkinter window for editing
             and outputs payee and memo.
        '''
#        pdb.set_trace()
        cls.string86 = string86 + '\n'
        cls.bank_account = 'Account: ' + bank_account + '\n'
        cls.date = 'Date: ' + date + '\n'
        cls.amount = 'Amount: ' + amount + '\n'
        cls.input_flag = True
        cls.exit_flag = False
        cls.payee = ''
        cls.memo = ''
        cls.string86_list = [cls.string86]
        cls.payee_list = [cls.payee]
        cls.memo_list = [cls.memo]

        root = Tk()
        cls.displaytext = Text(root, width=200)
        cls.displaytext.pack()
        cls.displaytext.bind("<Return>", cls.handle_input)

        while not cls.exit_flag:
            if cls.input_flag:
                cls.display()

            root.update()

        else:
            root.destroy()

        return cls.payee, cls.memo

    @classmethod
    def handle_input(cls, event):
        '''  method to handle input. Input is in the form:
             'q' - quit, 'u' - undo, 's' - skip, ''<start> <end> p' and
             ''<start> <end> m'
        '''
        text_input = cls.displaytext.get(10.4, 'end')
        text_input = text_input.strip()
        start, end, command = cls.parse(text_input)

        if end >= len(cls.string86):
            end = len(cls.string86)-1  # leave the /n !

        if command == 'q':
            cls.exit_flag = True

        elif command == 's':
            cls.exit_flag = True
            cls.payee = 'MANUAL'
            cls.memo = cls.string86_list[0]

        elif command == 'u':
            try:
                del cls.string86_list[-1]
                del cls.payee_list[-1]
                del cls.memo_list[-1]
                cls.string86 = cls.string86_list[-1]
                cls.payee = cls.payee_list[-1]
                cls.memo = cls.memo_list[-1]

            except Exception as e:
                print('cannot undo')

        elif (start < 0) or (end < start):
            print('invalid entry')

        elif command == 'p':
            if not cls.payee:
                cls.payee = cls.string86[start:end]
            else:
                cls.payee = cls.payee + ' - ' + cls.string86[start:end]

            cls.string86 = cls.string86.replace(cls.string86[start:end], '')
            cls.string86_list.append(cls.string86)
            cls.payee_list.append(cls.payee)
            cls.memo_list.append('')

        elif command == 'm':
            if not cls.memo:
                cls.memo = cls.string86[start:end]
            else:
                cls.memo = cls.memo + ' - ' + cls.string86[start:end]

            cls.string86 = cls.string86.replace(cls.string86[start:end], '')
            cls.string86_list.append(cls.string86)
            cls.memo_list.append(cls.memo)
            cls.payee_list.append('')

        cls.displaytext.delete(1.0, 'end')
        cls.input_flag = True

    @classmethod
    def display(cls):
        '''  method to display the text in the editing console
        '''
        cls.input_flag = False
        _payee = 'Payee: ' + cls.payee + '\n'
        _memo = 'Memo: ' + cls.memo + '\n'
        text = ''.join([cls.bank_account, cls.date, cls.amount,
                        _payee, _memo, '\n',
                        cls.TEXT1, cls.TEXT2, cls.string86, cls.TEXT3])
        cls.displaytext.insert(1.0, text)
        cls.displaytext.mark_set("insert", 10.4)

    @staticmethod
    def parse(text_input):
        '''  method to parse the input string
        '''
        start = -1
        end = -1
        command = ''
        if text_input in ['q', 'Q']:  # quit editing
            command = 'q'

        elif text_input in ['u', 'U']:  # undo entry
            command = 'u'

        elif text_input in ['s', 'S']:  # skip editing take original string86
            command = 's'

        else:
            _ = re.search(r'(\d{3}|\d{2}|\d).*?(?=\d)(\d{3}|\d{2}|\d).*(\D)',
                          text_input)

            try:
                start = int(_.group(1))-1
                end = int(_.group(2))
                command = _.group(3).lower()
                print(start, end, command)

            except Exception as e:
                print(e)

        return start, end, command
