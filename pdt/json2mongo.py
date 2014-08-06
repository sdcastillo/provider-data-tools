#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4
# Alan Viars

from pymongo import Connection
import os, sys, string, json
from collections import OrderedDict

import functools
import pymongo
import time
import hashlib

MONGO_HOST="127.0.0.1"
MONGO_PORT=27017

def json2mongo(jsonfile, database_name         = "database1",
               collection_name                 = "collection1",
               delete_collection_before_import = False ):
    
    """Return a response_dict with a summary of json2mongo transaction."""
    print "Start the import of", jsonfile, "into the collection", collection_name, "within the database", database_name, "."

    response_dict = OrderedDict()
    fileindex = 0
    mongoindex = 0
    error_list =[]

    mconnection = Connection(MONGO_HOST, MONGO_PORT)
    db          = mconnection[database_name]
    collection  = db[collection_name]

    if delete_collection_before_import:
        print "Clearing the collection prior to import."
        myobjectid=collection.remove({})

    fh = open(jsonfile, 'rU')

    j = fh.read()
    
    try:
        j = json.loads(j)

        if type(j) != type({}):
            error_message = "File " + str(jsonfile) +  " did not contain a JSON object, i.e. {}."
            error_list.append(error_message)
    
    except:
        print jsonfile
        print "here"
        error_message = "File " + str(jsonfile) +  " did not contain valid JSON."
        error_list.append(error_message)
        

    if not error_list:
        
        myobjectid =  collection.insert(j)
        mongoindex += 1

        if error_list:
            response_dict['num_files_imported']=mongoindex
            response_dict['num_file_errors']=len(error_list)
            response_dict['errors']=error_list
            response_dict['code']=400
            response_dict['message']="Completed with errors."
  
        else:
            response_dict['num_rows_imported']=mongoindex
            response_dict['num_file_errors']=len(error_list)
            response_dict['code']=200
            response_dict['message']="Completed without errors."

  
    else:    
        response_dict['num_rows_imported']=mongoindex
        response_dict['num_file_errors']=len(error_list)
        response_dict['code']=500
        syserror = sys.exc_info()
        errors = error_list
        if syserror[0]:
            errors.append(str(sys.exc_info()))
        
        response_dict['errors']=errors
    

    return response_dict

if __name__ == "__main__":

    
    if len(sys.argv)!=5:
        print "Usage:"
        print "python json2mongo.py [JSONFILE] [DATABASE] [COLLECTION] [DELETE_COLLECTION_BEFORE_IMPORT (T/F)]"
        sys.exit(1)

    json_file                       = sys.argv[1]
    database                        = sys.argv[2]
    collection                      = sys.argv[3]
    delete_collection_before_import = sys.argv[4]

    if sys.argv[4].lower() in ('t', 'true', '1'):
        delete_collection_before_import = True
    else:
        delete_collection_before_import = False
    result = json2mongo(json_file, database, collection, delete_collection_before_import)
    
    
    print json.dumps(result, indent =4)
