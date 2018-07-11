# modules for MT940 ABN-AMRO
import re
from mt940e_p36 import Editor
import pdb

# decode MT940 86 strings and deducts payee and memo
# for MT940 ABN-AMRO output

def code86(string86, bank_account, date, amount):
    p=''
    m=''
    # determine the code in line 86 on how to handle it
    search_string = re.search('^.{5}',string86)
    code = search_string.group()

    # modify string86 so it will handle '/' in text correctly
    string86 = re.sub(r"(/\D{3}/|/\D{4}/)",r"/\1",string86)

    cutoff = 65
    if code == '':
        print ('No code')

    # for TRTP [bank transfer] handle as follows:
    # find payee - first IBAN number and then NAME
    elif code == '/TRTP':
        search_string = re.search('//IBAN/(.*?(?=//))', string86)
        if search_string != None:
            p = search_string.group(1) +' - '
            search_string = re.search('//NAME/(.*?(?=//))', string86)
            if search_string != None:
                p = p+search_string.group(1)

        # find memo - field after REMI and if this is only a number then add the next field
        string86 = re.sub(r"(/\D{3}/|/\D{4}/)",r"/\1",string86)
        search_string = re.search('//REMI/(.*?(?=//))', string86)

        if search_string != None:
            m = search_string.group(1)

        if m.isdigit():
            search_string = re.search('//REMI/.*?(?=/)/(.*?(?=//))', string86)
            if search_string != None:
                m = m +'/'+search_string.group(1)

    # for SEPA [bank transfer] handle as follows:
    # find payee account number 'IBAN:', then name 'NAAM:' and description
    # 'OMSCHRIJVING:'
    elif code == 'SEPA ':
        search_string = re.search('IBAN:(.*?(?=BIC:))', string86)
        if search_string != None:
            p = search_string.group(1).strip() + ' - '
            search_string = re.search('NAAM:(.*?(?=OMSCHRIJVING:))', string86)
            if search_string != None:
                p = p + search_string.group(1).strip()

        #find memo - field after OMSCHRIJVING:
        search_string = re.search('OMSCHRIJVING:(.*$)', string86)
        if search_string != None:
            m = (search_string.group(1)).strip()

    # for BEA [use of card pin code] handle as follows:
    # find payee and set memo
    elif code == 'BEA  ':
        p = 'PIN: '
        search_string = re.search(r'(\d\d.\d\d\.\d\d/\d\d.\d\d\s.*$)', string86)
        if search_string != None:
            m = search_string.group(1)
            p = p + re.search(r'\d\d.\d\d\.\d\d/\d\d.\d\d\s(.*?(?=,))', m).group(1)

    # for GEA [use of ATM] handle as follows:
    # find ATM machine as payee and set memo
    elif code == 'GEA  ':
        p = 'ATM: '
        search_string = re.search(r'(\d\d.\d\d\.\d\d/\d\d.\d\d\s.*$)', string86)
        if search_string != None:
            m = search_string.group(1)
            p = p + re.search(r'\d\d.\d\d\.\d\d/\d\d.\d\d\s(.*?(?=,))', m).group(1)

    # where code is not defined just take whole 86 string (stripped from any whitespaces)
    # as memo and set payee to ABN-AMRO
    else:
        string86 = re.sub(' +', ' ', string86)
        p, m = Editor.edit(string86, bank_account, date, amount)
        cutoff = 200

    m = re.sub('\s+',' ',m.strip())[:cutoff]  # allow m only to be 65 characters long
    return p,m

# convert amount string in proper format and output as string
def conv_amount_str(creditsign, amount_str):
    amount = amount_str.replace(',', '.')
    if creditsign == 'D':
        sign = '-'
    else:
        sign = ''

    amount = '{0}{1}'.format(sign, amount)
    if amount.endswith('.'):
        amount = amount +'00'
#   print('amount: ', amount)
    return amount

# convert transaction date in the format <dd/mm/yyyy>
# MT940 defines transaction date as <mmdd> and valuta date as <yymmdd>
# check is made correct year is added to transaction date and it is assumed all transactions are in the current century
def transaction_date_conversion(v_d,t_d):
    date = ''
    year = int(v_d[0:2])+2000 # this century only

    # check month to see valuta date and transaction date are in the same year
    if int(v_d[2:4]) > int(t_d[0:2]):
        year = year+1

    # convert to <dd/mm/yyyy> format
    date = t_d[2:4]+'/'+t_d[0:2]+'/'+str(year)

    return date

def write_qif_record(qf, date, amount, payee, memo):
# write the date, amount, payee and memo in qif format:
#   D<date>
#   T<amount>
#   P<payee>
#   M<memo>
#   ^
#
    qf.write('D%s\n' % date)
    qf.write('T%s\n' % amount)
    qf.write('P%s\n' % payee)
    qf.write('M%s\n' % memo)
    qf.write('^\n')

    return
