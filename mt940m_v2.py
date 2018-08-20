# modules for MT940 ABN-AMRO
import re
from mt940e_v2 import Editor
import pdb # noqa F401

# decode MT940 86 strings and deducts payee and memo
# for MT940 ABN-AMRO output


class ParseMT940:

    cutoff = 65

    @classmethod
    def code86(cls, string86, bank_account, date, amount):
        '''  determine the code in line 86 on how to handle it. The first
             5 characters are taken as the code
        '''
        _search = re.search('^.{5}', string86)
        code = _search.group()

        # modify string86 so it will handle '/' in text correctly
        string86 = re.sub(r"(/\D{3}/|/\D{4}/)", r"/\1", string86)

        if code == '':
            assert False, "something not right there should alwats be a code"

        elif code == '/TRTP':
            _search = re.search('//IBAN/(.*?(?=//))', string86)
            if _search:
                payee = _search.group(1) + ' - '

            _search = re.search('//NAME/(.*?(?=//))', string86)
            if _search:
                payee = payee + _search.group(1)

            string86 = re.sub(r"(/\D{3}/|/\D{4}/)", r"/\1", string86)
            _search = re.search('//REMI/(.*?(?=//))', string86)

            if _search:
                memo = _search.group(1)

            if memo.isdigit():
                _search = re.search('//REMI/.*?(?=/)/(.*?(?=//))', string86)

                if _search:
                    memo = memo + '/' + _search.group(1)

        elif code == 'SEPA ':
            _search = re.search('IBAN:(.*?(?=BIC:))', string86)

            if _search:
                payee = _search.group(1).strip() + ' - '
                _search = re.search('NAAM:(.*?(?=OMSCHRIJVING:))', string86)

                if _search:
                    payee = payee + _search.group(1).strip()

            _search = re.search('OMSCHRIJVING:(.*$)', string86)

            if _search:
                memo = (_search.group(1)).strip()

        elif code == 'BEA  ':
            payee = 'PIN: '
            _search = re.search(r'(\d\d.\d\d\.\d\d/\d\d.\d\d\s.*$)', string86)

            if _search:
                memo = _search.group(1)

                _search = re.search(r'\d\d.\d\d\.\d\d/\d\d.\d\d\s(.*?(?=,))',
                                    memo).group(1)
                if _search:
                    payee = payee + _search

        elif code == 'GEA  ':
            payee = 'ATM: '
            _search = re.search(r'(\d\d.\d\d\.\d\d/\d\d.\d\d\s.*$)', string86)

            if _search:
                memo = _search.group(1)

                _search = re.search(r'\d\d.\d\d\.\d\d/\d\d.\d\d\s(.*?(?=,))',
                                    memo).group(1)
                payee = payee + _search

        # where code is not defined call an editor program to
        # manually parse it
        else:
            string86 = re.sub(' +', ' ', string86)
            payee, memo = Editor.edit(string86, bank_account, date, amount)
            cls.cutoff = 200

        memo = re.sub('\s+', ' ', memo.strip())[:cls.cutoff]
        return payee, memo

    @staticmethod
    def conv_amount_str(creditsign, amount_str):
        '''   converts amount and output amount in str value
        '''
        amount = amount_str.replace(',', '.')

        if creditsign == 'D':
            sign = '-'
        else:
            sign = ''

        amount = '{0}{1}'.format(sign, amount)

        if amount.endswith('.'):
            amount = amount + '00'

        return amount

    @staticmethod
    def transaction_date_conversion(v_date, t_date):
        '''  converts the date and checks if v_d and t_d are in the same year
             input: v_date: yymmdd, t_date: mmdd
             output: date ddmmyyyy
        '''
        date = ''
        year = int(v_date[0:2])+2000  # this century only

        # check if valuta date is December and transaction date is January
        # add a year in that case
        if (v_date[2:4] == '12') and (t_date[0:2] == '01'):
            year = year+1

        date = t_date[2:4]+'/'+t_date[0:2]+'/'+str(year)

        return date

    @staticmethod
    def write_qif_record(qf, date, amount, payee, memo):
        '''  output to file with the qif format
             - D<date>
             - T<amount>
             - P<payee>
             - M<memo>
             -   ^
        '''
        qf.write('D%s\n' % date)
        qf.write('T%s\n' % amount)
        qf.write('P%s\n' % payee)
        qf.write('M%s\n' % memo)
        qf.write('^\n')
