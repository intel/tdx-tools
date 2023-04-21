#!/usr/bin/env python

'''
Enrolling keys and variables into OVMF
'''

import argparse
import logging
from ovmfkeyenroll.var_enroll import var_enroll, VarEnrollOps

# pylint: disable=redefined-builtin

LOG = logging.getLogger(__name__)

class VarEnrollParams:
    '''
    VarEnroll related params
    '''
    def __init__(self, info=None, input=None, operation=None, name=None, guid=None, attributes=None,
                 data_file=None, output=None):
        self.info = info
        self.input = input
        self.operation = operation
        self.name = name
        self.guid = guid
        self.attributes = attributes
        self.data_file = data_file
        self.output = output

if __name__ == '__main__':
    LOG.info("Enroll variables into OVMF")

    parser = argparse.ArgumentParser(
        description="The utility to enroll variables into OVMF")

    # add arguments
    parser.add_argument('-i', type=str, default="OVMF.fd",
                        help='input OVMF file', dest='input')
    parser.add_argument('-o', type=str, default="OVMF_FDE.fd",
                        help='output OVMF file', dest='out')
    parser.add_argument('-n', type=str, default=None,
                        help='name of variable', dest='name')
    parser.add_argument('-g', type=str, default=None,
                        help='GUID of variable', dest='guid')
    parser.add_argument('-d', type=str, default=None,
                        help='value of variable', dest='data')
    # parse arguments
    args = parser.parse_args()

    # check arguments
    if args.name is not None and args.guid is not None and args.data is not None:
        params  = VarEnrollParams(input=args.input, output=args.out, data_file=args.data,
                                  guid=args.guid, name=args.name, attributes='7',
                                  operation=VarEnrollOps.ADD)
        if var_enroll(params):
            LOG.info("Variable enrolled successfully")
        else:
            LOG.error("Variable enrolled failed")
