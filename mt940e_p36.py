from tkinter import Tk, Label, Frame, Entry
import re
import pdb # noqa F401

PADDING = 7
WIDTH = 230
FONT = ('courier', 10)
HELP_TEXT = '       s - skip, <start> <end> m - memo, '\
            '<start> <end> p - payee, u - undo, q - quit, enter'
TEXT1 = '0                                                 '\
        '                                                 1'\
        '                                                  '\
        '                                                 2\n'

TEXT2 = '0        1         2         3         4         5'\
        '         6         7         8         9         0'\
        '         1         2         3         4         5'\
        '         6         7         8         9         0\n'
TEXT3 = '12345678901234567890123456789012345678901234567890'\
        '12345678901234567890123456789012345678901234567890'\
        '12345678901234567890123456789012345678901234567890'\
        '12345678901234567890123456789012345678901234567890\n'


class Editor:
    '''  Class for editor to edit entries in Tkinter that can not be parsed
         automatically
         Methods:
         - edit
         - handle_input
         - display
         - parse
    '''
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
        root.title('QIF Editor')
        cls.info_frame = Frame(root,
                               relief='ridge',
                               highlightbackground='black',
                               highlightcolor='black',
                               highlightthickness=2,
                               bg='white')

        cls.str86_frame = Frame(root,
                                relief='ridge',
                                highlightbackground='black',
                                highlightcolor='black',
                                highlightthickness=2,
                                bg='white')

        cls.input_frame = Frame(root,
                                relief='ridge',
                                highlightbackground='black',
                                highlightcolor='black',
                                highlightthickness=2,
                                bg='white')

        cls.info_frame.pack(anchor='w', padx=PADDING, pady=PADDING)
        cls.str86_frame.pack(anchor='w', padx=PADDING, pady=PADDING)
        cls.input_frame.pack(anchor='w', padx=PADDING, pady=PADDING)
        cls.l_info = Label(cls.info_frame)
        cls.l_str86 = Label(cls.str86_frame)
        cls.l_info.pack()
        cls.l_str86.pack()

        Label(cls.input_frame, text='>>').pack(side='left')
        cls.command = Entry(cls.input_frame, width=10)
        cls.command.pack(side='left')
        Label(cls.input_frame, text=HELP_TEXT).pack(side='left')
        cls.command.bind("<Return>", cls.handle_input)

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
        text_input = cls.command.get()
        text_input = text_input.strip()
        start, end, instruction = cls.parse(text_input)

        if instruction == 'q':
            cls.exit_flag = True

        elif instruction == 's':
            cls.exit_flag = True
            cls.payee = 'MANUAL'
            cls.memo = cls.string86_list[0]

        elif instruction == 'u':
            assert len(cls.payee_list) == len(cls.memo_list), 'check this out'

            if len(cls.payee_list) > 1:
                del cls.string86_list[-1]
                del cls.payee_list[-1]
                del cls.memo_list[-1]
                cls.string86 = cls.string86_list[-1]
                cls.payee = cls.payee_list[-1]
                cls.memo = cls.memo_list[-1]

            else:
                print('cannot undo')

        elif (start < 0) or (end < start):
            print('invalid entry')

        elif instruction == 'p':
            if not cls.payee:
                cls.payee = cls.string86[start:end]
            else:
                cls.payee = cls.payee + ' - ' + cls.string86[start:end]

            cls.payee = cls.payee.replace('\n', '')
            cls.string86 = cls.string86.replace(cls.string86[start:end], '')
            cls.string86_list.append(cls.string86)
            cls.payee_list.append(cls.payee)
            cls.memo_list.append(cls.memo)

        elif instruction == 'm':
            if not cls.memo:
                cls.memo = cls.string86[start:end]
            else:
                cls.memo = cls.memo + ' - ' + cls.string86[start:end]

            cls.memo = cls.memo.replace('\n', '')
            cls.string86 = cls.string86.replace(cls.string86[start:end], '')
            cls.string86_list.append(cls.string86)
            cls.memo_list.append(cls.memo)
            cls.payee_list.append(cls.payee)

        cls.command.delete(0, 'end')
        cls.input_flag = True

    @classmethod
    def display(cls):
        '''  method to display the text in the editing console
        '''
        cls.input_flag = False
        _payee = 'Payee: ' + cls.payee + '\n'
        _memo = 'Memo: ' + cls.memo + '\n'
        info_text = ''.join([cls.bank_account, cls.date, cls.amount,
                            _payee, _memo])
        str86_text = ''.join([TEXT1, TEXT2, TEXT3, cls.string86])
        cls.l_info.forget()
        cls.l_str86.forget()
        cls.l_info = Label(cls.info_frame, text=info_text, width=WIDTH,
                           font=FONT, anchor='w', justify='left')
        cls.l_str86 = Label(cls.str86_frame, text=str86_text, width=WIDTH,
                            font=FONT, anchor='w', justify='left')
        cls.l_info.pack()
        cls.l_str86.pack()

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
