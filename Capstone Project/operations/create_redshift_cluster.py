import configparser
import psycopg2
import sys
import boto3
import pandas as pd


def read_config_file():
    """Reads aws credentials from config file.
    """
    config = configparser.ConfigParser()
    config.read_file(open('./aws/credentials.cfg'))

    HOST = config.get("CLUSTER","HOST")
    CLUST_NAME = config.get("OTHER","CLUSTER_NAME")
    DB_NAME = config.get("CLUSTER","DB_NAME")
    DB_USER = config.get("CLUSTER","DB_USER")
    DB_PASS = config.get("CLUSTER","DB_PASSWORD")
    DB_PORT = config.get("CLUSTER","DB_PORT")
    ARN = config.get("IAM_ROLE","ARN")
    KEY = config.get("AWS","AWS_ACCESS_KEY_ID")
    SECRET = config.get("AWS","AWS_SECRET_ACCESS_KEY")
    
    return [HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT, CLUST_NAME, ARN, KEY, SECRET]


def redshift_client(key, secret):
    """Instantiate redshift client.    
    """
    redshift = boto3.client('redshift',
                            region_name = "us-west-2",
                            aws_access_key_id = key,
                            aws_secret_access_key = secret)
    return redshift


def ec2_resource(key, secret):
    """Instantiate EC2.
    """
    ec2 = boto3.resource('ec2',
                         region_name = "us-west-2",
                         aws_access_key_id = key,
                         aws_secret_access_key = secret)
    return ec2

def create_cluster():
    """Create redshift cluster.
    """
    cfg_lst = read_config_file()
    ec2 = ec2_resource(cfg_lst[7], cfg_lst[8])
    redshift = redshift_client(cfg_lst[7], cfg_lst[8])
    
    try:
        response = redshift.create_cluster(
            ClusterIdentifier = cfg_lst[5],
            ClusterType = "multi-node",
            NodeType = "dc2.large",
            NumberOfNodes = 3,
            DBName = cfg_lst[1],        
            MasterUsername = cfg_lst[2],
            MasterUserPassword = cfg_lst[3],
            IamRoles = [cfg_lst[6]]  
        )
    except Exception as e:
        print(e)
        
    myClusterProps = redshift.describe_clusters(ClusterIdentifier = cfg_lst[5])['Clusters'][0]
    
    try:
        vpc = ec2.Vpc(id = myClusterProps['VpcId'])
        defaultSg = list(vpc.security_groups.all())[0]
        defaultSg.authorize_ingress(
            GroupName = defaultSg.group_name,
            CidrIp = '0.0.0.0/0',
            IpProtocol = 'TCP',
            FromPort = int(cfg_lst[4]),
            ToPort = int(cfg_lst[4])
        )
    except Exception as e:
        print(e)    

def delete_cluster():
    """Delete redshift cluster.
    """
    cfg_lst = read_config_file()
    redshift = redshift_client(cfg_lst[7], cfg_lst[8])
    
    try:
        redshift.delete_cluster(ClusterIdentifier=cfg_lst[5], SkipFinalClusterSnapshot=True)
    except Exception as e:
        print(e)
        

def main():
    args = sys.argv[1:]
    
    if(len(args)== 1 and args[0]=='create'):
        create_cluster()
    elif(len(args)==1 and args[0]=='delete'):
        delete_cluster()
    else:
        print(f"Invalid argument: '{args[0]}'")
    

if __name__ == "__main__":
    main()