# mt940---simple
>Read MT940 records (ABNAMRO) and then convert them to QIF

## MT940 -- ABNAMRO 

Converter from SWIFT format MT940 (ABNAMRO) to simple Quicken QIF format.

From the bank download the MT940 format (<filename>.sta). From this file each field 61
is taken as a transaction and combined with the 86 field to yield:
date <dd/mm/yyyy>, amount, payee, memo and then written to a QIF file <filename>.qif.

There is no error capturing in the program and more written as proof of concept and finger 
exercise learning python, after almost 30 years of not coding!

Thanks to Mark Halder to give me a starting point!

## Usage python 3.6

convert STA file::

```sh
    python3 mt940_p36.py <filename>
```

output: <STA file>_<bank_account>.qit [a seperate qif file for each bank account]

## Usage python 2.7 (to be updated)

convert STA file::
```sh
    python mt940.py <filename>
``` 
output: <STA file>.qif

