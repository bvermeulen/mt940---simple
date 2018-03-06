#!/usr/bin/env python
import re
import sys
import mt940m_p36

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
total_amount = 0
bank_account = ''
fn = ''

# record: pattern to determine a MT940 record group, note more than one transaction
# is possible within a record
record_pat = re.compile('(?P<record>:\d\d.??:.*?(?=-ABN))')

# field_pat: pattern to seperate the fields in the MT940 file :num :field
field_pat = re.compile(':(?P<num>\d\d.??):(?P<field>.*?(?=:\d\d.??:))')

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
            if field != bank_account and bank_account != '':
                # close the qif file if this is not the first instance
                qif_file.close()
                print ('{}: the total sum of transfers is {:.2f}'.format(fn, total_amount))
                total_amount = 0
                fn = ''

            if field != bank_account:
                # open a new qif file if a new bank account is encountered
                bank_account = field
                fn = argf.rsplit('.',1)[0] # make the file name the same as the 1st argument + some changes
                fn =  fn + '_' + bank_account +'.qif'
                qif_file = open(fn,'w')
                qif_file.write('!Type:Bank\n')
                
        # in case field number is '61' handle the transaction using the information in field 61 and subsequent 86
        if num == '61':
            m = re.match(val61_pat, field)
            m_dict = m.groupdict()

        if num == '86':
            payee, memo = mt940m_p36.code86(field)

            transaction_date = m_dict['date']
            valuta_date = m_dict['valuta']
            amount = m_dict['amount']
            amount = amount.replace(',', '.')
            if m_dict['sign'] == 'D':
                sign = '-'
            else:
                sign = ''
     
            amount = '{0}{1}'.format(sign, amount)
            if amount.endswith('.'):
                amount = amount +'00'

            total_amount = total_amount + float(amount)
            date = mt940m_p36.transaction_date_conversion(valuta_date, transaction_date)

#           print ('{0}, {1}, {2}, {3}'.format(date, amount, payee, memo))
            mt940m_p36.write_qif_record (qif_file, date, amount, payee, memo)

# on finishing the program close the last qif_file
if fn !='':
    qif_file.close()
    print ('{}: the total sum of transfers is {:.2f}'.format(fn, total_amount))
else:
    print('this is not a valid MT940 file')
