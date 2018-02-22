#!/usr/bin/env python
import re
import sys
import mt940m

# read and concatenate entire MT940 contents and add '-ABN' to make sure the last record is captured
text = open(sys.argv[1]).read().splitlines()
text = ''.join(text) +'-ABN'


# make the qif file name with extension qif
# based on file given in the argument
fn = sys.argv[1].rsplit('.',1)[0]+'.qif'
qif_file = open(fn, 'w')
qif_file.write('!Type:Bank\n')

payee = ''
memo = ''
total_amount = 0

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
	
	# each time a field 61 is encountered it will record the transaction with the details
	# from the subsequent field 86
	for match in re.finditer(field_pat,record):
		num = match.group('num')
        	field = match.group('field')
	
		if num == '61':
			m = re.match(val61_pat, field)
        		m_dict = m.groupdict()

		if num == '86':
			payee, memo = mt940m.code86(field)
	
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
        	   	date = mt940m.transaction_date_conversion(valuta_date, transaction_date)

	           	print('{0}, {1}, {2}, {3}'.format(date, amount, payee, memo))
			mt940m.write_qif_record (qif_file, date, amount, payee, memo)

print ('The total sum of transfers is {}'.format(total_amount))
qif_file.close()
