#!/usr/bin/env python

from cm_api.api_client import ApiResource
from cm_api.endpoints.types import *
import argparse
import os
import sys
from collections import namedtuple


def retrieve_args():
    """
    Attempts to retrieve Cloudera Manager connection information from the environment.
    If that fails, the information is parsed from the command line.
    @rtype:  namespace
    @return: The parsed arguments.
    """

    if all(env_var in os.environ for env_var in ("DEPLOYMENT_HOST_PORT",
                                                 "CM_USERNAME", "CM_PASSWORD",
                                                 "CLUSTER_NAME")):
        sys.stdout.write("Arguments detected in environment -- command line arguments being ignored.\n")
        args = namedtuple("args", ["host", "port", "username", "password", "cluster", "use_tls"])

        parsed_url = os.environ["DEPLOYMENT_HOST_PORT"].split(":")
        args.host = parsed_url[0]
        args.port = int(parsed_url[1])
        args.username = os.environ["CM_USERNAME"]
        args.password = os.environ["CM_PASSWORD"]
        args.cluster = os.environ["CLUSTER_NAME"]
        args.use_tls = False

        return args
    else:
        return parse_args()


def parse_args():
    """
    Parses host and cluster information from the given command line arguments.
    @rtype:  namespace
    @return: The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Creating peer for BDR",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--host', metavar='HOST', type=str, help="The Cloudera Manager host")
    # parser.add_argument('cluster', metavar='CLUSTER', type=str, help="The name of the target cluster")
    parser.add_argument('--port', metavar='port', type=int, default=7180, help="Cloudera Manager's port.")
    parser.add_argument('--username', metavar='USERNAME', type=str, default='admin',
                        help="The username to log into Cloudera Manager with.")
    parser.add_argument('--password', metavar='PASSWORD', type=str, default='admin',
                        help="The password to log into Cloudera Manager with.")
    parser.add_argument('--use-tls', action='store_true', help="Whether to use TLS to connect to Cloudera Manager.")
    parser.add_argument('--source_cm_url', metavar='SOURCE_CM_URL', type=str, help="full CM URL of the source cluster")
    parser.add_argument("--source-user", metavar='SOURCE_CM_USER', type=str, default='admin',
                        help="The username to log into Source Cloudera Manager with." )
    parser.add_argument("--source-password", metavar='SOURCE_CM_PWD', type=str, default='admin',
                        help="The password to log into Source Cloudera Manager with." )
    parser.add_argument("--peer-name" , metavar='PEER_NAME', type=str, default='peer1',
                        help="ALias Name to be created of the Source cluster" )
    return parser.parse_args()


def printusagemessage():
    print ("Usage: python add_peer.py")
    print ("Example that lists queries that have run more than 10 minutes:")
    print ("python add_peer.py --host 18.205.59.216 --port 7180 --username admin --password admin "
           "--source_cm_url http://34.226.244.149:7180/ --source-user admin --source-password admin --peer-name peer2")
    print ("Example that creates peer with name peer2")



def main():
    """
    Add peer to the cluster.
    @rtype:   number
    @returns: A number representing the status of success.
    """
    settings = retrieve_args()
    if len(sys.argv) == 1 or len(sys.argv) > 8:
        printusagemessage()
    quit(1)

    # TARGET_CM_HOST = "18.205.59.216"
    # SOURCE_CM_URL = "http://34.226.244.149:7180/"


    api_target = ApiResource(settings.host, settings.port, settings.username,
                      settings.password, settings.use_tls, 14)

    # api_root = ApiResource(TARGET_CM_HOST, username="admin", password="admin")
    cm = api_target.get_cloudera_manager()
    cm.create_peer(settings.peer_name, settings.source_cm_url, settings.source_user, settings.source_password)

    return 0

if __name__ == '__main__':
    sys.exit(main())



