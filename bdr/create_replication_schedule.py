#!/usr/bin/env python
"""This script creates HDFS replication schedule."""

import argparse
import sys
from cm_api.api_client import ApiResource
from cm_api.endpoints.types import *

def parse_args():
    """
    Parses host and cluster information from the given command line arguments.
    @rtype:  namespace
    @return: The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Creating the REPLICATION Schedule",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-s', '--server', metavar='HOST', type=str,
                        help="The Cloudera Manager host")
    parser.add_argument('-p', '--port', metavar='port', type=int, default=7180,
                        help="Cloudera Manager's port.")
    parser.add_argument('-u', '--username', metavar='USERNAME', type=str, default='admin',
                        help="The username to log into Cloudera Manager with.")
    parser.add_argument('-pwd', '--password', metavar='PASSWORD', type=str, default='admin',
                        help="The password to log into Cloudera Manager with.")
    parser.add_argument('--use-tls', action='store_true',
                        help="Whether to use TLS to connect to Cloudera Manager.")
    parser.add_argument('--source-server', metavar='Source Cloudera Manager URL', type=str,
                        help="The Cloudera Manager host")
    parser.add_argument('--source-port', metavar='Source port', type=int, default=7180,
                        help="Cloudera Manager's port.")
    parser.add_argument("--source-user", metavar='Source Cloudera Manager Username',
                        type=str, default='admin',
                        help="The username to log into Source Cloudera Manager with.")
    parser.add_argument("--source-password", metavar='SOURCE_CM_PWD',
                        type=str, default='admin',
                        help="The password to log into Source Cloudera Manager with.")
    parser.add_argument('--s-use-tls', action='store_true',
                        help="Whether to use TLS to connect to Cloudera Manager.")
    parser.add_argument("--peer-name", metavar='PEER_NAME',
                        type=str, default='peer1',
                        help="ALias Name to be created of the Source cluster")
    parser.add_argument('-sp', '--source-path', metavar='SOURCE PATH')
    parser.add_argument('-tp', '--target-path', metavar='DESTINATION PATH')
    parser.add_argument('--source-cluster-name', metavar='Source Cluster Name')
    parser.add_argument('--target-cluster-name', metavar='Destination Cluster Name')

    return parser.parse_args()

def print_usage_message():
    ''' Print usage instructions
    '''
    print "usage: create_replication_schedule.py [-h] [-s HOST] [-p port] [-u USERNAME] \
          [-pwd PASSWORD] [--use-tls] \
          [--source-server Source Cloudera Manager URL] \
          [--source-port Source port] \
          [--source-user Source Cloudera Manager Username] \
          [--source-password SOURCE_CM_PWD] \
          [--s-use-tls] [--peer-name PEER_NAME] \
          [-sp SOURCE PATH] [-tp DESTINATION PATH] \
          [--source-cluster-name Source Cluster Name] \
          [--target-cluster-name Destination Cluster Name]"



def get_service_name(service_type, cluster_api, cluster_name):
    """
    Inputs: Common name of the Service,cluster APiResource and cluster name
    :return: Service name , returns "None" if service is not present
    """
    cluster = cluster_api.get_cluster(cluster_name)
    services = cluster.get_all_services()
    for service_name in services:
        if service_type in service_name.name:
            return service_name.name
    return None



def main():
    """
    Add peer to the cluster.
    @rtype:   number
    @returns: A number representing the status of success.
    """
    settings = parse_args()
    if len(sys.argv) == 1 or len(sys.argv) > 17:
        print_usage_message()
        quit(1)

    api_target = ApiResource(settings.server,
                             settings.port,
                             settings.username,
                             settings.password,
                             settings.use_tls,
                             14)
    api_source = ApiResource(settings.source_server,
                             settings.source_port,
                             settings.source_user,
                             settings.source_password,
                             settings.s_use_tls,
                             14)

    source_hdfs_name = get_service_name('HDFS', api_source, settings.source_cluster_name)
    target_yarn_service = get_service_name('YARN', api_target, settings.target_cluster_name)
    target_hdfs_name = get_service_name('HDFS', api_target, settings.target_cluster_name)

    hdfs = api_target.get_cluster(settings.target_cluster_name).get_service(target_hdfs_name)

    hdfs_args = ApiHdfsReplicationArguments(None)
    hdfs_args.sourceService = ApiServiceRef(None, peerName=settings.peer_name,
                                            clusterName=settings.source_cluster_name,
                                            serviceName=source_hdfs_name)
    hdfs_args.sourcePath = settings.source_path
    hdfs_args.destinationPath = settings.target_path
    hdfs_args.mapreduceServiceName = target_yarn_service

    # creating a schedule with daily frequency
    start = datetime.datetime.now()
    # The time at which the scheduled activity is triggered for the first time.
    end = start + datetime.timedelta(days=365)
    # The time after which the scheduled activity will no longer be triggered.

    schedule = hdfs.create_replication_schedule(start, end, "DAY", 1, True, hdfs_args)

    ## Updating the Schedule's properties
    schedule.hdfsArguments.removeMissingFiles = False
    schedule.alertOnFail = True
    schedule = hdfs.update_replication_schedule(schedule.id, schedule)

    print "Schedule created with Schdule ID: " + str(schedule.id)
    # print schedule.alertOnFail
    # print schedule.hdfsArguments.removeMissingFiles
    # print schedule.hdfsArguments.sourcePath
    # print schedule.hdfsArguments.preserveXAttrs
    # print schedule.hdfsArguments.exclusionFilters
    # print schedule.hdfsArguments.replicationStrategy
    # print schedule.hdfsArguments.numMaps
    # print schedule.hdfsArguments.userName
    # print schedule.hdfsArguments.schedulerPoolName
    # print type(schedule)


    return 0

if __name__ == '__main__':
    sys.exit(main())
