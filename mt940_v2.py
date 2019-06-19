#!/usr/bin/env python
import re
import sys
import decimal
from mt940m_v2 import ParseMT940

D = decimal.Decimal

# read and concatenate entire MT940 contents and add '-ABN' to make sure the last record is captured
if len(sys.argv)== 2:
    argf = sys.argv[1]
else:
    print('please provide a valid MT940 file')
    exit()

text = open(argf).read().splitlines()
text = ''.join(text) +'-ABN'

payee = ''
memo = ''
total_amount = D('0')
bank_account = ''
fn = ''

# record: pattern to determine a MT940 record group, note more than one transaction
# is possible within a record
record_pat = re.compile('(?P<record>:\d\d.??:.*?(?=-ABN))')

# field_pat: pattern to seperate the fields in the MT940 file :num :field
field_pat = re.compile(':(?P<num>\d\d).??:(?P<field>.*?(?=:\d\d.??:))')

# val61_pat: pattern to seperate the values in field 61
#:valuta (date) :date (transaction date and used for date) :sign :amount :code :reference
val61_pat = re.compile('(?P<valuta>\d{6})(?P<date>\d{4})(?P<sign>\D)'
                       '(?P<amount>\d+[,.]\d*)(?P<code>\w{4})(?P<reference>\w+$)')

for match in re.finditer(record_pat, text):
    # add token ':99:' to the end of the record to make sure the last field is also captured
    record = match.group('record') +':99:'

    # parse the string in a field number 'num' and its corresponding 'field'
    for match in re.finditer(field_pat,record):
        num = match.group('num')
        field = match.group('field')

        # in case field number is equal to '25' check if it is a new bank_account. If new make new qif file using
        # the name of the bank account found in field '25'. Field 25 is assumed to be before field 61.
        if num == '25':
            # close the qif file if this is not the first instance
            if field != bank_account and bank_account != '':
                qif_file.close()
                end_balance = start_balance + total_amount
                print ('{}: start balance: {:.2f} / transfers: {:.2f} / end balance: {:.2f}'  \
                       .format(fn, start_balance, total_amount, end_balance))
                total_amount  = D('0')
                fn = ''

            # open a new qif file if a new bank account is encountered
            if field != bank_account:
                bank_account = field
                new_bank_flag = True
                fn = argf.rsplit('.',1)[0] # make the file name the same as the 1st argument + some changes
                fn =  fn + '_' + bank_account +'.qif'
                qif_file = open(fn,'w')
                qif_file.write('!Type:Bank\n')

        #find the start_balance for a new bank account in field 60
        if num == '60' and new_bank_flag:
            m=re.search(r'(\D)\d{6}.*?(?=[\d])(.*$)',field)
            start_balance=D(ParseMT940.conv_amount_str(m.group(1),m.group(2)))
            new_bank_flag = False

        # in case field number is '61' handle the transaction using the information in field 61 and subsequent 86
        if num == '61':
            f61 = re.match(val61_pat, field)
            f61_dict = f61.groupdict()

        # in case field number is '86' handle to payee and memo and write the transaction to QIF
        if num == '86':
            date = ParseMT940.transaction_date_conversion(f61_dict['valuta'], f61_dict['date'])
            amount = ParseMT940.conv_amount_str(f61_dict['sign'], f61_dict['amount'])
            payee, memo = ParseMT940.code86(field, bank_account, date, amount)
            total_amount += D(amount)
            ParseMT940.write_qif_record (qif_file, date, amount, payee, memo)

# on finishing the program close the last qif_file
if fn !='':
    qif_file.close()
    end_balance = start_balance + total_amount
    print ('{}: start balance: {:.2f} / transfers: {:.2f} / end balance: {:.2f}'.format(fn, start_balance, total_amount, end_balance))
else:
    print('this is not a valid MT940 file')
