#code taken from: https://github.com/andialbrecht/sqlparse/blob/master/examples/extract_table_names.py

import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML
    
def is_subselect(parsed):
    if not parsed.is_group():
        return False
    for item in parsed.tokens:
        if item.ttype is DML and item.value.upper() == 'SELECT':
            return True
    return False

def extract_from_part(parsed):
    from_seen = False
    for item in parsed.tokens:
        if from_seen:
            if is_subselect(item):
                for x in extract_from_part(item):
                    yield x
            else:
                yield item
        elif item.ttype is Keyword and item.value.upper() == 'FROM':
            from_seen = True


def extract_table_identifiers(token_stream):
    for item in token_stream:
        if isinstance(item, IdentifierList):
            for identifier in item.get_identifiers():
                yield str(identifier.get_name())
        elif isinstance(item, Identifier):
            yield str(item.get_name())
        # It's a bug to check for Keyword here, but in the example
        # above some tables names are identified as keywords...
        #elif item.ttype is Keyword:
        #    yield str(item.value)

def extract_all_keywords(token_stream):
    for item in token_stream:
        if item.ttype is Keyword:
            yield str(item.value.upper())
        elif item.ttype is DML:
            yield str(item.value.upper())
            
def extract_keywords(sql):
    toks = sqlparse.parse(sql)[0]
    return list(extract_all_keywords(toks.tokens))
    
def extract_tables(sql):
    stream = extract_from_part(sqlparse.parse(sql)[0])
    return list(extract_table_identifiers(stream))